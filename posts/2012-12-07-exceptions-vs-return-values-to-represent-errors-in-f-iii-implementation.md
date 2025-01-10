---
id: 109
title: 'Exceptions vs. Return Values to represent errors (in F#) – IV – Implementation'
date: 2012-12-07T09:44:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=109
categories:
  - fsharp
tags:
  - fsharp
---
The Critical monad is defined as follows. First there is the type that propagates through the monad: 

```fsharp
type Result<'a, 'b> =
| Success of 'a
| Failure of 'b
```

Then we define the usual computation expression methods.

```fsharp
type Critical() =
       // a -> m a
        member o.Return x       = Success x
        // m a -> (a -> m b) -> m b
        member o.Bind (m, f)    = match m with
                                    | Failure e -> Failure e
                                    | Success x -> f x
        // m a -> m a
        member o.ReturnFrom m   = m
```

Explaining how computational expressions work in F# is a blog onto itself. And several chapters in many books. Sufficient to say that conceptually this propagates the success value and returns the failure value.

We then define an instance of this type, so that we can use the nice 'critical { ... }' syntax.

```fsharp
let critical = Critical()
```

We then go and define the functions that the user needs to use to annotate their function calls. The simplest one is the one to propagate any exception coming from the function 'f'.

```fsharp
let fault f = f
```

Then it comes the one to manage contingencies. This will trap any exception for which 'stopF ex' is 'true', call 'errF ex' to construct the error return value and wrap it in a 'Failure'. Otherwise it will rethrow the exception.

```fsharp
let contingentGen stopF errF f =
    try
        Success(f ())
    with
        | ex when stopF ex -> Failure(errF ex)
        | _                -> reraise ()
```

Albeit very simple, the above is the core of the system. Everything else is just details. Let's look at them.

First we want a function that takes as parameter a list of (Exception, ReturnValue) and gives back the correct stopF errF to plug into 'contingentGen'.

```fsharp
let exceptionMapToFuncs exMap =
    let tryFind ex = exMap |> List.tryFind (fun (k, _) -> k.GetType() = ex.GetType())
    (fun ex ->
        let found = tryFind ex
        match found with Some(_) -> true | None -> false),
    (fun ex ->
        let found = tryFind ex
        match found with
        | Some(k, v)    -> v ex
        | None          -> raise ex)
```

Then ugliness comes. For the sake of getting a decent syntax (not great) on the calling site, we need to fake overloading of functions by the old trick of adding a number at the end. Thanks to [Tobias](http://gotocon.com/amsterdam-2012/speaker/Tobias+Gedell) to point out this (my api was even worse earlier).

I often wondered about the trade-off between currying and overloading for functions. I seem to always paint myself in a situation where I need overloading. In any case, here it goes:

```fsharp
let contingent1 exMap f x =
    let stopF, errF = exceptionMapToFuncs exMap
    contingentGen stopF errF (fun _ -> f x)
let contingent2 exMap f x y =
    let stopF, errF = exceptionMapToFuncs exMap
    contingentGen stopF errF (fun _ -> f x y)
let contingent3 exMap f x y z =
    let stopF, errF = exceptionMapToFuncs exMap
    contingentGen stopF errF (fun _ -> f x y z)
```

Sometimes you want to trap all exceptions from a function and return your own error value:

```fsharp
let neverThrow1 exc f x     = contingentGen (fun _ -> true) (fun ex -> exc ex) (fun _ -> f x)
let neverThrow2 exc f x y   = contingentGen (fun _ -> true) (fun ex -> exc ex) (fun _ -> f x y)
let neverThrow3 exc f x y z = contingentGen (fun _ -> true) (fun ex -> exc ex) (fun _ -> f x y z)
```

Other times you need to go from a function that returns return values to one that throws exceptions. You need translating from contingencies to faults:

```fsharp
let alwaysThrow exc f x =
    match f x with
    | Success(ret)              -> ret
    | Failure(e)                -> raise (exc e)
```

And that's it. Hopefully we have bridged the gap between exceptions and return values without making the code too ugly (just a little bit). Or perhaps not.

I need to add that I haven't used this library myself (yet). I'm sure when I do I'll discover many things to change.
