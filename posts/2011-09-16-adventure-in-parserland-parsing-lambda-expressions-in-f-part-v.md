---
id: 73
title: 'Adventure in parserland – parsing lambda expressions in F# – Part V'
date: 2011-09-16T06:57:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/09/16/adventure-in-parserland-parsing-lambda-expressions-in-f-part-v/
categories:
  - fsharp
tags:
  - fsharp
  - Lambda expressions
  - Parsing
---
We are now going to look at a solution which is concise, efficient and gives sophisticated error messages. It is also less than 20 lines of code. We'll be using [FParsec](http://www.quanttec.com/fparsec/).

FParsec is a port of an Haskell library. It is a parser combinator library or, as I like to think of it, an internal [DSL](http://www.google.co.uk/url?sa=t&source=web&cd=1&ved=0CC0QFjAA&url=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FDomain-specific_language&ei=2uInTsvgG4LDhAfxrIzvCQ&usg=AFQjCNFeEXnlId4QmC-faKR_2dF1paxZMA&sig2=aCu7doIcVL0yFVlg3uA-pA) to build parsers in F#. My usual disclaimer: I'm not an expert in FParsec. It is likely that, if you are an expert, you can come up with more maintainable/efficient/elegant version of this parser.

The whole code is below:

```fsharp
let ws = " \t\n"
let specialChars = ".)(\\\n"
let pWs = spaces
let pName = manyChars (noneOf (ws + specialChars)) |>> EName
let pExpr, pExprRef = createParserForwardedToRef<Expression, Unit>()
let curry2 f a b = f(a,b)
let pFunction = pchar '\\' >>. pipe2 pName (pchar '.' >>. pExpr) (curry2 Function)
let pApplication = pchar '(' >>. pipe2 pExpr (pWs >>. pExpr) (curry2 Application)
                          .>> pWs .>> pchar ')'
do pExprRef := pFunction <|> pApplication <|> pName
let pExpressions = sepBy pExpr spaces1
```

This mirrors pretty closely the grammar we are trying to parse. A program is a bunch of expressions separated by whitespaces.

```fsharp
let pExpressions = sepBy pExpr spaces1
```

sepBy is a combinator that takes a parser that defines what to parse and a parser that defines what the separator should be. And the separator should be one or more spaces …

_pExpr_ is either a function, an application or a name. the operator <|> is a choice combinator that tries each parser in order. It tries the right parser just if the left parser fails and it doesn't consume input. So it doesn't backtrack. If you need a backtracking parser, you'll need to get acquainted with the _attempt_ combinator.

```fsharp
do pExprRef := pFunction <|> pApplication <|> pName
```

A function starts with a '\', then comes a name, a dot and an expression. 

```fsharp
let pFunction = pchar '\\' >>. pipe2 pName (pchar '.' >>. pExpr) (curry2 Function)
```

I know that might look crazy (and maybe it is), but just bear with me. Someone , who I'm not sure I can name, once told me that functional programming is great to write code, but terrible to read it and debug it. The phrase stayed with me as containing a grain of truth. In any case, in the code above:

  * >>. is a combinator that says "use the left parser, discard its value and then use the right one, returning its value". Try to guess what .>> does … 
  * pipe2 is a combinator that says "apply the first parser, the second parser and then call a function passing as parameters the values returned by the two parsers 
  * curry2 is a function combinator that transform a function that takes a tuple to a function that takes the parameters as untupled 

```fsharp
let curry2 f a b = f(a,b)
```

An application works similarly, but differently …

```fsharp
let pApplication = pchar '(' >>. pipe2 pExpr (pWs >>. pExpr) (curry2 Application)
                          .>> pWs .>> pchar ')'
```

The only difference is that now we have to consume the optional whitespaces and the ')' at the end. A rule of thumb that I use is to use >>.&#160; to flow the result through and pipeX when I need more than one result.

The last thing is pName, which consume chars until it finds either a whitespace or a special char.

```fsharp
let ws = " \t\n"
let specialChars = ".)(\\\n"
let pWs = spaces
let pName = manyChars (noneOf (ws + specialChars)) |>> EName
```

And there you have it, a lexer, a parser all in 20 lines of code. I don't like the code that I wrote above much. I'm sure I could refine it plenty and it probably contains some bugs, but it gives an idea of what is possible with FParsec.
