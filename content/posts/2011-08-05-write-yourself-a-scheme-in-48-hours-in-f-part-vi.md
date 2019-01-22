---
id: 53
title: 'Write Yourself a Scheme in 48 Hours in F# – Part VI'
date: 2011-08-05T07:08:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/08/06/write-yourself-a-scheme-in-48-hours-in-f-part-vi/
permalink: /2011/08/05/write-yourself-a-scheme-in-48-hours-in-f-part-vi/
categories:
  - 'F#'
---
The evaluator takes as an input a _LispVal_. Where does it come from? There must be something that converts your textual input into it. That is the job of the parser.

I have used [FParsec](http://www.quanttec.com/fparsec/) to build my parser. FParsec is a fantastic library to build parsers. It is a perfect showcase of the composition potential that functional code yields.&#160; 

When you write an FParsec parser you compose many little parsers to create the one parser that works for your language.&#160; The resulting code looks very much like your language grammar, but you don’t need&#160; a separate code generation compilation step to produce it.

There is one element of ugliness in the syntax to create recursive parsers. You need to define two global variables that can be referred to before they are constructed. This is an artefact of how F# works. So you need a line in your code that looks like this:

<pre class="code"><span style="color:blue;">let </span>parseExpr, parseExprRef : LispParser * LispParser ref = createParserForwardedToRef()</pre>

With that piece of machinery out of the way, we can focus on the parser itself. Our goal here is to parse expressions and generate _LispVal_. We need a _LispParser_ like the below (the second generic parameter is for advanced usage).

<pre class="code"><span style="color:blue;">type </span>LispParser = Parser&lt;LispVal, unit&gt;</pre>

We need to parse all the kind of expressions that the user can type. Notice in the below the use of a computation expression to simplify the syntax. Also note that lists and dotted lists look very much the same until you encounter the ‘.’ character. You could disambiguate the situation by extracting out the commonality in a separate kind of expression. I decided instead to instruct the parser to backtrack if it gets it wrong (_attempt_). This is slower, but keeps the code identical to our conceptual model. I value that greatly. 

<pre class="code"><span style="color:blue;">do </span>parseExprRef := parseAtom
                   &lt;|&gt; parseString
                   &lt;|&gt; parseNumber
                   &lt;|&gt; parseQuoted
                   &lt;|&gt; parse {
                           <span style="color:blue;">do! </span>chr <span style="color:maroon;">'('
                           </span><span style="color:blue;">let! </span>x = (attempt parseList) &lt;|&gt; parseDottedList
                           <span style="color:blue;">do! </span>chr <span style="color:maroon;">')'
                           </span><span style="color:blue;">return </span>x
                       }</pre>

Let’s start from the top. Parsing an atom means parsing something that starts with a letter or symbol and continues with letters, symbols or digits. Also “#t” and “#f” can be resolved at parsing time.

<pre class="code"><span style="color:blue;">let </span>parseAtom : LispParser = parse {
        <span style="color:blue;">let! </span>first = letter &lt;|&gt; symbol
        <span style="color:blue;">let! </span>rest = manyChars (letter &lt;|&gt; symbol &lt;|&gt; digit)
        <span style="color:blue;">return match </span>first.ToString() + rest <span style="color:blue;">with
               </span>| <span style="color:maroon;">"#t" </span><span style="color:blue;">-&gt; </span>Bool <span style="color:blue;">true
               </span>| <span style="color:maroon;">"#f" </span><span style="color:blue;">-&gt; </span>Bool <span style="color:blue;">false
               </span>| atom <span style="color:blue;">-&gt; </span>Atom atom
}</pre>

A string is just a bunch of chars (except ‘\’) surrounded by ‘ ” ’.

<pre class="code"><span style="color:blue;">let </span>parseString : LispParser = parse {
    <span style="color:blue;">do! </span>chr <span style="color:maroon;">'"'
    </span><span style="color:blue;">let! </span>xs = manyChars (noneOf <span style="color:maroon;">"\""</span>)
    <span style="color:blue;">do! </span>chr <span style="color:maroon;">'"'
    </span><span style="color:blue;">return </span>String(xs)
}</pre>



A number is just one or more digits. I am afraid we just support integers at this stage …

<pre class="code"><span style="color:blue;">let </span>parseNumber : LispParser = many1Chars digit |&gt;&gt; (System.Int32.Parse &gt;&gt; Number)</pre>

A quoted expression is jut a ‘\’ followed by an expression.

<pre class="code"><span style="color:blue;">let </span>parseQuoted : LispParser = chr <span style="color:maroon;">'\'' </span>&gt;&gt;. parseExpr |&gt;&gt; <span style="color:blue;">fun </span>expr <span style="color:blue;">-&gt; </span>List [Atom <span style="color:maroon;">"quote"</span>; expr] </pre>

A list is just a bunch of expressions separate by at least one space.

<pre class="code"><span style="color:blue;">let </span>parseList : LispParser = sepBy parseExpr spaces1 |&gt;&gt; List</pre>

A dotted list starts in the same way (hence the backtracking above), but then has a dot, one or more spaces and an expression.

<pre class="code"><span style="color:blue;">let </span>parseDottedList : LispParser = parse {
    <span style="color:blue;">let! </span>head = endBy parseExpr spaces1
    <span style="color:blue;">let! </span>tail = chr <span style="color:maroon;">'.' </span>&gt;&gt;. spaces1 &gt;&gt;. parseExpr
    <span style="color:blue;">return </span>DottedList (head, tail)
}</pre>

And here are a bunch of functions used throughout the code, presented here for completeness.

<pre class="code"><span style="color:blue;">let </span>spaces1 : LispParser&lt;unit&gt; = skipMany1 whitespace
    <span style="color:blue;">let </span>chr c = skipChar c
    <span style="color:blue;">let </span>endBy  p sep = many  (p .&gt;&gt; sep)
    <span style="color:blue;">let </span>symbol : LispParser&lt;char&gt; = anyOf <span style="color:maroon;">"!$%&|*+-/:&lt;=&gt;?@^_~#"
</span></pre>



This is all the code you need to translate text to a _LispVal_ to feed the evaluator. That is pretty impressive.

There is also a function to go the other way, from a LispVal to text. It is used in implementing the testcases and to print out diagnostics.

<pre class="code"><span style="color:blue;">let rec </span>showVal = <span style="color:blue;">function
        </span>| String contents <span style="color:blue;">-&gt; </span><span style="color:maroon;">"\"" </span>+ contents + <span style="color:maroon;">"\""
        </span>| Atom name <span style="color:blue;">-&gt; </span>name
        | Number num <span style="color:blue;">-&gt; </span>num.ToString()
        | Bool t <span style="color:blue;">-&gt; if </span>t <span style="color:blue;">then </span><span style="color:maroon;">"#t" </span><span style="color:blue;">else </span><span style="color:maroon;">"#f"
        </span>| List l <span style="color:blue;">-&gt; </span><span style="color:maroon;">"(" </span>+ unwordsList l + <span style="color:maroon;">")"
        </span>| DottedList (head, tail) <span style="color:blue;">-&gt; </span><span style="color:maroon;">"(" </span>+ unwordsList head + <span style="color:maroon;">" . " </span>+ showVal tail + <span style="color:maroon;">")"
        </span>| PrimitiveFunc(_) <span style="color:blue;">-&gt; </span><span style="color:maroon;">"&lt;primitive&gt;"
        </span>| Port (_) <span style="color:blue;">-&gt; </span><span style="color:maroon;">"&lt;IO port&gt;"
        </span>| Func({ parms = parms; varargs = varargs; body = body; closure = closure }) <span style="color:blue;">-&gt;
                                                </span><span style="color:maroon;">"(lambda (" </span>+ unwordsList (parms |&gt; List.map (String)) +
                                                    (<span style="color:blue;">match </span>varargs <span style="color:blue;">with
                                                        </span>| None <span style="color:blue;">-&gt; </span><span style="color:maroon;">""
                                                        </span>| Some(arg) <span style="color:blue;">-&gt; </span><span style="color:maroon;">" . " </span>+ arg) + <span style="color:maroon;">") ...)"
    </span><span style="color:blue;">and
        </span>unwordsList = List.map showVal &gt;&gt; String.concat <span style="color:maroon;">" "
</span></pre>

