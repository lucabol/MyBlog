---
id: 53
title: 'Write Yourself a Scheme in 48 Hours in F# – Part VI'
date: 2011-08-05T07:08:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/08/06/write-yourself-a-scheme-in-48-hours-in-f-part-vi/
categories:
  - fsharp
tags:
  - fsharp
  - Lambda expressions
  - Parsing
---
The evaluator takes as an input a _LispVal_. Where does it come from? There must be something that converts your textual input into it. That is the job of the parser.

I have used [FParsec](http://www.quanttec.com/fparsec/) to build my parser. FParsec is a fantastic library to build parsers. It is a perfect showcase of the composition potential that functional code yields.&#160; 

When you write an FParsec parser you compose many little parsers to create the one parser that works for your language.&#160; The resulting code looks very much like your language grammar, but you don't need&#160; a separate code generation compilation step to produce it.

There is one element of ugliness in the syntax to create recursive parsers. You need to define two global variables that can be referred to before they are constructed. This is an artefact of how F# works. So you need a line in your code that looks like this:

```fsharp
let parseExpr, parseExprRef : LispParser * LispParser ref = createParserForwardedToRef()
```

With that piece of machinery out of the way, we can focus on the parser itself. Our goal here is to parse expressions and generate _LispVal_. We need a _LispParser_ like the below (the second generic parameter is for advanced usage).

```fsharp
type LispParser = Parser<LispVal, unit>
```

We need to parse all the kind of expressions that the user can type. Notice in the below the use of a computation expression to simplify the syntax. Also note that lists and dotted lists look very much the same until you encounter the '.' character. You could disambiguate the situation by extracting out the commonality in a separate kind of expression. I decided instead to instruct the parser to backtrack if it gets it wrong (_attempt_). This is slower, but keeps the code identical to our conceptual model. I value that greatly. 

```fsharp
do parseExprRef := parseAtom
                   <|> parseString
                   <|> parseNumber
                   <|> parseQuoted
                   <|> parse {
                           do! chr '('
                           let! x = (attempt parseList) <|> parseDottedList
                           do! chr ')'
                           return x
                       }
```

Let's start from the top. Parsing an atom means parsing something that starts with a letter or symbol and continues with letters, symbols or digits. Also "#t" and "#f" can be resolved at parsing time.

```fsharp
let parseAtom : LispParser = parse {
        let! first = letter <|> symbol
        let! rest = manyChars (letter <|> symbol <|> digit)
        return match first.ToString() + rest with
               | "#t" -> Bool true
               | "#f" -> Bool false
               | atom -> Atom atom
}
```

A string is just a bunch of chars (except '\') surrounded by ' " '.

```fsharp
let parseString : LispParser = parse {
    do! chr '"'
    let! xs = manyChars (noneOf "\"")
    do! chr '"'
    return String(xs)
}
```

A number is just one or more digits. I am afraid we just support integers at this stage …

```fsharp
let parseNumber : LispParser = many1Chars digit |>> (System.Int32.Parse >> Number)
```

A quoted expression is jut a '\' followed by an expression.

```fsharp
let parseQuoted : LispParser = chr '\'' >>. parseExpr |>> fun expr -> List [Atom "quote"; expr]
```

A list is just a bunch of expressions separate by at least one space.

```fsharp
let parseList : LispParser = sepBy parseExpr spaces1 |>> List
```

A dotted list starts in the same way (hence the backtracking above), but then has a dot, one or more spaces and an expression.

```fsharp
let parseDottedList : LispParser = parse {
    let! head = endBy parseExpr spaces1
    let! tail = chr '.' >>. spaces1 >>. parseExpr
    return DottedList (head, tail)
}
```

And here are a bunch of functions used throughout the code, presented here for completeness.

```fsharp
let spaces1 : LispParser<unit> = skipMany1 whitespace
    let chr c = skipChar c
    let endBy  p sep = many  (p .>> sep)
    let symbol : LispParser<char> = anyOf "!$%&|*+-/:<=?>@^_~#"
```

This is all the code you need to translate text to a _LispVal_ to feed the evaluator. That is pretty impressive.

There is also a function to go the other way, from a LispVal to text. It is used in implementing the testcases and to print out diagnostics.

```fsharp
let rec showVal = function
        | String contents -> "\"" + contents + "\""
        | Atom name -> name
        | Number num -> num.ToString()
        | Bool t -> if t then "#t" else "#f"
        | List l -> "(" + unwordsList l + ")"
        | DottedList (head, tail) -> "(" + unwordsList head + " . " + showVal tail + ")"
        | PrimitiveFunc(_) -> "<primitive>"
        | Port (_) -> "<IO port>"
        | Func({ parms = parms; varargs = varargs; body = body; closure = closure }) ->
                                                "(lambda (" + unwordsList (parms |> List.map (String)) +
                                                    (match varargs with
                                                        | None -> ""
                                                        | Some(arg) -> " . " + arg) + ") ...)"
    and
        unwordsList = List.map showVal >> String.concat " "
