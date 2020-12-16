---
id: 67
title: 'Adventure in parserland – parsing lambda expressions in F# – Part II'
date: 2011-08-26T14:25:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/08/26/adventure-in-parserland-parsing-lambda-expressions-in-f-part-ii/
categories:
  - fsharp
tags:
  - fsharp
  - Lambda expressions
  - Parsing
---
The parser starts simple with the following two functions to parse either a string or a file. I use the XXX_Readers_ because I want to lazy read character by character.

<pre class="code"><span style="color:blue;">let </span>parseString s =
    <span style="color:blue;">let </span>reader = <span style="color:blue;">new </span>StringReader(s)
    parseTextReader reader
<span style="color:blue;">let </span>parseFile fileName =
    <span style="color:blue;">let </span>reader = <span style="color:blue;">new </span>StreamReader(fileName: string)
    parseTextReader reader</pre>

The whole parser is in the following two lines:

<pre class="code"><span style="color:blue;">let </span>parseTextReader: TextReader <span style="color:blue;">-&gt; </span>seq&lt;Expression&gt; =
                    textReaderToLazyList &gt;&gt; tokenStream &gt;&gt; parseExpressions</pre>

I need to specify the signature otherwise the compiler gets confused : wait, does it take a StringReader or a StreamReader? You better tell me!

The function is a composite of three functions applied in sequence:

  1. Translate a TextReader to a LazyList<char> 
  2. Translate a LazyList<char> to a LazyList<Token> (lexer) 
  3. Translate a LazyList<Token> to a LazyList<Expression> (parser) 

My usage of _LazyList_ as the workhorse for the program is because I want to match on the head of the stream of chars/tokens in a lazy way.

I love it when a program naturally decomposes in such simple understandable pieces. I impute some of that to functional programming. For one reason or another, in my 15+ years of object oriented programming, I’ve rarely got to the core of a problem with such immediacy.

A sequence of operations likes the above would be lost in a protected overridden implementation of a base class somewhere (or something else equally long to pronounce). The beauty would be lost somewhere in the vast machinery required to support it.

In any case, _TextReaderToLazyList_ is a trivial generator function that uses the unfold function of LazyList to read a character at the time.

<pre class="code"><span style="color:blue;">let </span>textReaderToLazyList textReader = LazyList.unfold (<span style="color:blue;">fun </span>(ts:TextReader) <span style="color:blue;">-&gt;
    let </span>ch = ts.Read()
    <span style="color:blue;">if </span>ch = -1 <span style="color:blue;">then </span>None <span style="color:blue;">else </span>Some(char ch, ts)) textReader</pre>

The next step is to look at either the lexer, going bottom up, or the parser, going top down.