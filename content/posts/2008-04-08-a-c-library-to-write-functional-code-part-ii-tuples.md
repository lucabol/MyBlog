---
id: 493
title: 'A C# library to write functional code - Part II - Tuples'
date: 2008-04-08T16:51:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples/
permalink: /2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "8369978"
orig_parent_id:
  - "8369978"
orig_thread_id:
  - "575453"
orig_application_key:
  - lucabol
orig_post_author_id:
  - "3896"
orig_post_author_username:
  - lucabol
orig_post_author_created:
  - 'Apr  2 2005 10:57:56:453AM'
orig_is_approved:
  - "1"
orig_attachment_count:
  - "1"
orig_url_title:
  - http://blogs.msdn.com/b/lucabol/archive/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="A C# library to write functional code  - Part II  - Tuples" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator Tuples are a way for you not to name things. In Object Oriented languages&nbsp;you got to name everything. If you need to represent a bunch of data,..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="A C# library to write functional code  - Part II  - Tuples" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples/" />
    <meta name="twitter:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator Tuples are a way for you not to name things. In Object Oriented languages&nbsp;you got to name everything. If you need to represent a bunch of data,..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - csharp
---
Other posts in the series:

  * [**<font color="#006bad">Part I  - Background</font>**](http://blogs.msdn.com/lucabol/archive/2008/04/01/a-c-library-to-write-functional-code-part-i-background.aspx) 
      * [**<font color="#006bad">Part II  - Tuples</font>**](http://blogs.msdn.com/lucabol/archive/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples.aspx) 
          * **[<font color="#006bad">Part III  - Records</font>](http://blogs.msdn.com/lucabol/archive/2008/04/21/a-c-library-to-write-functional-code-part-iii-records.aspx)**
          * **[Part IV  - Type Unions](http://blogs.msdn.com/lucabol/archive/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions.aspx){.}**
          * **[Part V  - The Match operator](http://blogs.msdn.com/lucabol/archive/2008/07/15/a-c-library-to-write-functional-code-part-v-the-match-operator.aspx){.}**
        <a href="http://en.wikipedia.org/wiki/Tuple" target="_blank"><strong><font color="#006bad">Tuples</font></strong></a> are a way for you not to name things. In Object Oriented languages&nbsp;you got to name everything. If you need to represent a bunch of data, you create a class for it.
        
        There is a strange asymmetry in mainstream OO languages in that you can pass multiple parameters to a function, but you can return just one value. Granted, there are ways around it: you can use &#8216;ref' in C# or return some sort of collection where things are stored. But by and large the model is: you pass many, you get one; if you need to return more than one, create a class to represent this &#8216;bunch of data'. Tuples are a way for you not to create such a class.
        
        Tuples are also much more than that. Once you have&nbsp;the language&nbsp;concept of &#8216;a bunch of data without a name', you can create arrays of them, you can pass them as parameters, use them as local variables. Wherever you'd use a type, you can use a Tuple instead.
        
        This is particularly appealing to me as I like to use classes almost exclusively to represent things that have a counterpart in the domain I'm modeling (i.e. Customer, Account). I don't like to create classes/structs just for the sake of temporarily put some data together.
        
        You can create&nbsp;your own Tuple class&nbsp;in C#, but the syntax gets ugly. Syntax matter. Syntax helps you to think differently about your program. We have syntax for anonymous types, but given that they cannot escape the scope of a method, they cannot be used as full replacement for Tuples.
        
        In any case, to my implementation. Here is how you create a Tuple:
        
        <pre class="code"><span style="color:rgb(0,0,255);">var</span> t1 = <span style="color:rgb(43,145,175);">F</span>.Tuple(34, <span style="color:rgb(163,21,21);">"bo"</span>, 2.3);</pre>
        
        not too bad. In F# it is better: (34, bo, 2.3). And you often don't need the parenthesis. But still, my C# version is ok.
        
        You then need to access its elements:
        
        <pre class="code"><span style="color:rgb(0,0,255);">var</span> n = t1.Item1;
            <span style="color:rgb(0,0,255);">var</span> s = t1.Item2;
</pre>
        
        In F# you usually access them by doing pattern matching, which gives a more intuitive syntax. But again, my C# syntax is not terrible.&nbsp;
        
        Tuples need to have structural equality, which means that the following has to work:
        
        <pre class="code"><span style="color:rgb(43,145,175);">ArrayList</span> mad1 = <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">ArrayList</span> { <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">List</span>&lt;<span style="color:rgb(43,145,175);">IEnumerable</span>&lt;<span style="color:rgb(0,0,255);">string</span>&gt;&gt; { <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(0,0,255);">string</span>[] { <span style="color:rgb(163,21,21);">"bo"</span> }, <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(0,0,255);">string</span>[] { <span style="color:rgb(163,21,21);">"bo"</span> } },<br />                               32, <span style="color:rgb(163,21,21);">"bo"</span>, <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(0,0,255);">int</span>[] { 4, 5, 6 } };
        <span style="color:rgb(43,145,175);">ArrayList</span> mad2 = <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">ArrayList</span> { <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">List</span>&lt;<span style="color:rgb(43,145,175);">IEnumerable</span>&lt;<span style="color:rgb(0,0,255);">string</span>&gt;&gt; { <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(0,0,255);">string</span>[] { <span style="color:rgb(163,21,21);">"bo"</span> }, <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(0,0,255);">string</span>[] { <span style="color:rgb(163,21,21);">"bo"</span> } },<br />                               32, <span style="color:rgb(163,21,21);">"bo"</span>, <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(0,0,255);">int</span>[] { 4, 5, 6 } };
        <span style="color:rgb(43,145,175);">ArrayList</span> mad3 = <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">ArrayList</span> { <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">List</span>&lt;<span style="color:rgb(43,145,175);">IEnumerable</span>&lt;<span style="color:rgb(0,0,255);">string</span>&gt;&gt; { <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(0,0,255);">string</span>[] { <span style="color:rgb(163,21,21);">"bo"</span> }, <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(0,0,255);">string</span>[] { <span style="color:rgb(163,21,21);">"bo"</span> } },<br />                               32, <span style="color:rgb(163,21,21);">"bo"</span>, <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(0,0,255);">int</span>[] { 4, 5, 5 } };</pre>
        
        
        
        <pre class="code"><span style="color:rgb(43,145,175);">Assert</span>.AreEqual(<span style="color:rgb(43,145,175);">F</span>.Tuple(mad1, mad2, mad1), <span style="color:rgb(43,145,175);">F</span>.Tuple(mad2, mad1, mad2));
        <span style="color:rgb(43,145,175);">Assert</span>.AreNotEqual(<span style="color:rgb(43,145,175);">F</span>.Tuple(mad1, mad2, mad1), <span style="color:rgb(43,145,175);">F</span>.Tuple(mad1, mad3, mad1));</pre>
        
        You can use Tuples as return values, parameters, locals etc. Unfortunately, the syntax is ugly when Tuples are part of the signature of a function:
        
        <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">Tuple</span>&lt;<span style="color:rgb(0,0,255);">string</span>, <span style="color:rgb(43,145,175);">IEnumerable</span>&lt;<span style="color:rgb(43,145,175);">Tuple</span>&lt;<span style="color:rgb(0,0,255);">string</span>, <span style="color:rgb(43,145,175);">ObservationHistory</span>&gt;&gt;&gt; Execute() {
    }</pre>
        
        With the above information, you can be a user of Tuples. From this point on, I'll talk about some details of the implementation (I also attach the full code to this post as a zip file).
        
        <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">class</span> <span style="color:rgb(43,145,175);">Tuple</span>&lt;T1&gt; {
        <span style="color:rgb(0,0,255);">public</span> Tuple(T1 t1) {
            Item1 = t1;
        }
        <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">readonly</span> T1 Item1;
<span style="color:rgb(0,0,255);">       <font color="#80ff80"> </font><font color="#808080">#region</font></span><font color="#808080"> Equals, GetHashCode, ==, !=</font>
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">class</span> <span style="color:rgb(43,145,175);">Tuple</span>&lt;T1, T2&gt; : <span style="color:rgb(43,145,175);">Tuple</span>&lt;T1&gt; {
        <span style="color:rgb(0,0,255);">public</span> Tuple(T1 t1, T2 t2) : <span style="color:rgb(0,0,255);">base</span>(t1) { Item2 = t2; }
        <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">readonly</span> T2 Item2;
<span style="color:rgb(0,0,255);">        <font color="#808080">#region</font></span><font color="#808080"> Equals, GetHashCode, ==, !=
</font>    }</pre>
        
        &nbsp;
        
        So, Tuples are classes, not structs. The reason for it is fully described in <a href="http://blogs.msdn.com/lucabol/archive/2008/01/11/creating-an-immutable-value-object-in-c-part-v-using-a-library.aspx" target="_blank"><strong><font color="#006bad">this series of posts</font></strong></a>. They also inherit from one another. There are pros and cons to that. The main pros are that I had to write less code and that you can pass a Tuple<int, string> when a function expects a Tuple<int, string, int>. The main drawback is that you can pass a Tuple<int, string> when a function expects a Tuple<int, string, int>.&nbsp; Also notice the use of public fields. These&nbsp;is a problem with frameworks that insist on properties (i.e. Data Binding). Also, I just got to 5 as arity goes. The day I need 6 items, I'll add another one. It is boilerplate code (that I'd still like not to write).
        
        The Equals method is a bit convoluted:
        
        <pre class="code"><span style="color:rgb(0,0,255);">internal</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(0,0,255);">class</span> <span style="color:rgb(43,145,175);">Utils</span> {
        <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(0,0,255);">void</span> CheckNull&lt;T&gt;(T t) {
            <span style="color:rgb(0,0,255);">if</span> (t == <span style="color:rgb(0,0,255);">null</span>)
                <span style="color:rgb(0,0,255);">throw</span> <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">ArgumentNullException</span>();
        }<br />     }</pre>
        
        
        
        <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">override</span> <span style="color:rgb(0,0,255);">bool</span> Equals(<span style="color:rgb(0,0,255);">object</span> right) {
            <span style="color:rgb(43,145,175);">Utils</span>.CheckNull(right);
            <span style="color:rgb(0,0,255);">if</span> (<span style="color:rgb(0,0,255);">object</span>.ReferenceEquals(<span style="color:rgb(0,0,255);">this</span>, right))
                <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">true</span>;
            <span style="color:rgb(0,0,255);">if</span> (<span style="color:rgb(0,0,255);">this</span>.GetType() != right.GetType())
                <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">false</span>;
            <span style="color:rgb(0,0,255);">var</span> rightT = right <span style="color:rgb(0,0,255);">as</span> <span style="color:rgb(43,145,175);">Tuple</span>&lt;T1, T2, T3&gt;;
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">base</span>.Equals(rightT) && <span style="color:rgb(43,145,175);">F</span>.DSEquals(<span style="color:rgb(0,0,255);">this</span>.Item3, rightT.Item3);
        }</pre>
        
        
        
        I always get complaints when I show Equals methods that throw if null is passed in, but I stand by my logic, that&nbsp;the presence of null for these categories of&nbsp;&#8216;structurally equal' classes is symptom of an error and I want to be notified.&nbsp;Returning false doesn't do that.
        
        <pre class="code"><span style="color:rgb(0,0,255);">internal</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(0,0,255);">bool</span> DSEquals&lt;T&gt;(T left, T right) {
            <span style="color:rgb(0,0,255);">if</span> (left == <span style="color:rgb(0,0,255);">null</span> && right == <span style="color:rgb(0,0,255);">null</span>)
                <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">true</span>;
            <span style="color:rgb(0,0,255);">if</span> (left == <span style="color:rgb(0,0,255);">null</span> && right != <span style="color:rgb(0,0,255);">null</span>)
                <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">false</span>;
            <span style="color:rgb(0,0,255);">var</span> len = left <span style="color:rgb(0,0,255);">as</span> <span style="color:rgb(43,145,175);">IEnumerable</span>;
            <span style="color:rgb(0,0,255);">var</span> ren = right <span style="color:rgb(0,0,255);">as</span> <span style="color:rgb(43,145,175);">IEnumerable</span>;
            <span style="color:rgb(0,0,255);">if</span> (len == <span style="color:rgb(0,0,255);">null</span> && ren == <span style="color:rgb(0,0,255);">null</span>)
                <span style="color:rgb(0,0,255);">return</span> left.Equals(right);
            <span style="color:rgb(0,0,255);">if</span> (len == <span style="color:rgb(0,0,255);">null</span> && ren != <span style="color:rgb(0,0,255);">null</span>)
                <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">false</span>;
            <span style="color:rgb(0,0,255);">if</span> (len != <span style="color:rgb(0,0,255);">null</span> && ren == <span style="color:rgb(0,0,255);">null</span>)
                <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">false</span>;
            <span style="color:rgb(0,0,255);">return</span> SequenceEqual(len, ren);
        }</pre>
        
        DSEquals check the content of the Tuple and forward to SequenceEqual in case one slot of the Tuple contains an IEnumerable.
        
        <pre class="code"><span style="color:rgb(0,0,255);">internal</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(0,0,255);">bool</span> SequenceEqual(<span style="color:rgb(43,145,175);">IEnumerable</span> en1, <span style="color:rgb(43,145,175);">IEnumerable</span> en2) {
            <span style="color:rgb(0,0,255);">var</span> enumerator = en2.GetEnumerator();
            <span style="color:rgb(0,0,255);">foreach</span> (<span style="color:rgb(0,0,255);">var</span> o <span style="color:rgb(0,0,255);">in</span> en1) {
                <span style="color:rgb(0,0,255);">if</span> (!enumerator.MoveNext())
                    <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">false</span>;
                <span style="color:rgb(0,0,255);">if</span> (!DSEquals(o, enumerator.Current))
                    <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">false</span>;
            }
