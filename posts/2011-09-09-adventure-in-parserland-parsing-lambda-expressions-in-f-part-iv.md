---
id: 71
title: 'Adventure in parserland – parsing lambda expressions in F# – Part IV'
date: 2011-09-09T06:09:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/09/09/adventure-in-parserland-parsing-lambda-expressions-in-f-part-iv/
categories:
  - fsharp
tags:
  - fsharp
  - Lambda expressions
  - Parsing
---
Let' now look at the parser. First let's review the grammar:

```fsharp
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

And the data type to represent it:

```fsharp
type Name = string
and Body = Expression
and Function = Name * Expression
and FunctionExpression = Expression
and ArgumentExpression = Expression
and Expression =
| EName of string
| Function of Expression * Body
| Application of FunctionExpression * ArgumentExpression
| EOT
```

In essence, the data type need to store all the information needed for subsequent stages of computation (i.e. beta reductions and such). The closer it is to the grammar, the better. In this case it looks pretty close.

Remember what is the main goal of our parser:

```fsharp
let parseTextReader: TextReader -> seq<Expression> =
                    textReaderToLazyList >> tokenStream >> parseExpressions
```

We have already looked at _TextReaderToLazyList_ and _tokenStream_. Now it is the time to look at _parseExpressions_. It's goal is to&#160; parse the _LazyList<Token>_ and return a sequence of expressions. The choice of returning a sequence at this point is to make the _parseTextReader_, which is the main function in the program, return a more 'standard' type.

```fsharp
and parseExpressions tokens = seq {
   let tokens = parseOptionalWs tokens
   let expr, tokens = parseExpr tokens
   let tokens = parseOptionalWs tokens
   match expr with
    | EOT   -> yield EOT
    | exp   -> yield exp; yield! parseExpressions tokens }
```

_parseOtionalWs_ simply skips ahead whatever whitespaces it finds.

```fsharp
and parseOptionalWs tokens = match tokens with
                                | LazyList.Nil -> LazyList.empty
                                | LazyList.Cons(h, t) ->
                                    match h with
                                       | Ws _ -> parseOptionalWs t
                                       | _ -> tokens
```

_parseExpr_ is more interesting. It is the main switch that creates expression kinds.

```fsharp
let rec parseExpr tokens = match tokens with
                            | LazyList.Nil -> EOT, LazyList.empty
                            | LazyList.Cons(h, t) ->
                                match h with
                                    | EOF -> parseEOF tokens
                                    | Name _ -> parseName  tokens
                                    | Lambda -> parseFunction tokens
                                    | OpenParens -> parseApplication tokens
                                    | token -> errorAtStart "Expression" token
```

_parseEOF_ is not.

```fsharp
and parseEOF tokens = EOT, LazyList.empty
```

_parseName_ just returns a _EName_, unwrapping it from Name.

```fsharp
and parseName tokens = EName (head tokens |> unwrapName), tail tokens
```

Unwrap just unwraps it.

```fsharp
let unwrapName = function
    | Name(s) -> s
    | tok -> errorExpecting "a Name" <| writeToken tok
```

_parseFunction_ just conumes a Lambda, a name, a Dot token, a body (i.e. \x.x)and assembles them in a Function:

```fsharp
and parseFunction tokens =
    let tokens = consumeToken Lambda tokens
    let name, tokens = parseName tokens
    let tokens = consumeToken Dot tokens
    let body, tokens = parseExpr tokens
    Function(name, body), tokens
```

_consumeToken_ tries to consume a token generating an error if it doesn't find it:

```fsharp
let consumeToken token =
    genericConsumeToken (fun token' _ -> errorExpecting (writeToken token') (writeToken token)) token
```

_genericConsumeToken_ is just a generalization of the function above:

```fsharp
let genericConsumeToken noMatch token = function
    | LazyList.Nil -> LazyList.empty
    | LazyList.Cons(h, t) as originalTokens ->
        match h with
        | tok when tok = token -> t
        | tok -> noMatch token originalTokens
```

The last thing left to consume is an application which is in this form (func args):

```fsharp
and parseApplication tokens =
    let tokens = consumeToken OpenParens tokens
    let funExpr, tokens = parseExpr tokens
    let tokens = parseOptionalWs tokens
    let argExpr, tokens = parseExpr tokens
    let tokens = consumeToken CloseParens tokens
    Application(funExpr, argExpr), tokens
```

Various error and utility functions are defined below:

```fsharp
let errorEOF expecting = failwith  ("Expected " + expecting + ", got EOF")
let errorExpecting expecting gotToken = failwith ("Expected " + expecting + ", got" + gotToken)
let errorAtStart expecting gotToken = failwith ("Expected " + expecting + " which cannot start with" + writeToken gotToken)
let tail = LazyList.tail
let head = LazyList.head
```

And that is the parser. All 100+ lines of it. As you can tell it is rather formulaic to go from a grammar to a lexer and a parser, which is why you shouldn't do it, but instead let a tool generate the code for you given the grammar or use FParsec.

We have written 200+ code and I don't think we can be too proud of our achievement. It is:

  * Certainly buggy
  * Primitive in error handling
  * Not tail recursive (big text is likely to blow up our stack)
  * Probably inefficient

So let's look next at a better way to do it.
