---
id: 71
title: 'Adventure in parserland – parsing lambda expressions in F# – Part IV'
date: 2011-09-09T06:09:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/09/09/adventure-in-parserland-parsing-lambda-expressions-in-f-part-iv/
permalink: /2011/09/09/adventure-in-parserland-parsing-lambda-expressions-in-f-part-iv/
categories:
  - 'F#'
---
Let’ now look at the parser. First let’s review the grammar:

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

And the data type to represent it:

<pre class="code"><span style="color:blue;">type </span>Name = string
<span style="color:blue;">and </span>Body = Expression
<span style="color:blue;">and </span>Function = Name * Expression
<span style="color:blue;">and </span>FunctionExpression = Expression
<span style="color:blue;">and </span>ArgumentExpression = Expression
<span style="color:blue;">and </span>Expression =
| EName <span style="color:blue;">of </span>string
| Function <span style="color:blue;">of </span>Expression * Body
| Application <span style="color:blue;">of </span>FunctionExpression * ArgumentExpression
| EOT</pre>

In essence, the data type need to store all the information needed for subsequent stages of computation (i.e. beta reductions and such). The closer it is to the grammar, the better. In this case it looks pretty close.

Remember what is the main goal of our parser:

<pre class="code"><span style="color:blue;">let </span>parseTextReader: TextReader <span style="color:blue;">-&gt; </span>seq&lt;Expression&gt; =
                    textReaderToLazyList &gt;&gt; tokenStream &gt;&gt; parseExpressions</pre>

We have already looked at _TextReaderToLazyList_ and _tokenStream_. Now it is the time to look at _parseExpressions_. It’s goal is to&#160; parse the _LazyList<Token>_ and return a sequence of expressions. The choice of returning a sequence at this point is to make the _parseTextReader_, which is the main function in the program, return a more ‘standard’ type.

<pre class="code"><span style="color:blue;">and </span>parseExpressions tokens = seq {
   <span style="color:blue;">let </span>tokens = parseOptionalWs tokens
   <span style="color:blue;">let </span>expr, tokens = parseExpr tokens
   <span style="color:blue;">let </span>tokens = parseOptionalWs tokens
   <span style="color:blue;">match </span>expr <span style="color:blue;">with
    </span>| EOT   <span style="color:blue;">-&gt; yield </span>EOT
    | exp   <span style="color:blue;">-&gt; yield </span>exp; <span style="color:blue;">yield! </span>parseExpressions tokens }</pre>

_parseOtionalWs_ simply skips ahead whatever whitespaces it finds.

<pre class="code"><span style="color:blue;">and </span>parseOptionalWs tokens = <span style="color:blue;">match </span>tokens <span style="color:blue;">with
                                </span>| LazyList.Nil <span style="color:blue;">-&gt; </span>LazyList.empty
                                | LazyList.Cons(h, t) <span style="color:blue;">-&gt;
                                    match </span>h <span style="color:blue;">with
                                       </span>| Ws _ <span style="color:blue;">-&gt; </span>parseOptionalWs t
                                       | _ <span style="color:blue;">-&gt; </span>tokens</pre>

_parseExpr_ is more interesting. It is the main switch that creates expression kinds.

<pre class="code"><span style="color:blue;">let rec </span>parseExpr tokens = <span style="color:blue;">match </span>tokens <span style="color:blue;">with
                            </span>| LazyList.Nil <span style="color:blue;">-&gt; </span>EOT, LazyList.empty
                            | LazyList.Cons(h, t) <span style="color:blue;">-&gt;
                                match </span>h <span style="color:blue;">with
                                    </span>| EOF <span style="color:blue;">-&gt; </span>parseEOF tokens
                                    | Name _ <span style="color:blue;">-&gt; </span>parseName  tokens
                                    | Lambda <span style="color:blue;">-&gt; </span>parseFunction tokens
                                    | OpenParens <span style="color:blue;">-&gt; </span>parseApplication tokens
                                    | token <span style="color:blue;">-&gt; </span>errorAtStart <span style="color:maroon;">"Expression" </span>token</pre>

_parseEOF_ is not.

