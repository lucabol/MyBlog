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
This is part of my ‘things that I do in the empty spaces between one meeting and the next one, which might end up being vaguely interesting’. It is a lambda expression parser.

The full source code is [here](http://code.msdn.microsoft.com/Parsing-Lambda-Expressions-7ad5271f).

I actually have two versions of it: one written longhand and the other one written with [FParsec](http://www.quanttec.com/fparsec/about/fparsec-vs-alternatives.html). Just to be clear: I’m no expert of either.

And just to be more clear: I think writing most parsers longhand in the way I am about to show is crazy. You either use FParsec or&#160; [fslex / fsyacc](http://blogs.msdn.com/b/jomo_fisher/archive/2010/06/15/use-fslex-and-fsyacc-to-make-a-parser-in-f.aspx).

I have a strong distaste for additional compilation steps. I think it lingers on from MFC project types of 15/20 years ago. I was one of these crazy folks that would generate the project, wrap the generated code (with some generalizations) in my own library and use that one from then on.

So I prefer FParsec. I’m ok rewriting [left recursive](http://en.wikipedia.org/wiki/Left_recursion) rules and its performance has never been a problem for me. [Here](http://www.quanttec.com/fparsec/about/fparsec-vs-alternatives.html) is a table that compares the different approaches.

But I started wondering about coding a a recursive descent parser for a simple grammar by hand, fully knowing the foolishness of the idea. Thanks to [Jose](http://www.haskellers.com/user/pepeiborra) for code reviewing it.

The inspiration for the grammar comes from [this book](http://www.google.co.uk/url?sa=t&source=web&cd=4&ved=0CDgQFjAD&url=http%3A%2F%2Fwww.amazon.com%2FIntroduction-Functional-Programming-Calculus-International%2Fdp%2F0201178125&ei=KoklTqzjF4GWhQf-w5XlCQ&usg=AFQjCNGPzv_27nSNwctaEykBivq3N-I7Dg&sig2=4iLu_nZnd8GlwPXpt8crMg).

<pre class="code"><span style="color:green;">(*
        &lt;expression&gt; ::= &lt;name&gt; | &lt;function&gt; | &lt;application&gt;
        &lt;name&gt; ::= non­blank character sequence
        &lt;function&gt; ::= \ &lt;name&gt; . &lt;body&gt;
        &lt;body&gt; ::= &lt;expression&gt;
        &lt;application&gt; ::= ( &lt;function expression&gt; &lt;argument expression&gt; )
        &lt;function expression&gt; ::= &lt;expression&gt;
        &lt;argument expression&gt; ::= &lt;expression&gt;
    *)
</span></pre>

In English, an expression is either a name, a function or an application. A name is a bunch of characters (better defined in the code). A function is ‘\’, a name, ‘.’ and an expression. An application is ‘(‘, an expression, whitespaces, an expression and ‘)’.

Some testcases for the above grammar and the parsers written to parse it are below. It should be intuitive what this code does just by the name of the functions. Even it isn’t, check that the expressions symbol contains valid productions from the grammar above.

<pre class="code"><span style="color:blue;">module </span>Test
<span style="color:blue;">open </span>Microsoft.FSharp.Collections
<span style="color:blue;">open </span>Xunit
<span style="color:blue;">open </span>LambdaEngine
<span style="color:blue;">open </span>Parser
<span style="color:blue;">open </span>Lexer
<span style="color:blue;">open </span>FParser
<span style="color:blue;">let </span>writeTokenStream stream = Seq.fold (<span style="color:blue;">fun </span>acc token <span style="color:blue;">-&gt; </span>acc + writeToken token) <span style="color:maroon;">"" </span>stream
<span style="color:blue;">let rec </span>writeExpr = <span style="color:blue;">function
        </span>| EName(s) <span style="color:blue;">-&gt; </span>s
        | Function(expr, body) <span style="color:blue;">-&gt; </span>writeToken Lambda + writeExpr expr + writeToken Dot + writeExpr body
        | Application(funExpr, argExpr) <span style="color:blue;">-&gt; </span>writeToken OpenParens + writeExpr funExpr + writeToken (Ws(<span style="color:maroon;">" "</span>))
                                            + writeExpr argExpr + writeToken CloseParens
        | EOT <span style="color:blue;">-&gt; </span><span style="color:maroon;">""
</span><span style="color:blue;">let </span>tokenStreams = [
    <span style="color:maroon;">""
    "(\xs.xs \y.(y \x.y))"
    "(\xst.xst \y.(y  \x.y))"
    " "
    "x"
    "(x y)"
    </span>]
<span style="color:blue;">let </span>expressions = [
    <span style="color:maroon;">""
    "(\x.x \y.(y \x.y))"
    "x"
    "(x y)"
    </span>]
<span style="color:blue;">let </span>stringToCharList s =
    <span style="color:blue;">let </span>textReader = <span style="color:blue;">new </span>System.IO.StringReader(s)
    textReaderToLazyList textReader
[&lt;Fact&gt;]
<span style="color:blue;">let </span>testTokenizer () =
    <span style="color:blue;">let </span>testTokenStream s =
        <span style="color:blue;">let </span>stream = tokenStream &lt;| stringToCharList s
        <span style="color:blue;">let </span>s1 = writeTokenStream stream
        Assert.Equal(s, s1)
    tokenStreams |&gt; List.iter testTokenStream
<span style="color:blue;">let </span>testExpr parseFunction s =
    <span style="color:blue;">let </span>exprs = parseFunction s
    <span style="color:blue;">let </span>s1 = exprs |&gt; Seq.fold (<span style="color:blue;">fun </span>s expr <span style="color:blue;">-&gt; </span>s + writeExpr expr) <span style="color:maroon;">""
    </span>Assert.Equal(s, s1)
[&lt;Fact&gt;]
<span style="color:blue;">let </span>testParser () = expressions |&gt; List.iter (testExpr parseString)
[&lt;Fact&gt;]
<span style="color:blue;">let </span>testFParser () = expressions |&gt; List.iter (testExpr fparseString)</pre>

In the next instalment, we’ll start looking at the real code for the parser.