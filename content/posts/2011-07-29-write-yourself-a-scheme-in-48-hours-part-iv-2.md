---
id: 48
title: 'Write Yourself a Scheme in 48 Hours in F# – Part V'
date: 2011-07-29T07:26:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/07/30/write-yourself-a-scheme-in-48-hours-part-iv-2/
permalink: /2011/07/29/write-yourself-a-scheme-in-48-hours-part-iv-2/
categories:
  - 'F#'
tags:
  - 'F#'
  - Lambda expressions
  - Parsing
---
We have one loose end to tie in the evaluator: the primitive operators. These are things that the interpreter knows intrinsically. There is a list of them below.

<pre class="code"><span style="color:blue;">let rec </span>primitives =
     [
        <span style="color:maroon;">"+"</span>,    numericBinop (+)
        <span style="color:maroon;">"-"</span>,    numericBinop (-)
        <span style="color:maroon;">"*"</span>,    numericBinop (*)
        <span style="color:maroon;">"/"</span>,    numericBinop (/)
        <span style="color:maroon;">"mod"</span>,  numericBinop (%)
        <span style="color:maroon;">"="</span>,    numBoolBinop (=)
        <span style="color:maroon;">"&lt;"</span>,    numBoolBinop (&lt;)
        <span style="color:maroon;">"&gt;"</span>,    numBoolBinop (&gt;)
        <span style="color:maroon;">"/="</span>,   numBoolBinop (&lt;&gt;)
        <span style="color:maroon;">"&gt;="</span>,   numBoolBinop (&gt;=)
        <span style="color:maroon;">"&lt;="</span>,   numBoolBinop (&lt;=)
        <span style="color:maroon;">"&&"</span>,   boolBoolBinop (&&)
        <span style="color:maroon;">"||"</span>,   boolBoolBinop (||)
        <span style="color:maroon;">"string=?"</span>,     strBoolBinop (=)
        <span style="color:maroon;">"string&gt;?"</span>,      strBoolBinop (&gt;)
        <span style="color:maroon;">"string&lt;?"</span>,      strBoolBinop (&lt;)
        <span style="color:maroon;">"string&lt;=?"</span>,    strBoolBinop (&lt;=)
        <span style="color:maroon;">"string&gt;=?"</span>,    strBoolBinop (&gt;=)
        <span style="color:maroon;">"car"</span>,  car
        <span style="color:maroon;">"cdr"</span>,  cdr
        <span style="color:maroon;">"cons"</span>, cons
        <span style="color:maroon;">"eq?"</span>, eqv
        <span style="color:maroon;">"eqv?"</span>, eqv
        <span style="color:maroon;">"equal?"</span>, equal
        <span style="color:green;">// IO primitives
        </span><span style="color:maroon;">"apply"</span>, applyProc
        <span style="color:maroon;">"open-input-file"</span>, makePort FileAccess.Read
        <span style="color:maroon;">"open-output-file"</span>, makePort FileAccess.Write
        <span style="color:maroon;">"close-input-port"</span>, closePort
        <span style="color:maroon;">"close-output-port"</span>, closePort
        <span style="color:maroon;">"read"</span>, readProc
        <span style="color:maroon;">"write"</span>, writeProc
        <span style="color:maroon;">"read-contents"</span>, readContents
        <span style="color:maroon;">"read-all"</span>, readAll
     ]</pre>

Having seen the above list, it now becomes clearer why the _primitiveBindings_ function was defined as such. It just binds these pairs into the environment.

<pre class="code"><span style="color:blue;">let </span>primitiveBindings () =
    (nullEnv ()) |&gt; bindVars [ <span style="color:blue;">for </span>v, f <span style="color:blue;">in </span>primitives <span style="color:blue;">-&gt; </span>v, PrimitiveFunc f ] </pre>



_numericBinop_ unpacks the numbers, applies the provided operator and packs the result back in the Number.

<pre class="code"><span style="color:blue;">let </span>numericBinop op parms =
    <span style="color:blue;">if </span>List.length parms &lt; 2
        <span style="color:blue;">then </span>throw &lt;| NumArgs(2, parms)
        <span style="color:blue;">else </span>parms |&gt; List.map unpackNum |&gt; foldl1 op |&gt; Number</pre>

