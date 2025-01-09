---
id: 42
title: 'Write Yourself a Scheme in 48 Hours in F# – Part II'
date: 2011-07-08T07:01:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/07/09/write-yourself-a-scheme-in-48-hours-in-f-part-ii/
categories:
  - fsharp
tags:
  - fsharp
  - Lambda expressions
  - Parsing
---
Usually, when I do blog posts that are all about code, I write them 'bottom up'. I start talking about the most primitive types and functions and build up from there toward higher abstractions. I think this is a pretty common way of doing it.

For this series I'm going to try the opposite. I start with the code that creates the REPL window and move down from there toward the guts of the interpreter. I hold the opinion that, if the code is written right, this should be ok. The naming scheme and general structure of it should allow understanding it at different levels.

Or at least I hope so.

Let's start from the _main_ function. Depending on the number of arguments it either runs the REPL window or executes whatever is in the file passed in as the first argument using the other arguments as parameters.

```fsharp
[<EntryPoint>]
let main(args: string[]) =
    match Array.toList args with
    | [] -> runRepl ()
    | filename :: args -> runOne filename args
    0
```

The latter case is coded in the below function. It first load all the primitive operators (i.e. '+', '-' etc…) and the standard library. The word 'load' above is a little misleading. In reality it adds them to the environment. It then proceeds to add the arguments that were passed on. As the last step, it evaluates the 'load' command by using the newly created environment, it transforms the returned token to a string and prints it.

```fsharp
let runOne (filename : string) (args : list<string>) =
    let env = primitiveBindings ()
                |> loadStdLib
                |> bindVars [ "args", List (List.map String args) ]
    List [Atom "load"; String filename] |> eval env |> showVal |> printStr
```

Running the REPL windows is equally simple. Load the primitive operators and the standard library, show a prompt and evaluate the input until the input is 'Quit'.

```fsharp
let runRepl () =
    let env = primitiveBindings () |> loadStdLib
    until (fun s -> s = "Quit" || s = "quit") (fun () -> readPrompt "Lisp>>> ") (evalAndPrint env)
```

_readPrompt_ is pretty simple:

```fsharp
let printStr (s: string) = Console.Write(s)
let readPrompt (s: string) = printStr s ; Console.ReadLine ()
```

_EvalAndPrint_ is written as a chain of functions (lookup the '>>' operator in F#) and just evaluate the string, transform the result to a string, prints it and newline it.

```fsharp
let newLine () = Console.WriteLine()
let evalAndPrint env = evalString env >> showVal >> printStr >> newLine
```

_evalString_ parses the string and evaluates the expression. Note the exception management. This is a result of my decision of throwing an exception every time something goes wrong instead of using a monad to pass the state around. I think it is pretty clear, but haskellers might disagre. This is one of the main differences from the Haskell version.

```fsharp
let evalString env expr =
    try
        expr |> readExpr |> eval env
    with
    | LispException(error) -> String (showError error)
```

For the sake of completeness, here is _until_. Maybe there is a library function somewhere that I could have used?

```fsharp
let rec until pred prompter evaluator =
    let result = prompter ()
    if not (pred result) then
        evaluator result
        until pred prompter evaluator
```

Back on the main flow of the code, _loadStdLib_ just loads the standard file and returns the populated environment.

```fsharp
let loadStdLib env =
    eval env (List [Atom "load"; String "stdlib.scm"]) |> ignore
    env
```

primitiveBindings creates a new empty environment and adds a bunch of pairs (primitiveName, LispVal –> LispVal). LispVal is a representation of a Scheme expression, so the second part of the tuple is simply a reduction from one expression to another (hopefully simpler in some sense). We'll talk more about LispVal in upcoming posts.

```fsharp
let primitiveBindings () =
    (nullEnv ()) |> bindVars [ for v, f in primitives -> v, PrimitiveFunc f ]
```

There you have it. That's the full implementation for the REPL window. Next post, we'll look at LispEval and the evaluator.
