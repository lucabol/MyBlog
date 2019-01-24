---
id: 44
title: 'Write Yourself a Scheme in 48 Hours in F# – Part III'
date: 2011-07-15T07:12:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/07/16/write-yourself-a-scheme-in-48-hours-in-f-part-iii/
permalink: /2011/07/15/write-yourself-a-scheme-in-48-hours-in-f-part-iii/
categories:
  - 'F#'
tags:
  - 'F#'
  - Lambda expressions
  - Parsing
---
Very often my code ends up having the following form: parse an input to create an intermediate data structure and evaluate the structure to produce an output. Strangely, many years ago, when my code was object oriented, that wasn’t the case. Or at least I wasn’t explicitly aware of it.

When you write an interpreter or a compiler, things always work out like that, but I see the same pattern in almost everything I produce: from financial backtesting to chart libraries. Sometimes when, out of laziness or stupidity, I forego the intermediate structure, I end up in the end having to retrofit it in. Simply processing input and generating output at the same time rarely cuts it. But it is tempting because you get going pretty fast and I’m tricked into it occasionally.

Hence the first thing that I find myself reasoning about is often the particular form of such intermediate structure. In this case it looks like the following:

<pre class="code"><span style="color:blue;">type </span>Env = (string * LispVal ref) list ref
<span style="color:blue;">and </span>FuncRecord = { parms: string list; varargs: string option; body: LispVal list; closure: Env}
<span style="color:blue;">and </span>LispVal =
    | Atom <span style="color:blue;">of </span>string
    | List <span style="color:blue;">of </span>LispVal list
    | DottedList <span style="color:blue;">of </span>LispVal list * LispVal
    | Number <span style="color:blue;">of </span>int
    | String <span style="color:blue;">of </span>string
    | Bool <span style="color:blue;">of </span>bool
    | PrimitiveFunc <span style="color:blue;">of </span>(LispVal list <span style="color:blue;">-&gt; </span>LispVal)
    | Func <span style="color:blue;">of </span>FuncRecord
    | Port <span style="color:blue;">of </span>System.IO.FileStream</pre>

This _LispVal_ structure has one constructor for each kind of expression (production) that is allowed in Scheme. Or at least that ones I support …

It is important that each one stores all the information that is necessary for the evaluator to evaluate the expression. No more, no less. Here is a brief description:

  * **Atom**: it is a kind of a constant in Scheme. This is probably the worst definition ever given for it. Please read about it in your little schemer book.
  * **List**: is the main Scheme type. It represents a list of expressions.
  * **DottedList**: this is the bizarre Scheme way to pass optional parameters
  * **Number**: is a number 🙂 You will discover which kind of number when we talk about the parser
  * **String** : is a string
  * **Bool**: #t, #f
  * **PrimitiveFunc**: is the representation for the primitive operators/functions that are burned into the interpreter. It is just a function that takes a list of LispVal and returns a LispVal
  * **Func**: is a user defined function. Notice that the body of it is simply a list of LispVal. This is why LISP is so powerful. Also notice that a closure gets passed to it for the ‘captured’ variables.
  * **Port**: is a slightly goofy representation of an in/out stream
  * Anything else (i.e. macros) is not supported, but this would be the first piece to change if they were.

The only remaining code to address is: 

<span style="color:blue;">type </span>Env = (string * LispVal ref) list ref 

This is the symbol table and it is ugly. It is not multithread safe either. But it works and it is close enough to the Haskell version so I decided to retain it. A proper code review would ‘strongly suggest’ rewriting the code to pass it around to each function instead of using ‘ref’ or using the state monad encapsulated in a computation expression. Any of these solutions is left as an exercise to the reader (use the testcases to validate that you get it right).

We could go in many different direction from here. We could talk about:

  * The evaluator
  * The parser
  * The symbol table
  * Error handling

To keep with the top – down approach I’ve been espousing. I’ll probably talk about the evaluator next.