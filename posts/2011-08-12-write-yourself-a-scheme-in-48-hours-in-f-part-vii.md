---
id: 55
title: 'Write Yourself a Scheme in 48 Hours in F# – Part VII'
date: 2011-08-12T07:11:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/08/12/write-yourself-a-scheme-in-48-hours-in-f-part-vii/
categories:
  - fsharp
tags:
  - fsharp
  - Lambda expressions
  - Parsing
---
Let's talk about the environment now.&#160; This is the part of the interpreter that I like the least. It is a global variable and it contains a list of&#160; (string, LispVal) where the LispVal is mutable.

```fsharp
type Env = (string * LispVal ref) list ref
```

This is pretty bad. First of all, it immediately cuts off any option of running interpreters in different threads. Moreover, it makes a lot of functions in the evaluator to have side effects. That makes it much harder to reason about them.

In a world where I am provided with infinite time and energy, I would change it. In this world, I won't. If you try your hand at doing it, make sure that you pass all the testcases before declaring victory. The scope rules of Scheme are not all that obvious. A code reviewer called them the Italian scoping rules because he thought I got them wrong …

In any case, there isn't much to the symbol table management.&#160; You can create an empty one:

```fsharp
let nullEnv (): Env = ref List.empty
```

Check if a variable is bound:

```fsharp
let keyEq name (k, _) = name = k
let isBound var (env: Env) = !env |> List.exists (keyEq var)
```

Get a variable out:

```fsharp
let getVar var (env: Env) =
    let result = !env |> List.tryFind (keyEq var)
    match result with
    | None -> throw (UnboundVar("Getting an unbound variable: " , var))
    | Some(_, r) -> !r
```

Set the value of an existing variable:

```fsharp
let setVar var value (env:Env) =
    let result = !env |> List.tryFind (keyEq var)
    match result with
    | Some(_, v) -> v := value ; value
    | None -> throw (UnboundVar("Setting an unbound variable: " , var))
```

Or define a new variable in the environment. Note that if the variable already exist, its value gets set.

```fsharp
let define (env:Env) var value =
    let result = !env |> List.tryFind (keyEq var)
    match result with
    | Some(_, v) -> v := value ; value
    | None ->
        env := [var, ref value] @ !env; value
```

You can also bind a list of (string, LispVal) to the environment by prepending it to the existing ones:

```fsharp
let bindVars bindings (env:Env) =
   ref ((bindings |> List.map (fun (n, v) -> n , ref v)) @ !env)
```

Once you accept the evil of the global mutable variable scheme, these functions are easy enough.

The only piece left is error management. This is where my implementation differs from the Haskell version the most. In essence, I throw exception and catch them to report errors, while the Haskell version uses a monad to propagate the error information.

I have a _LispError_ that represents everything that can go wrong:

```fsharp
type LispError =
    | NumArgs of int * LispVal list
    | TypeMismatch of string * LispVal
    | ParseError of string * FParsec.Error.ParserError
    | BadSpecialForm of string * LispVal
    | NotFunction of string * string
    | UnboundVar of string * string
    | Default of string
    | IOError of string
```

I wrap it in an exception:

```fsharp
exception LispException of LispError
```

This is what I throw in various places in the code.

```fsharp
let throw le = raise (LispException(le))
```

I then catch it at the outer layer:

```fsharp
let evalString env expr =
    try
        expr |> readExpr |> eval env
    with
    | LispException(error) -> String (showError error)
```

And display the error by using the below function:

```fsharp
let showError = function
    | NumArgs(expected, found) -> "Expected " + expected.ToString() + " args; found values " + unwordsList found
    | TypeMismatch(expected, found) -> "Invalid type: expected " + expected + ", found " + showVal found
    | ParseError(msg, _) -> "Parse Errror" + msg
    | BadSpecialForm(message, form) -> message + showVal form
    | NotFunction(message, func) -> message + func
    | UnboundVar(message, varName) -> message + varName
    | Default(message) -> message
    | IOError(message) -> message
```

And that's all there is to it. I hope you guys and gals enjoyed this seven part extravagance. Cheers.
