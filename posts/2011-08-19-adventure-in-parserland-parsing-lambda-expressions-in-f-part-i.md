---
id: 66
title: 'Adventure in parserland – parsing lambda expressions in F# – Part I'
date: 2011-08-19T06:53:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/08/19/adventure-in-parserland-parsing-lambda-expressions-in-f-part-i/
categories:
  - fsharp
tags:
  - fsharp
  - Lambda expressions
  - Parsing
---
This is part of my 'things that I do in the empty spaces between one meeting and the next one, which might end up being vaguely interesting'. It is a lambda expression parser.

The full source code is [here](http://code.msdn.microsoft.com/Parsing-Lambda-Expressions-7ad5271f).

I actually have two versions of it: one written longhand and the other one written with [FParsec](http://www.quanttec.com/fparsec/about/fparsec-vs-alternatives.html). Just to be clear: I'm no expert of either.

And just to be more clear: I think writing most parsers longhand in the way I am about to show is crazy. You either use FParsec or&#160; [fslex / fsyacc](http://blogs.msdn.com/b/jomo_fisher/archive/2010/06/15/use-fslex-and-fsyacc-to-make-a-parser-in-f.aspx).

I have a strong distaste for additional compilation steps. I think it lingers on from MFC project types of 15/20 years ago. I was one of these crazy folks that would generate the project, wrap the generated code (with some generalizations) in my own library and use that one from then on.

So I prefer FParsec. I'm ok rewriting [left recursive](http://en.wikipedia.org/wiki/Left_recursion) rules and its performance has never been a problem for me. [Here](http://www.quanttec.com/fparsec/about/fparsec-vs-alternatives.html) is a table that compares the different approaches.

But I started wondering about coding a a recursive descent parser for a simple grammar by hand, fully knowing the foolishness of the idea. Thanks to [Jose](http://www.haskellers.com/user/pepeiborra) for code reviewing it.

The inspiration for the grammar comes from [this book](http://www.google.co.uk/url?sa=t&source=web&cd=4&ved=0CDgQFjAD&url=http%3A%2F%2Fwww.amazon.com%2FIntroduction-Functional-Programming-Calculus-International%2Fdp%2F0201178125&ei=KoklTqzjF4GWhQf-w5XlCQ&usg=AFQjCNGPzv_27nSNwctaEykBivq3N-I7Dg&sig2=4iLu_nZnd8GlwPXpt8crMg).

```text
(*
        <expression> ::= <name> | <function> | <application>
        <name> ::= non­blank character sequence
        <function> ::= \ <name> . <body>
        <body> ::= <expression>
        <application> ::= ( <function expression> <argument expression> )
        <function expression> ::= <expression>
        <argument expression> ::= <expression>
    *)
```

In English, an expression is either a name, a function or an application. A name is a bunch of characters (better defined in the code). A function is '\', a name, '.' and an expression. An application is '(', an expression, whitespaces, an expression and ')'.

Some testcases for the above grammar and the parsers written to parse it are below. It should be intuitive what this code does just by the name of the functions. Even it isn't, check that the expressions symbol contains valid productions from the grammar above.

```fsharp
module Test
open Microsoft.FSharp.Collections
open Xunit
open LambdaEngine
open Parser
open Lexer
open FParser

let writeTokenStream stream = Seq.fold (fun acc token -> acc + writeToken token) "" stream

let rec writeExpr = function
        | EName(s) -> s
        | Function(expr, body) -> writeToken Lambda + writeExpr expr + writeToken Dot + writeExpr body
        | Application(funExpr, argExpr) -> writeToken OpenParens + writeExpr funExpr + writeToken (Ws(" "))
                                            + writeExpr argExpr + writeToken CloseParens
        | EOT -> ""

let tokenStreams = [
    ""
    "(\xs.xs \y.(y \x.y))"
    "(\xst.xst \y.(y  \x.y))"
    " "
    "x"
    "(x y)"
    ]

let expressions = [
    ""
    "(\x.x \y.(y \x.y))"
    "x"
    "(x y)"
    ]

let stringToCharList s =
    let textReader = new System.IO.StringReader(s)
    textReaderToLazyList textReader

[<Fact>]
let testTokenizer () =
    let testTokenStream s =
        let stream = tokenStream <| stringToCharList s
        let s1 = writeTokenStream stream
        Assert.Equal(s, s1)
    tokenStreams |> List.iter testTokenStream

let testExpr parseFunction s =
    let exprs = parseFunction s
    let s1 = exprs |> Seq.fold (fun s expr -> s + writeExpr expr) ""
    Assert.Equal(s, s1)

[<Fact>]
let testParser () = expressions |> List.iter (testExpr parseString)

[<Fact>]
let testFParser () = expressions |> List.iter (testExpr fparseString)
```

In the next instalment, we'll start looking at the real code for the parser.