While we are at it, we can define _fold1 (_it tends to be&#160; useful)

<pre class="code"><span style="color:blue;">let </span>foldl1 op = <span style="color:blue;">function
    </span>| h::t <span style="color:blue;">-&gt; </span>List.fold op h t
    | [] <span style="color:blue;">-&gt; </span>throw (Default(<span style="color:maroon;">"Expected a not empty list, got an empty list"</span>))</pre>

The other XBinops work similarly …

<pre class="code"><span style="color:blue;">let </span>boolBinop unpacker op args =
    <span style="color:blue;">match </span>args <span style="color:blue;">with
    </span>| [ left; right ] <span style="color:blue;">-&gt; </span>Bool (op (unpacker left) (unpacker right))
    | _ <span style="color:blue;">-&gt; </span>throw (NumArgs(2,args))
<span style="color:blue;">let </span>numBoolBinop = boolBinop unpackNum
<span style="color:blue;">let </span>strBoolBinop = boolBinop unpackStr
<span style="color:blue;">let </span>boolBoolBinop = boolBinop unpackBool</pre>

We now have to look at the family of unpackers. They all work rather similarly. Notice Scheme making an effort to get a number out of a string and to get anything out of a list. Strong type folks won’t like that. Oh well, just remove these lines …

<pre class="code"><span style="color:blue;">let rec </span>unpackNum = <span style="color:blue;">function
    </span>| Number n  <span style="color:blue;">-&gt; </span>n
    | String n  <span style="color:blue;">-&gt; let </span>success, result = System.Int32.TryParse n
                   <span style="color:blue;">if </span>success
                       <span style="color:blue;">then </span>result
                       <span style="color:blue;">else </span>throw (TypeMismatch(<span style="color:maroon;">"number"</span>, String n))
    | List [n]  <span style="color:blue;">-&gt; </span>unpackNum n
    | notNumber <span style="color:blue;">-&gt; </span>throw (TypeMismatch(<span style="color:maroon;">"number"</span>, notNumber))
<span style="color:blue;">let rec </span>unpackStr = <span style="color:blue;">function
    </span>| String s <span style="color:blue;">-&gt; </span>s
    | Number n <span style="color:blue;">-&gt; </span>n.ToString()
    | Bool b   <span style="color:blue;">-&gt; </span>b.ToString()
    | List [s]  <span style="color:blue;">-&gt; </span>unpackStr s
    | noString <span style="color:blue;">-&gt; </span>throw (TypeMismatch(<span style="color:maroon;">"string"</span>, noString))
<span style="color:blue;">let rec </span>unpackBool = <span style="color:blue;">function
    </span>| Bool b <span style="color:blue;">-&gt; </span>b
    | List [b]  <span style="color:blue;">-&gt; </span>unpackBool b
    | noBool <span style="color:blue;">-&gt; </span>throw (TypeMismatch(<span style="color:maroon;">"boolean"</span>, noBool))</pre>

Now back to the list of primitive operators, there are the signature LISP operators _car_, _cdr_ and _cons_. Just understanding the first line for each function should be enough to get an idea of what they do.

<pre class="code"><span style="color:blue;">let </span>car = <span style="color:blue;">function
    </span>| [List (x :: _)] <span style="color:blue;">-&gt; </span>x
    | [DottedList (x :: _, _)] <span style="color:blue;">-&gt; </span>x
    | [badArg] <span style="color:blue;">-&gt; </span>throw (TypeMismatch(<span style="color:maroon;">"pair"</span>, badArg))
    | badArgList <span style="color:blue;">-&gt; </span>throw (NumArgs(1, badArgList))
<span style="color:blue;">let </span>cdr = <span style="color:blue;">function
    </span>| [List (x :: xs)] <span style="color:blue;">-&gt; </span>List xs
    | [DottedList ([xs], x)] <span style="color:blue;">-&gt; </span>x
    | [DottedList ((_ :: xs), x)] <span style="color:blue;">-&gt; </span>DottedList (xs, x)
    | [badArg] <span style="color:blue;">-&gt; </span>throw (TypeMismatch(<span style="color:maroon;">"pair"</span>, badArg))
    | badArgList <span style="color:blue;">-&gt; </span>throw (NumArgs(1, badArgList))
<span style="color:blue;">let </span>cons = <span style="color:blue;">function
    </span>| [x; List xs] <span style="color:blue;">-&gt; </span>List (x :: xs)
    | [x; DottedList (xs, xlast)] <span style="color:blue;">-&gt; </span>DottedList (x :: xs, xlast)
    | [x1; x2] <span style="color:blue;">-&gt; </span>DottedList([x1], x2)
    | badArgList <span style="color:blue;">-&gt; </span>throw (NumArgs(2, badArgList))</pre>

We then need to work our way to implement _eqv_ (aka _eq?_ in Scheme). We first define a function that tests that two LispVal are the same. It should be pretty self explanatory (the list piece is kind of cute).

<pre class="code"><span style="color:blue;">let rec </span>eqvPrim e1 e2 =
        <span style="color:blue;">match </span>e1, e2 <span style="color:blue;">with
        </span>| (Bool b1, Bool b2) <span style="color:blue;">-&gt; </span>b1 = b2
        | (Number n1, Number n2) <span style="color:blue;">-&gt; </span>n1 = n2
        | (String s1, String s2) <span style="color:blue;">-&gt; </span>s1 = s2
        | (Atom a1, Atom a2) <span style="color:blue;">-&gt; </span>a1 = a2
        | (DottedList (xs, x), DottedList(ys, y)) <span style="color:blue;">-&gt; </span>eqvPrim (List (xs @ [x])) (List (ys @ [y]))
        | (List l1, List l2) <span style="color:blue;">-&gt; </span>l1.Length = l2.Length && List.forall2 eqvPrim l1 l2
        | _ <span style="color:blue;">-&gt; false
</span></pre>

Now we wrap the result in a _Bool_. Doing it this way avoid repeating the wrapping in each single line of _eqvPrim_ (thanks to Tobias for spotting this refactoring).

<pre class="code"><span style="color:blue;">let </span>eqv = <span style="color:blue;">function
          </span>| [e1; e2] <span style="color:blue;">-&gt; </span>Bool (eqvPrim e1 e2)
          | badArgList <span style="color:blue;">-&gt; </span>throw (NumArgs (2, badArgList))</pre>

_Equal?_ checks if there is any unpacking scheme that can be used to test equality of the two elements of a two element list.

<pre class="code"><span style="color:blue;">let </span>equal = <span style="color:blue;">function
    </span>| [arg1; arg2] <span style="color:blue;">-&gt;
        let </span>unpackEqual = numUnpackEq arg1 arg2 ||
                          strUnpackEq arg1 arg2 ||
                          boolUnpackEq arg1 arg2
        Bool (eqvPrim arg1 arg2 || unpackEqual)
    | argsList <span style="color:blue;">-&gt; </span>throw (NumArgs(2, argsList))</pre>

We need to define equality of packed primitive types. We do it nicely below.

<pre class="code"><span style="color:blue;">let </span>tryUnpacker (unpack : LispVal <span style="color:blue;">-&gt; </span>'a) (op : 'a <span style="color:blue;">-&gt; </span>'a <span style="color:blue;">-&gt; </span>bool) arg1 arg2 =
    <span style="color:blue;">try </span>op (unpack arg1) (unpack arg2) <span style="color:blue;">with </span>_ <span style="color:blue;">-&gt; false
let </span>numUnpackEq = tryUnpacker unpackNum (=)
<span style="color:blue;">let </span>strUnpackEq = tryUnpacker unpackStr (=)
<span style="color:blue;">let </span>boolUnpackEq = tryUnpacker unpackBool (=)</pre>

The _apply_ statement maps more or less directly to our _apply_ function.

<pre class="code">applyProc = <span style="color:blue;">function
            </span>| [func; List args] <span style="color:blue;">-&gt; </span>apply func args
            | func :: args <span style="color:blue;">-&gt; </span>apply func args
            | [] <span style="color:blue;">-&gt; </span>throw (Default(<span style="color:maroon;">"Expecting a function, got an empty list"</span>))</pre>

And we are left with the I/O processing functions. We are simply wrapping a FileStream in a Port.

<pre class="code"><span style="color:blue;">let </span>makePort fileAccess = fileIOFunction (<span style="color:blue;">fun </span>fileName <span style="color:blue;">-&gt;
                                </span>File.Open(fileName,FileMode.OpenOrCreate, fileAccess) |&gt; Port)
    <span style="color:blue;">let </span>closePort = <span style="color:blue;">function
                    </span>| [Port(port)] <span style="color:blue;">-&gt; </span>port.Close() ; Bool <span style="color:blue;">true
                    </span>| _ <span style="color:blue;">-&gt; </span>Bool <span style="color:blue;">false
</span></pre>

We then can read and write from it. Notice how the lack of arguments makes us do it from the standard Console.

<pre class="code"><span style="color:blue;">let rec </span>readProc port =
    <span style="color:blue;">let </span>parseReader (reader:TextReader) = reader.ReadLine() |&gt; readExpr
    <span style="color:blue;">match </span>port <span style="color:blue;">with
       </span>| [] <span style="color:blue;">-&gt; </span>parseReader(System.Console.In)
       | [Port(port)] <span style="color:blue;">-&gt;
            use </span>reader = <span style="color:blue;">new </span>StreamReader(port)
            parseReader (reader)
       | args <span style="color:blue;">-&gt; </span>throw (NumArgs(1, args))
<span style="color:blue;">let </span>writeProc objPort =
    <span style="color:blue;">let </span>write obj (writer: TextWriter) = writer.Write(showVal obj) ; Bool <span style="color:blue;">true
    match </span>objPort <span style="color:blue;">with
    </span>| [obj] <span style="color:blue;">-&gt; </span>write obj (System.Console.Out)
    | [obj ; Port(port)] <span style="color:blue;">-&gt;
        use </span>writer = <span style="color:blue;">new </span>StreamWriter(port)
        write obj writer
    | args <span style="color:blue;">-&gt; </span>throw (NumArgs(1, args))</pre>

There you go. A full evaluator in two blog posts!! Next up, the parser.