</pre>
        
        SequenceEqual checks that the number of items in the enumerator is the same and recursively calls DSEqual to check structural equality for items at the same index in the two enumerators.
        
        GetHashCode is trivial (and maybe trivially wrong, one of these days I'll learn everything about GetHashCode() ).
        
        <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">override</span> <span style="color:rgb(0,0,255);">int</span> GetHashCode() {
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">base</span>.GetHashCode() | Item3.GetHashCode();
        }</pre>
        
        
        
        The equality operators are equally simple.
        
        <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(0,0,255);">bool</span> <span style="color:rgb(0,0,255);">operator</span> ==(<span style="color:rgb(43,145,175);">Tuple</span>&lt;T1, T2, T3&gt; t1, <span style="color:rgb(43,145,175);">Tuple</span>&lt;T1, T2, T3&gt; t2) {
            <span style="color:rgb(43,145,175);">Utils</span>.CheckNull(t1);
            <span style="color:rgb(43,145,175);">Utils</span>.CheckNull(t2);
            <span style="color:rgb(0,0,255);">return</span> t1.Equals(t2);
        }
        <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(0,0,255);">bool</span> <span style="color:rgb(0,0,255);">operator</span> !=(<span style="color:rgb(43,145,175);">Tuple</span>&lt;T1, T2, T3&gt; t1, <span style="color:rgb(43,145,175);">Tuple</span>&lt;T1, T2, T3&gt; t2) {
            <span style="color:rgb(0,0,255);">return</span> !(t1 == t2);
        }</pre>
        
        And ToString() prints my favorite Tuple format.
        
        <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">override</span> <span style="color:rgb(0,0,255);">string</span> ToString() {
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">string</span>.Format(<span style="color:rgb(163,21,21);">"{0},{1}"</span>, <span style="color:rgb(0,0,255);">base</span>.ToString(), Item3.ToString());
        }</pre>
        
        I'm sure you can find plenty of issues in this code. As always, it is not &#8216;production ready', it is more &#8216;Luca having fun doing it'. In any case, there are some testcases in the solution to check the extent of my testing.
        
        In the next post we'll look at Records.
        
        [Functional.zip](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/08/36/99/78/Functional.zip)