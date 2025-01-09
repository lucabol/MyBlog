---
id: 69
title: 'Adventure in parserland – parsing lambda expressions in F# – Part III'
date: 2011-09-02T15:25:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/09/02/adventure-in-parserland-parsing-lambda-expressions-in-f-part-iii/
categories:
  - fsharp
tags:
  - fsharp
  - Lambda expressions
  - Parsing
---
Let's start from the lexer. Remember, I wrote this code based on my memory of how a lexer ought to look like. I didn't read again the relevant chapters in [the Dragon book](http://en.wikipedia.org/wiki/Principles_of_Compiler_Design). But I think it came out all right after all.

The _tokenStream_ function we looked at last time takes a _LazyList<char>_ and returns a _LazyList<Token>_. It uses the unfold method on _LazyList_ to call _matchToken_ on each char until the stream is empty.

```fsharp
let rec tokenStream chars =
    LazyList.unfold
        (fun chList ->
            match chList with
            | LazyList.Nil -> None
            | chList ->
                let token, chList' = matchToken chList
                Some(token, chList')
        )
        chars 
```

A token is what gets passed up to the parser to do syntactic analysis on. It is the vocabulary of our language. The lexer divide a phrase in words, the parser put together the words in a phrase. So, these are the words.

```fsharp
type Token =
    | Name of string
    | Dot
    | OpenParens
    | CloseParens
    | Lambda
    | Def
    | Ws of string
    | NewLine
    | EOF
```

Matching is a process whereas you try to return the token that you have read plus the list of characters yet to be read. Matching a Token is defined below:

```fsharp
let matchToken = function
    | LazyList.Nil                 -> EOF, LazyList.empty
    | LazyList.Cons(h, t) as chars ->
        match h with
        | ch when isWs ch -> matchWs chars
        | ch when isSpecialChar ch -> matchSpecialChar ch t
        | _ -> matchString chars
```

A token is either nothing, a whitespace, a special char or anything else.

Let's look at what matching each one of them means.&#160; Matching whitespaces means consuming them and remembering what was consumed.

```fsharp
let matchWs chars =
    let value, remainingChars = matchSeriesOfChars isWs chars
    Ws value, remainingChars
```

_matchSeriesOfChars_ takes a predicate and a _LazyList_ of chars and returns the string composed of all the consecutive chars for which the predicate is true, plus, as always, the remaining chars to be matched. In this case the predicate returns true if the char is a whitespace.

To write _matchSeriesOfChars_ I need a function that reverses a LazyList. Not having found such thing, I wrote it.

```fsharp
let reversell l =
    let rec go l' a = match l', a with
                        | LazyList.Nil, a -> a
                        | LazyList.Cons(h, t), a -> go t (LazyList.cons h a)
    go l LazyList.empty
```

Then I wrote _matchSeriesOfChars_. The function uses an accumulator. It adds to the front whenever the predicate is true, it reverses it and translates it to a string (I could have reversed the string instead, it might have been better).

```fsharp
let matchSeriesOfChars comparer chars =
    let rec go result = function
        | LazyList.Nil    -> charListToString(reversell result), LazyList.empty
        | LazyList.Cons(h, t) -> if comparer h then go (LazyList.cons h result) t
                                 else charListToString (reversell result), LazyList.cons h t
    go LazyList.empty chars
```

These are&#160; predicates we'll use later on to recognize characters:

```fsharp
let isInString (ch: char) (s: string) = s.IndexOf(ch) <> -1
let isWs (chr: char) = isInString chr wsChars
let isNameChar (chr: char) = not (isInString chr (wsChars + specialChars))
let isSpecialChar ch = isInString ch specialChars
```

_wsChar_ and _specialChars_ are defined below:

```fsharp
let wsChars = " \t"
```

```fsharp
let charTokens =
    Map.ofList [
        '.', Dot
        '(', OpenParens
        ')', CloseParens
        '\\', Lambda
        '\n', NewLine
     ]
let specialChars = charTokens |> Map.fold (fun s k v -> s + k.ToString()) ""
```

Getting back to the more important matching functions, matching a special character is defined as a simple lookup in the _charToken_ map:

```fsharp
let matchSpecialChar ch chars = Map.find ch charTokens, chars
```

We are left with matchString, this simply matches the characters until it finds a char that cannot be part of a name. It then looks it up in a list of special strings. If it finds it, it returns it, otherwise it just returns the name.

```fsharp
let stringTokens =
    Map.ofList [
        "Def", Def
    ]
```

```fsharp
let matchString chars =
    let value, remainingChars = matchSeriesOfChars isNameChar chars
    let specialString = Map.tryFind value stringTokens
    if specialString.IsSome
        then specialString.Value, remainingChars
        else Name(value), remainingChars
```

And we are done with the lexer, all of 100+ lines of it …
