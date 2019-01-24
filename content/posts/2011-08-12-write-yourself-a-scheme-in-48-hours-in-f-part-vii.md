---
id: 55
title: 'Write Yourself a Scheme in 48 Hours in F# – Part VII'
date: 2011-08-12T07:11:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/08/12/write-yourself-a-scheme-in-48-hours-in-f-part-vii/
permalink: /2011/08/12/write-yourself-a-scheme-in-48-hours-in-f-part-vii/
categories:
  - 'F#'
tags:
  - 'F#'
  - Lambda expressions
  - Parsing
---
Let’s talk about the environment now.&#160; This is the part of the interpreter that I like the least. It is a global variable and it contains a list of&#160; (string, LispVal) where the LispVal is mutable.

<pre class="code"><span style="color:blue;">type </span>Env = (string * LispVal ref) list ref</pre>

This is pretty bad. First of all, it immediately cuts off any option of running interpreters in different threads. Moreover, it makes a lot of functions in the evaluator to have side effects. That makes it much harder to reason about them.

In a world where I am provided with infinite time and energy, I would change it. In this world, I won’t. If you try your hand at doing it, make sure that you pass all the testcases before declaring victory. The scope rules of Scheme are not all that obvious. A code reviewer called them the Italian scoping rules because he thought I got them wrong …

In any case, there isn’t much to the symbol table management.&#160; You can create an empty one:

<pre class="code"><span style="color:blue;">let </span>nullEnv (): Env = ref List.empty</pre>

Check if a variable is bound:

<pre class="code"><span style="color:blue;">let </span>keyEq name (k, _) = name = k
<span style="color:blue;">let </span>isBound var (env: Env) = !env |&gt; List.exists (keyEq var)</pre>

Get a variable out:

<pre class="code"><span style="color:blue;">let </span>getVar var (env: Env) =
    <span style="color:blue;">let </span>result = !env |&gt; List.tryFind (keyEq var)
    <span style="color:blue;">match </span>result <span style="color:blue;">with
    </span>| None <span style="color:blue;">-&gt; </span>throw (UnboundVar(<span style="color:maroon;">"Getting an unbound variable: " </span>, var))
    | Some(_, r) <span style="color:blue;">-&gt; </span>!r</pre>

Set the value of an existing variable:

<pre class="code"><span style="color:blue;">let </span>setVar var value (env:Env) =
    <span style="color:blue;">let </span>result = !env |&gt; List.tryFind (keyEq var)
    <span style="color:blue;">match </span>result <span style="color:blue;">with
    </span>| Some(_, v) <span style="color:blue;">-&gt; </span>v := value ; value
    | None <span style="color:blue;">-&gt; </span>throw (UnboundVar(<span style="color:maroon;">"Setting an unbound variable: " </span>, var))</pre>

Or define a new variable in the environment. Note that if the variable already exist, its value gets set.

<pre class="code"><span style="color:blue;">let </span>define (env:Env) var value =
    <span style="color:blue;">let </span>result = !env |&gt; List.tryFind (keyEq var)
    <span style="color:blue;">match </span>result <span style="color:blue;">with
    </span>| Some(_, v) <span style="color:blue;">-&gt; </span>v := value ; value
    | None <span style="color:blue;">-&gt;
        </span>env := [var, ref value] @ !env; value</pre>

<pre class="code"><font face="Lucida Sans Unicode">You can also bind a list of (string, LispVal) to the environment by prepending it to the existing ones:</font></pre>

<pre class="code"><span style="color:blue;">let </span>bindVars bindings (env:Env) =
   ref ((bindings |&gt; List.map (<span style="color:blue;">fun </span>(n, v) <span style="color:blue;">-&gt; </span>n , ref v)) @ !env)</pre>

Once you accept the evil of the global mutable variable scheme, these functions are easy enough.

The only piece left is error management. This is where my implementation differs from the Haskell version the most. In essence, I throw exception and catch them to report errors, while the Haskell version uses a monad to propagate the error information.

I have a _LispError_ that represents everything that can go wrong:

<pre class="code"><span style="color:blue;">type </span>LispError =
    | NumArgs <span style="color:blue;">of </span>int * LispVal list
    | TypeMismatch <span style="color:blue;">of </span>string * LispVal
    | ParseError <span style="color:blue;">of </span>string * FParsec.Error.ParserError
    | BadSpecialForm <span style="color:blue;">of </span>string * LispVal
    | NotFunction <span style="color:blue;">of </span>string * string
    | UnboundVar <span style="color:blue;">of </span>string * string
    | Default <span style="color:blue;">of </span>string
    | IOError <span style="color:blue;">of </span>string</pre>

I wrap it in an exception:

<pre class="code"><span style="color:blue;">exception </span>LispException <span style="color:blue;">of </span>LispError</pre>

This is what I throw in various places in the code.

<pre class="code"><span style="color:blue;">let </span>throw le = raise (LispException(le))</pre>



I then catch it at the outer layer:

<pre class="code"><span style="color:blue;">let </span>evalString env expr =
    <span style="color:blue;">try
        </span>expr |&gt; readExpr |&gt; eval env
    <span style="color:blue;">with
    </span>| LispException(error) <span style="color:blue;">-&gt; </span>String (showError error)</pre>

And display the error by using the below function:

<pre class="code"><span style="color:blue;">let </span>showError = <span style="color:blue;">function
    </span>| NumArgs(expected, found) <span style="color:blue;">-&gt; </span><span style="color:maroon;">"Expected " </span>+ expected.ToString() + <span style="color:maroon;">" args; found values " </span>+ unwordsList found
    | TypeMismatch(expected, found) <span style="color:blue;">-&gt; </span><span style="color:maroon;">"Invalid type: expected " </span>+ expected + <span style="color:maroon;">", found " </span>+ showVal found
    | ParseError(msg, _) <span style="color:blue;">-&gt; </span><span style="color:maroon;">"Parse Errror" </span>+ msg
    | BadSpecialForm(message, form) <span style="color:blue;">-&gt; </span>message + showVal form
    | NotFunction(message, func) <span style="color:blue;">-&gt; </span>message + func
    | UnboundVar(message, varName) <span style="color:blue;">-&gt; </span>message + varName
    | Default(message) <span style="color:blue;">-&gt; </span>message
    | IOError(message) <span style="color:blue;">-&gt; </span>message</pre>



And that’s all there is to it. I hope you guys and gals enjoyed this seven part extravagance. Cheers.