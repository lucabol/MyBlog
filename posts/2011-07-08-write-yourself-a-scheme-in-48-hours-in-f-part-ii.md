---
id: 42
title: 'Write Yourself a Scheme in 48 Hours in F# – Part II'
date: 2011-07-08T07:01:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/07/09/write-yourself-a-scheme-in-48-hours-in-f-part-ii/
categories:
  - fsharp
tags:
  - fsharp
  - Lambda expressions
  - Parsing
---
Usually, when I do blog posts that are all about code, I write them ‘bottom up’. I start talking about the most primitive types and functions and build up from there toward higher abstractions. I think this is a pretty common way of doing it.

For this series I’m going to try the opposite. I start with the code that creates the REPL window and move down from there toward the guts of the interpreter. I hold the opinion that, if the code is written right, this should be ok. The naming scheme and general structure of it should allow understanding it at different levels.

Or at least I hope so.

Let’s start from the _main_ function. Depending on the number of arguments it either runs the REPL window or executes whatever is in the file passed in as the first argument using the other arguments as parameters.

<pre class="code">[&lt;EntryPoint&gt;]
<span style="color:blue;">let </span>main(args: string[]) =
    <span style="color:blue;">match </span>Array.toList args <span style="color:blue;">with
    </span>| [] <span style="color:blue;">-&gt; </span>runRepl ()
    | filename :: args <span style="color:blue;">-&gt; </span>runOne filename args
    0</pre>

The latter case is coded in the below function. It first load all the primitive operators (i.e. ‘+’, ‘-‘ etc…) and the standard library. The word ‘load’ above is a little misleading. In reality it adds them to the environment. It then proceeds to add the arguments that were passed on. As the last step, it evaluates the ‘load’ command by using the newly created environment, it transforms the returned token to a string and prints it.

<pre class="code"><span style="color:blue;">let </span>runOne (filename : string) (args : list&lt;string&gt;) =
    <span style="color:blue;">let </span>env = primitiveBindings ()
                |&gt; loadStdLib
                |&gt; bindVars [ <span style="color:maroon;">"args"</span>, List (List.map String args) ]
    List [Atom <span style="color:maroon;">"load"</span>; String filename] |&gt; eval env |&gt; showVal |&gt; printStr</pre>

Running the REPL windows is equally simple. Load the primitive operators and the standard library, show a prompt and evaluate the input until the input is ‘Quit’.

<pre class="code"><span style="color:blue;">let </span>runRepl () =
    <span style="color:blue;">let </span>env = primitiveBindings () |&gt; loadStdLib
    until (<span style="color:blue;">fun </span>s <span style="color:blue;">-&gt; </span>s = <span style="color:maroon;">"Quit" </span>|| s = <span style="color:maroon;">"quit"</span>) (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt; </span>readPrompt <span style="color:maroon;">"Lisp&gt;&gt;&gt; "</span>) (evalAndPrint env)</pre>

_readPrompt_ is pretty simple:

<pre class="code"><span style="color:blue;">let </span>printStr (s: string) = Console.Write(s)
<span style="color:blue;">let </span>readPrompt (s: string) = printStr s ; Console.ReadLine ()</pre>

_EvalAndPrint_ is written as a chain of functions (lookup the ‘>>’ operator in F#) and just evaluate the string, transform the result to a string, prints it and newline it.

<pre class="code"><span style="color:blue;">let </span>newLine () = Console.WriteLine()
<span style="color:blue;">let </span>evalAndPrint env = evalString env &gt;&gt; showVal &gt;&gt; printStr &gt;&gt; newLine</pre>

_evalString_ parses the string and evaluates the expression. Note the exception management. This is a result of my decision of throwing an exception every time something goes wrong instead of using a monad to pass the state around. I think it is pretty clear, but haskellers might disagre. This is one of the main differences from the Haskell version.

<pre class="code"><span style="color:blue;">let </span>evalString env expr =
    <span style="color:blue;">try
        </span>expr |&gt; readExpr |&gt; eval env
    <span style="color:blue;">with
    </span>| LispException(error) <span style="color:blue;">-&gt; </span>String (showError error)</pre>

For the sake of completeness, here is _until_. Maybe there is a library function somewhere that I could have used?

<pre class="code"><span style="color:blue;">let rec </span>until pred prompter evaluator =
    <span style="color:blue;">let </span>result = prompter ()
    <span style="color:blue;">if </span>not (pred result) <span style="color:blue;">then
        </span>evaluator result
        until pred prompter evaluator</pre>

Back on the main flow of the code, _loadStdLib_ just loads the standard file and returns the populated environment.

<pre class="code"><span style="color:blue;">let </span>loadStdLib env =
    eval env (List [Atom <span style="color:maroon;">"load"</span>; String <span style="color:maroon;">"stdlib.scm"</span>]) |&gt; ignore
    env</pre>

primitiveBindings creates a new empty environment and adds a bunch of pairs (primitiveName, LispVal –> LispVal). LispVal is a representation of a Scheme expression, so the second part of the tuple is simply a reduction from one expression to another (hopefully simpler in some sense). We’ll talk more about LispVal in upcoming posts.

<pre class="code"><span style="color:blue;">let </span>primitiveBindings () =
    (nullEnv ()) |&gt; bindVars [ <span style="color:blue;">for </span>v, f <span style="color:blue;">in </span>primitives <span style="color:blue;">-&gt; </span>v, PrimitiveFunc f ] </pre>

There you have it. That’s the full implementation for the REPL window. Next post, we’ll look at LispEval and the evaluator.