<pre class="code"><span style="color:blue;">and </span>parseEOF tokens = EOT, LazyList.empty</pre>

_parseName_ just returns a _EName_, unwrapping it from Name.

<pre class="code"><span style="color:blue;">and </span>parseName tokens = EName (head tokens |&gt; unwrapName), tail tokens</pre>

Unwrap just unwraps it.

<pre class="code"><span style="color:blue;">let </span>unwrapName = <span style="color:blue;">function
    </span>| Name(s) <span style="color:blue;">-&gt; </span>s
    | tok <span style="color:blue;">-&gt; </span>errorExpecting <span style="color:maroon;">"a Name" </span>&lt;| writeToken tok</pre>

_parseFunction_ just conumes a Lambda, a name, a Dot token, a body (i.e. \x.x)and assembles them in a Function:

<pre class="code"><span style="color:blue;">and </span>parseFunction tokens =
    <span style="color:blue;">let </span>tokens = consumeToken Lambda tokens
    <span style="color:blue;">let </span>name, tokens = parseName tokens
    <span style="color:blue;">let </span>tokens = consumeToken Dot tokens
    <span style="color:blue;">let </span>body, tokens = parseExpr tokens
    Function(name, body), tokens</pre>

_consumeToken_ tries to consume a token generating an error if it doesn’t find it:

<pre class="code"><span style="color:blue;">let </span>consumeToken token =
    genericConsumeToken (<span style="color:blue;">fun </span>token' _ <span style="color:blue;">-&gt; </span>errorExpecting (writeToken token') (writeToken token)) token</pre>

_genericConsumeToken_ is just a generalization of the function above:

<pre class="code"><span style="color:blue;">let </span>genericConsumeToken noMatch token = <span style="color:blue;">function
    </span>| LazyList.Nil <span style="color:blue;">-&gt; </span>LazyList.empty
    | LazyList.Cons(h, t) <span style="color:blue;">as </span>originalTokens <span style="color:blue;">-&gt;
        match </span>h <span style="color:blue;">with
        </span>| tok <span style="color:blue;">when </span>tok = token <span style="color:blue;">-&gt; </span>t
        | tok <span style="color:blue;">-&gt; </span>noMatch token originalTokens</pre>



The last thing left to consume is an application which is in this form (func args):

<pre class="code"><span style="color:blue;">and </span>parseApplication tokens =
    <span style="color:blue;">let </span>tokens = consumeToken OpenParens tokens
    <span style="color:blue;">let </span>funExpr, tokens = parseExpr tokens
    <span style="color:blue;">let </span>tokens = parseOptionalWs tokens
    <span style="color:blue;">let </span>argExpr, tokens = parseExpr tokens
    <span style="color:blue;">let </span>tokens = consumeToken CloseParens tokens
    Application(funExpr, argExpr), tokens</pre>

Various error and utility functions are defined below:

<pre class="code"><span style="color:blue;">let </span>errorEOF expecting = failwith  (<span style="color:maroon;">"Expected " </span>+ expecting + <span style="color:maroon;">", got EOF"</span>)
<span style="color:blue;">let </span>errorExpecting expecting gotToken = failwith (<span style="color:maroon;">"Expected " </span>+ expecting + <span style="color:maroon;">", got" </span>+ gotToken)
<span style="color:blue;">let </span>errorAtStart expecting gotToken = failwith (<span style="color:maroon;">"Expected " </span>+ expecting + <span style="color:maroon;">" which cannot start with" </span>+ writeToken gotToken)
<span style="color:blue;">let </span>tail = LazyList.tail
<span style="color:blue;">let </span>head = LazyList.head</pre>



And that is the parser. All 100+ lines of it. As you can tell it is rather formulaic to go from a grammar to a lexer and a parser, which is why you shouldn’t do it, but instead let a tool generate the code for you given the grammar or use FParsec.

We have written 200+ code and I don’t think we can be too proud of our achievement. It is:

  * Certainly buggy
  * Primitive in error handling
  * Not tail recursive (big text is likely to blow up our stack)
  * Probably inefficient

So let’s look next at a better way to do it.