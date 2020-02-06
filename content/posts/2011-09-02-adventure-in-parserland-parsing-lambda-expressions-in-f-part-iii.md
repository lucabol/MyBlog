---
id: 69
title: 'Adventure in parserland – parsing lambda expressions in F# – Part III'
date: 2011-09-02T15:25:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/09/02/adventure-in-parserland-parsing-lambda-expressions-in-f-part-iii/
permalink: /2011/09/02/adventure-in-parserland-parsing-lambda-expressions-in-f-part-iii/
categories:
  - fsharp
tags:
  - fsharp
  - Lambda expressions
  - Parsing
---
Let’s start from the lexer. Remember, I wrote this code based on my memory of how a lexer ought to look like. I didn’t read again the relevant chapters in [the Dragon book](http://en.wikipedia.org/wiki/Principles_of_Compiler_Design). But I think it came out all right after all.

The _tokenStream_ function we looked at last time takes a _LazyList<char>_ and returns a _LazyList<Token>_. It uses the unfold method on _LazyList_ to call _matchToken_ on each char until the stream is empty.

<pre class="code"><span style="color:blue;">let rec </span>tokenStream chars =
    LazyList.unfold
        (<span style="color:blue;">fun </span>chList <span style="color:blue;">-&gt;
            match </span>chList <span style="color:blue;">with
            </span>| LazyList.Nil <span style="color:blue;">-&gt; </span>None
            | chList <span style="color:blue;">-&gt;
                let </span>token, chList' = matchToken chList
                Some(token, chList')
        )
        chars </pre>

A token is what gets passed up to the parser to do syntactic analysis on. It is the vocabulary of our language. The lexer divide a phrase in words, the parser put together the words in a phrase. So, these are the words.

<pre class="code"><span style="color:blue;">type </span>Token =
    | Name <span style="color:blue;">of </span>string
    | Dot
    | OpenParens
    | CloseParens
    | Lambda
    | Def
    | Ws <span style="color:blue;">of </span>string
    | NewLine
    | EOF</pre>

Matching is a process whereas you try to return the token that you have read plus the list of characters yet to be read. Matching a Token is defined below:

<pre class="code"><span style="color:blue;">let </span>matchToken = <span style="color:blue;">function
    </span>| LazyList.Nil                 <span style="color:blue;">-&gt; </span>EOF, LazyList.empty
    | LazyList.Cons(h, t) <span style="color:blue;">as </span>chars <span style="color:blue;">-&gt;
        match </span>h <span style="color:blue;">with
        </span>| ch <span style="color:blue;">when </span>isWs ch <span style="color:blue;">-&gt; </span>matchWs chars
        | ch <span style="color:blue;">when </span>isSpecialChar ch <span style="color:blue;">-&gt; </span>matchSpecialChar ch t
        | _ <span style="color:blue;">-&gt; </span>matchString chars</pre></p> 

A token is either nothing, a whitespace, a special char or anything else.



Let’s look at what matching each one of them means.&#160; Matching whitespaces means consuming them and remembering what was consumed.

<pre class="code"><span style="color:blue;">let </span>matchWs chars =
    <span style="color:blue;">let </span>value, remainingChars = matchSeriesOfChars isWs chars
    Ws value, remainingChars</pre>

_matchSeriesOfChars_ takes a predicate and a _LazyList_ of chars and returns the string composed of all the consecutive chars for which the predicate is true, plus, as always, the remaining chars to be matched. In this case the predicate returns true if the char is a whitespace.

To write _matchSeriesOfChars_ I need a function that reverses a LazyList. Not having found such thing, I wrote it.

<pre class="code"><span style="color:blue;">let </span>reversell l =
    <span style="color:blue;">let rec </span>go l' a = <span style="color:blue;">match </span>l', a <span style="color:blue;">with
                        </span>| LazyList.Nil, a <span style="color:blue;">-&gt; </span>a
                        | LazyList.Cons(h, t), a <span style="color:blue;">-&gt; </span>go t (LazyList.cons h a)
    go l LazyList.empty</pre>

Then I wrote _matchSeriesOfChars_. The function uses an accumulator. It adds to the front whenever the predicate is true, it reverses it and translates it to a string (I could have reversed the string instead, it might have been better).

<pre class="code"><span style="color:blue;">let </span>matchSeriesOfChars comparer chars =
    <span style="color:blue;">let rec </span>go result = <span style="color:blue;">function
        </span>| LazyList.Nil    <span style="color:blue;">-&gt; </span>charListToString(reversell result), LazyList.empty
        | LazyList.Cons(h, t) <span style="color:blue;">-&gt; if </span>comparer h <span style="color:blue;">then </span>go (LazyList.cons h result) t
                                 <span style="color:blue;">else </span>charListToString (reversell result), LazyList.cons h t
    go LazyList.empty chars</pre>

These are&#160; predicates we’ll use later on to recognize characters:

<pre class="code"><span style="color:blue;">let </span>isInString (ch: char) (s: string) = s.IndexOf(ch) &lt;&gt; -1
<span style="color:blue;">let </span>isWs (chr: char) = isInString chr wsChars
<span style="color:blue;">let </span>isNameChar (chr: char) = not (isInString chr (wsChars + specialChars))
<span style="color:blue;">let </span>isSpecialChar ch = isInString ch specialChars</pre>

_wsChar_ and _specialChars_ are defined below:

<pre class="code"><span style="color:blue;">let </span>wsChars = <span style="color:maroon;">" \t"</span></pre>

<pre class="code"><span style="color:blue;">    let </span>charTokens =
        Map.ofList [
            <span style="color:maroon;">'.' </span>, Dot
            <span style="color:maroon;">'(' </span>, OpenParens
            <span style="color:maroon;">')' </span>, CloseParens
            <span style="color:maroon;">'\\'</span>, Lambda
            <span style="color:maroon;">'\n'</span>, NewLine
         ]<br />
    <span style="color:blue;">let </span>specialChars = charTokens |&gt; Map.fold (<span style="color:blue;">fun </span>s k v <span style="color:blue;">-&gt; </span>s + k.ToString()) <span style="color:maroon;">""</span></pre>



Getting back to the more important matching functions, matching a special character is defined as a simple lookup in the _charToken_ map:

<pre class="code"><span style="color:blue;">let </span>matchSpecialChar ch chars = Map.find ch charTokens, chars</pre>

We are left with matchString, this simply matches the characters until it finds a char that cannot be part of a name. It then looks it up in a list of special strings. If it finds it, it returns it, otherwise it just returns the name.

<pre class="code"><span style="color:blue;">let </span>stringTokens =
    Map.ofList [
        <span style="color:maroon;">"Def"</span>, Def
    ]</pre>

<pre class="code"><span style="color:blue;">let </span>matchString chars =
    <span style="color:blue;">let </span>value, remainingChars = matchSeriesOfChars isNameChar chars
    <span style="color:blue;">let </span>specialString = Map.tryFind value stringTokens
    <span style="color:blue;">if </span>specialString.IsSome
        <span style="color:blue;">then </span>specialString.Value, remainingChars
        <span style="color:blue;">else </span>Name(value), remainingChars</pre>

And we are done with the lexer, all of 100+ lines of it …