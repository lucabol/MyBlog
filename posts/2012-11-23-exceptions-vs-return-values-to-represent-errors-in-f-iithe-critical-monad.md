---
id: 104
title: 'Exceptions vs. Return Values to represent errors (in F#) – II– An example problem'
date: 2012-11-23T10:45:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=104
categories:
  - fsharp
tags:
  - fsharp
---
In the previous post, we talked about the difference between Critical and Normal code. In this post we are going to talk about the Critical code part. Ideally, we want:

  * A way to indicate that a particular piece of code (potentially the whole program) is Critical 
  * A way to force/encourage the programmer to make an explicit decision on the call site of a function on how he wants to manage the error conditions (both contingencies and faults) 
  * A way to force/encourage the programmer to expose contingencies/faults that are appropriate for the conceptual level of the function the code is in (aka don't expose implementation details for the function, i.e. don't throw SQLException from a getUser method where the caller is supposed to catch it) 

Remember that I can use the word 'force' here because the programmer has already taken the decision to analyse each line of code for error conditions. As we discussed in the previous post, In many/most cases, such level of scrutiny is unwarranted.

Let's use the below scenario to unravel the design:

```fsharp
type User = {Name:string; Age:int}
```

```fsharp
let fetchUser userName =
    let userText            = dbQuery (userName + ".user")
    let user                = parseUser(userText)
    user
```

This looks like a very reasonable .NET function and it is indeed reasonable in Normal code, but not in Critical code. Note that the caller likely needs to handle the user-not-in-repository case because there is no way for the caller to check such condition beforehand without incurring the performance cost of two network roundtrips.

Albeit the beauty and simplicity, there are issues with this function in a Critical context: 

  * The function throws implementation related exceptions, breaking encapsulation when the user needs to catch them 
  * It is not clear from the code if the developer thought about error management (do you think he did?) 
  * Preconditions are not checked, what about empty or null strings? 

To test our design let's define a fake dbQuery:

```fsharp
let dbQuery     = function
    | "parseError.user"     -> "parseError"
    | "notFound.user"       -> raise (FileNotFoundException())
    | "notAuthorized.user"  -> raise (UnauthorizedAccessException())
    | "unknown.user"        -> failwith "Unknown error reading the file"
    | _                     -> "FoundUser"
```

The first two exceptions are contingencies, the caller of fetchUser is supposed to manage them. The unknown.user exception is a fault in the implementation. parseError triggers a problem in the parseUser function.

ParseUser looks like this:

```fsharp
let parseUser   = function
    | "parseError"          -> failwith "Error parsing the user text"
    | u                     -> {Name = u; Age = 43}
```

Let's now create a test function to test the different versions of fetchUser that we are going to create:

```fsharp
let test fetchUser =
    let p x                 = try printfn "%A" (fetchUser x) with ex -> printfn "%A %s" (ex.GetType()) ex.Message
    p "found"
    p "notFound"
    p "notAuthorized"
    p "parseError"
    p "unknown"
```

Running the function exposes the problems described above. From the point of view of the caller, there is no way to know what to expect by just inspecting the signature of the function. There is no differentiation between contingencies and faults. The only way to achieve that is to catch some implementation-specific exceptions.

How would we translate this to Critical code?

First, we would define a type to represent the result of a function:

```fsharp
type Result<'a, 'b> =
| Success of 'a
| Failure of 'b
```

This is called the Either type, but the names have been customized to represent this scenario. We then need to define which kind of contingencies our function could return.

```fsharp
type UserFetchError =
| UserNotFound  of exn
| NotAuthorized of int * exn
```

So we assume that the caller can manage the fact that the user is not found or not authorized. This type contains an Exception member. This is useful in cases where the caller doesn't want to manage a contingency, but wants to treat it like a fault (for example when some Normal code is calling some Critical code).

In such cases, we don't lose important debugging information. But we still don't break encapsulation because the caller is not supposed to 'catch' a fault.

Notice that NotAuthorized contains an int member. This is to show that contingencies can carry some more information than just their type. For example, a caller could match on both the type and the additional data.

With that in place, let's see how the previous function looks like:

```fsharp
let tryFetchUser1 userName =
    if String.IsNullOrEmpty userName then invalidArg "userName" "userName cannot be null/empty"
    // Could check for file existence in this case, but often not (i.e. db)
    let userResult =    try
                            Success(dbQuery(userName + ".user"))
                        with
                        | FileNotFoundException as ex        -> Failure(UserNotFound ex)
                        | UnauthorizedAccessException as ex  -> Failure(NotAuthorized(2, ex))
                        | ex                                    -> reraise ()
    match userResult with
    | Success(userText) ->
        let user        = Success(parseUser(userText))
        user
    | Failure(ex)       -> Failure(ex)
```

Here is what changed:

  * Changed name to tryXXX to convey the fact that the method has contingencies 
  * Added precondition test, which generates a fault 
  * The signature of the function now conveys the contingencies that the user is supposed to know about 

But still, there are problems:

  * The code became very long and convoluted obfuscating the success code path 
  * Still, has the developer thought about the error conditions in parseUser and decided to let exceptions get out, or did she forget about it? 

The return value crowd at this point is going to shout: "Get over it!! Your code doesn't need to be elegant, it needs to be correct!". But I disagree, obfuscating the success code path is a problem because it becomes harder to figure out if your business logic is correct. It is harder to know if you solved the problem you set out to solve in the first place.

In the next post we'll see what we can do about keeping beauty and being correct.
