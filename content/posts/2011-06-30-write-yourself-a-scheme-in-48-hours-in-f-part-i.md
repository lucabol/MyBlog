---
id: 39
title: 'Write Yourself a Scheme in 48 Hours in F# – Part I'
date: 2011-06-30T15:41:12+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/06/30/write-yourself-a-scheme-in-48-hours-in-f-part-i/
permalink: /2011/06/30/write-yourself-a-scheme-in-48-hours-in-f-part-i/
categories:
  - 'F#'
---
Hi, I’m back. I’ve finally sorted out the guidelines for blogging in Credit Suisse. 

Here is something I have been playing around with in the spare time between one meeting and the next one.&#160; It is a Scheme interpreter that includes a REPL window. The full code is [here](http://code.msdn.microsoft.com/Write-Yourself-a-Scheme-in-d50ae449).

All the smarts for it come from [this Wiki Book](http://en.wikibooks.org/wiki/Write_Yourself_a_Scheme_in_48_Hours). I just ported the code to F# (and modified it a bit). I thought the comparison might be interesting, so here we go. Thanks to [Tobias](http://gedell.net/) and [Jose](http://www.haskellers.com/user/pepeiborra) for reviewing the code, find one bug and suggest improvements.

Before we start looking at the real code, here is what we are trying to accomplish in form of test cases. If you are a bit rusty on LISP syntax, you might want to try and see if you understand what it does.

Our goal is to make all this XUnit test cases pass. Each of the lists below contains the Scheme statement and the result to display in the REPL window.</p> 

<pre class="code"><span style="color:blue;">open </span>Xunit
<span style="color:blue;">open </span>Lisp.Repl
<span style="color:blue;">open </span>Lisp.Parser
<span style="color:blue;">open </span>Lisp.SymbolTable
<span style="color:blue;">let </span>eval env = evalString env &gt;&gt; showVal
<span style="color:blue;">let </span>initEnv () = primitiveBindings () |&gt; loadStdLib
<span style="color:blue;">let </span>test tests =
    <span style="color:blue;">let </span>env = initEnv ()
    tests |&gt; List.iter (<span style="color:blue;">fun </span>(expr, result) <span style="color:blue;">-&gt; </span>Assert.Equal(result, eval env expr))
[&lt;Fact&gt;]
<span style="color:blue;">let </span>simpleEval() =
    <span style="color:blue;">let </span>tests = [
        <span style="color:maroon;">"(+ 2 2)"</span>, <span style="color:maroon;">"4"
        "(+ 2 (- 4 1))"</span>, <span style="color:maroon;">"5"
        "(- (+ 4 6 3) 3 5 2)"</span>, <span style="color:maroon;">"3"
    </span>]
    test tests
[&lt;Fact&gt;]
<span style="color:blue;">let </span>errorCheck() =
    <span style="color:blue;">let </span>tests = [
         <span style="color:maroon;">"(+ 2 \"two\")"</span>, <span style="color:maroon;">"\"Invalid type: expected number, found \"two\"\""
         "(+ 2)"</span>, <span style="color:maroon;">"\"Expected 2 args; found values 2\""
         "(what? 2)"</span>, <span style="color:maroon;">"\"Getting an unbound variable: what?\""
         </span>]
    test tests
[&lt;Fact&gt;]
<span style="color:blue;">let </span>moreEval() =
    <span style="color:blue;">let </span>tests = [
         <span style="color:maroon;">"(&lt; 2 3)"</span>, <span style="color:maroon;">"#t"
         "(&gt; 2 3)"</span>, <span style="color:maroon;">"#f"
         "(&gt;= 3 3)"</span>, <span style="color:maroon;">"#t"
         "(string=? \"test\" \"test\")"</span>, <span style="color:maroon;">"#t"
         "(string=? \"abcd\" \"dsft\")"</span>, <span style="color:maroon;">"#f"
         "(if (&gt; 2 3) \"no\" \"yes\")"</span>, <span style="color:maroon;">"\"yes\""
         "(if (= 3 3) (+ 2 3 (- 5 1)) \"unequal\")"</span>, <span style="color:maroon;">"9"
         "(cdr '(a simple test))"</span>, <span style="color:maroon;">"(simple test)"
         "(car (cdr '(a simple test)))"</span>, <span style="color:maroon;">"simple"
         "(car '((this is) a test))"</span>, <span style="color:maroon;">"(this is)"
         "(cons '(this is) 'test)"</span>, <span style="color:maroon;">"((this is) . test)"
         "(cons '(this is) '())"</span>, <span style="color:maroon;">"((this is))"
         "(eqv? 1 3)"</span>, <span style="color:maroon;">"#f"
         "(eqv? 3 3)"</span>, <span style="color:maroon;">"#t"
         "(eqv? 'atom 'atom)"</span>, <span style="color:maroon;">"#t"
         </span>]
    test tests
[&lt;Fact&gt;]
<span style="color:blue;">let </span>assignement() =
    <span style="color:blue;">let </span>tests = [
        <span style="color:maroon;">"(define x 3)"</span>, <span style="color:maroon;">"3"
        "(+ x 2)"</span>, <span style="color:maroon;">"5"
        "(+ y 2)"</span>, <span style="color:maroon;">"\"Getting an unbound variable: y\""
        "(define y 5)"</span>, <span style="color:maroon;">"5"
        "(+ x (- y 2))"</span>, <span style="color:maroon;">"6"
        "(define str \"A string\")"</span>, <span style="color:maroon;">"\"A string\""
        "(&lt; str \"The string\")"</span>, <span style="color:maroon;">"\"Invalid type: expected number, found \"A string\"\""
        "(string&lt;? str \"The string\")"</span>, <span style="color:maroon;">"#t"
         </span>]
    test tests
[&lt;Fact&gt;]
<span style="color:blue;">let </span>closure() =
    <span style="color:blue;">let </span>tests = [
        <span style="color:maroon;">"(define (f x y) (+ x y))"</span>, <span style="color:maroon;">"(lambda (\"x\" \"y\") ...)"
        "(f 1 2)"</span>, <span style="color:maroon;">"3"
        "(f 1 2 3)"</span>, <span style="color:maroon;">"\"Expected 2 args; found values 1 2 3\""
        "(define (factorial x) (if (= x 1) 1 (* x (factorial (- x 1)))))"</span>, <span style="color:maroon;">"(lambda (\"x\") ...)"
        "(factorial 10)"</span>, <span style="color:maroon;">"3628800"
        "(define (counter inc) (lambda (x) (set! inc (+ x inc)) inc))"</span>, <span style="color:maroon;">"(lambda (\"inc\") ...)"
        "(define my-count (counter 5))"</span>, <span style="color:maroon;">"(lambda (\"x\") ...)"
        "(my-count 3)"</span>, <span style="color:maroon;">"8"
        "(my-count 6)"</span>, <span style="color:maroon;">"14"
        "(my-count 5)"</span>, <span style="color:maroon;">"19"
         </span>]
    test tests
[&lt;Fact&gt;]
<span style="color:blue;">let </span>predefinedFunctions() =
    <span style="color:blue;">let </span>tests = [
        <span style="color:maroon;">"(map (curry + 2) '(1 2 3 4))"</span>, <span style="color:maroon;">"(3 4 5 6)"
        "(filter even? '(1 2 3 4))"</span>, <span style="color:maroon;">"(2 4)"
        </span>]
    test tests
[&lt;Fact&gt;]
<span style="color:blue;">let </span>varargsCountCheck() =
    <span style="color:blue;">let </span>tests = [
        <span style="color:maroon;">"(define (sum x y . lst) (fold + (* x y) lst))"</span>, <span style="color:maroon;">"(lambda (\"x\" \"y\" . lst) ...)"
        "(sum 1 2 3)"</span>, <span style="color:maroon;">"5"
        "(sum 1 1 1)"</span>, <span style="color:maroon;">"2"
        "(sum 1 2)"</span>, <span style="color:maroon;">"2"
        "(sum 1)"</span>, <span style="color:maroon;">"\"Expected 2 args; found values 1\""
         </span>]
    test tests</pre>

