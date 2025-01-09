---
id: 107
title: 'Exceptions vs. Return Values to represent errors (in F#) – III–The Critical monad'
date: 2012-11-30T16:41:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=107
categories:
  - fsharp
tags:
  - fsharp
---
Code for this post is [here](https://github.com/lucabol/ErrorExceptional).

In the last post we looked at some Critical code and decided that, albeit correct, it is convoluted. The error management path obfuscates the underlying logic. Also we have no way of knowing if a developer had thought about the error path or not when invoking a function.

Let's tackle the latter concern first as it is easier. We want the developer to declaratively tag each method call with something that represents his intent about managing the Contingencies or Faults of the function. Moreover if the function has contingencies, we want to force the developer to manage them explicitly.

We cannot use attributes for this as function calls happen in the middle of the code, so there is no place to stick attributes into. So we are going to use higher level functions to wrap the function calls. 

The first case is easy. If the developer thinks that the caller of his code has no way to recover from all the exceptions thrown by a function, he can prepend his function call with the 'fault' word as in:

```fsharp
fault parseUser userText
```

That signals readers of the code that the developer is willing to propagate up all the exceptions thrown by the function parseUser. Embarrassingly, 'fault' is implemented as:

```fsharp
let fault f = f
```

So it is just a tag. Things get trickier when the function has contingencies. We want to find a way to manage them without introducing undue complexity in the code. 

We'd like to catch some exceptions thrown by the function and convert them to return values and then either return such return values or manage the contingency immediately after the function call. On top of that, we'd want all of the code written after the function call to appear as clean as if no error management were taking place. Monads (computation values) can be used to achieve these goals.

Last time we introduced a type to represent error return values:

```fsharp
type Result<'a, 'b> =
| Success of 'a
| Failure of 'b
```

```fsharp
type UserFetchError =
| UserNotFound  of exn
| NotAuthorized of int * exn
```

We can then create a computation expression that 'abstracts out' the Failure case and let you write the code as cleanly as if you were not handling errors. Let's call such thing 'critical'. Here is how the final code looks like:

```fsharp
let tryFetchUser3 userName =
    if String.IsNullOrEmpty userName then invalidArg "userName" "userName cannot be null/empty"
    critical {
        let Unauthorized (ex:exn) = NotAuthorized (ex.Message.Length, ex)
        let! userText = contingent1
                            [FileNotFoundException()        :> exn, UserNotFound;
                             UnauthorizedAccessException()  :> exn, Unauthorized]
                            dbQuery (userName + ".user")
        return fault parseUser userText
    }
```

You can compare this with the code you would have to write without the 'critical' library (from last post):

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

And with the original (not critical) function:

```fsharp
let fetchUser userName =
    let userText            = dbQuery (userName + ".user")
    let user                = parseUser(userText)
    user
```

Let's go step by step and see how it works. First of all, you need to enclose the Critical parts of your code (perhaps your whole program) in a 'critical' computation:

```fsharp
critical {
   ...
}
```

This allows you to call functions that return a Result and manage the return result as if it were the successful result. If an error were generated, it would be returned instead. We will show how to manage contingencies immediately after the function call later.

The above is illustrated by the following:

```fsharp
let! userText = contingent1
                    [FileNotFoundException()        :> exn, UserNotFound;
                     UnauthorizedAccessException()  :> exn, Unauthorized]
                    dbQuery (userName + ".user")
```

Here 'contingent1' is a function that returns a Result, but userText has type string. The Critical monad, and in particular the usage of 'let!' is what allows the magic to happen.

'contingentN' is a function that you call when you want to manage certain exceptions thrown by a function as contingencies. The N part represents how many parameters the function takes.

The first parameter to 'contingent1' is a list of pairs (Exception, ErrorReturnConstructor). That means: when an exception of type Exception is thrown, return the result of calling 'ErrorReturnConstructor(Exception)' wrapped inside a 'Failure' object. The second parameter to 'contingent1' is the function to invoke and the third is the argument to pass to it.

Conceptually, 'ContingentN' is a tag that says: if the function throws one of these exceptions, wrap them in these return values and propagate all the other exceptions. Notice that Unauthorized takes an integer and an exception as parameters while the ErrorReturnConstructor takes just an exception. So we need to add this line of code:

```fsharp
let Unauthorized (ex:exn) = NotAuthorized (ex.Message.Length, ex)
```

After the contingent1 call, we can then write code as if the function returned a normal string:

```fsharp
return fault parseUser userText
```

This achieves that we set up to do at the start of the series:

  * Contingencies are now explicit in the signature of tryFetchUser3 
  * The developer needs to indicate for each function call how he intend to manage contingencies and faults 
  * The code is only slightly more complex than the non-critical one 

You can also decide to manage your contingencies immediately after calling a function. Perhaps there is a way to recover from the problem. For example, if the user is not in the database, you might want to add a standard one:

```fsharp
let createAndReturnUser userName = critical { return {Name = userName; Age = 43}}
let tryFetchUser4 userName =
    if String.IsNullOrEmpty userName then invalidArg "userName" "userName cannot be null/empty"
    critical {
        let Unauthorized (ex:exn) = NotAuthorized (ex.Message.Length, ex) // depends on ex
        let userFound = contingent1
                            [FileNotFoundException()        :> exn, UserNotFound;
                             UnauthorizedAccessException()  :> exn, Unauthorized]
                            dbQuery (userName + ".user")
        match userFound with
        | Success(userText)         -> return  fault parseUser userText
        | Failure(UserNotFound(_))  -> return! createAndReturnUser(userName)
        | Failure(x)                -> return! Failure(x)
    }
```

The only difference in this case is the usage of 'let' instead of 'let!'. This exposes the real return type of the function allowing you to pattern match against it.

Sometimes a simple exception to return value mapping might not be enough and you want more control on which exceptions to catch and how to convert them to return values. In such cases you can use contingentGen:

```fsharp
let tryFetchUser2 userName =
    if String.IsNullOrEmpty userName then invalidArg "userName" "userName cannot be null/empty"
    critical {
        let! userText = contingentGen
                            (fun ex -> ex FileNotFoundException || ex UnauthorizedAccessException)
                            (fun ex ->
                                match ex with
                                       | FileNotFoundException       -> UserNotFound(ex)
                                       | UnauthorizedAccessException -> NotAuthorized(3, ex)
                                       | _ -> raise ex)
                            (fun _ -> dbQuery (userName + ".user"))
        return fault parseUser userText
    }
```

The first parameter is a lambda describing when to catch an exception. The second lambda translate between exceptions and return values. The third lambda represents which function to call.

Sometimes you might want to catch all the exceptions that a function might throw and convert them to a single return value:

```fsharp
type GenericError = GenericError of exn
// 1. Wrapper that prevents exceptions for escaping the method by wrapping them in a generic critical result
let tryFetchUserNoThrow userName =
    if String.IsNullOrEmpty userName then invalidArg "userName" "userName cannot be null/empty"
    critical {
        let! userText = neverThrow1 GenericError dbQuery (userName + ".user")
        return fault parseUser userText
    }
```

And sometimes you might want to go the opposite way. Given a function that exposes some contingencies, you want to translate them to faults because you don't know how to recover from them.

```fsharp
let operateOnExistingUser userName =
    let user = alwaysThrow GenericException tryFetchUserNoThrow userName
    ()
```

Next time we'll look at how the Critical computation expression is implemented.
