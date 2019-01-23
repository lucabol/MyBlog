---
id: 463
title: 'A C# library to write functional code - Part IV - Type Unions'
date: 2008-06-06T04:45:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions/
permalink: /2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "8577265"
orig_parent_id:
  - "8577265"
orig_thread_id:
  - "587316"
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
  - "0"
orig_url_title:
  - http://blogs.msdn.com/b/lucabol/archive/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="A C# library to write functional code  - Part IV  - Type Unions" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator I'm sorry for my prolonged absence in the middle of this series of posts. I'm on a long paternity leave in Italy (playing beach volley every day)...." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="A C# library to write functional code  - Part IV  - Type Unions" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions/" />
    <meta name="twitter:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator I'm sorry for my prolonged absence in the middle of this series of posts. I'm on a long paternity leave in Italy (playing beach volley every day)...." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - 'C#'
---
Other posts in the series:

  * [**<font color="#006bad">Part I  - Background</font>**](http://blogs.msdn.com/lucabol/archive/2008/04/01/a-c-library-to-write-functional-code-part-i-background.aspx) 
      * [**<font color="#006bad">Part II  - Tuples</font>**](http://blogs.msdn.com/lucabol/archive/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples.aspx) 
          * **[<font color="#006bad">Part III  - Records</font>](http://blogs.msdn.com/lucabol/archive/2008/04/21/a-c-library-to-write-functional-code-part-iii-records.aspx)**
          * **[Part IV  - Type Unions](http://blogs.msdn.com/lucabol/archive/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions.aspx){.}**
          * **[Part V  - The Match operator](http://blogs.msdn.com/lucabol/archive/2008/07/15/a-c-library-to-write-functional-code-part-v-the-match-operator.aspx){.}**
        I'm sorry for my prolonged absence in the middle of this series of posts. I'm on a long paternity leave in Italy (playing beach volley every day). It's hard to have the discipline
        
        A bunch of you wrote telling me to finish this. So here I go: let's talk about type unions. First of all: they are not called like that. The correct name is discriminated unions. I have no idea why I call them differently, but I want to be consistent with my previous mistake.
        
        For those of you with a C++ background (like myself) they are like unions, just better (or worse depending on your convictions). They let you define a type that can represent one of several different types. You can then use the &#8216;match' operator (discussed in the next post) to pattern match against it.
        
        I won't elaborate on the pros and cons of this style of programming versus using polymorphism. I just want to show you how I implemented this construct in C#. As always, my usual caveat: this is just &#8216;educational code', use it at your own risk, no extensive or perf related test has been done on it. You can download the zip file and check my unit tests for yourself.
        
        **How type unions are used**
        
        In my world, you declare a type union like this:
        
        <pre class="code"><span style="color:blue;">public class </span><span style="color:#2b91af;">Person </span>{ }
<span style="color:blue;">public class </span><span style="color:#2b91af;">Dog </span>{ }
<span style="color:blue;">public class </span><span style="color:#2b91af;">Friend </span>: <span style="color:#2b91af;">TypeUnion</span>&lt;<span style="color:#2b91af;">Person</span>, <span style="color:#2b91af;">Dog</span>&gt; {
    <span style="color:blue;">public </span>Friend(<span style="color:#2b91af;">Person </span>p) : <span style="color:blue;">base</span>(p) { }
    <span style="color:blue;">public </span>Friend(<span style="color:#2b91af;">Dog </span>d) : <span style="color:blue;">base</span>(d) { }
}</pre>
        
        
        
        You inherit a type union from the TypeUnion class and use generic parameters that correspond to the types that the union can represent.
        
        You can then create a type union as:
        
        <pre class="code"><span style="color:blue;">var </span>fr = <span style="color:blue;">new </span><span style="color:#2b91af;">Friend</span>(<span style="color:blue;">new </span><span style="color:#2b91af;">Dog</span>());</pre>
        
        Test its type by:
        
        <pre class="code"><span style="color:#2b91af;">Assert</span>.IsTrue(fr.Is&lt;<span style="color:#2b91af;">Dog</span>&gt;());
<span style="color:#2b91af;">Assert</span>.IsFalse(fr.Is&lt;<span style="color:#2b91af;">Person</span>&gt;());</pre>
        
        Cast it to one of the types they represent:
        
        <pre class="code"><span style="color:blue;">var </span>d = fr.As&lt;<span style="color:#2b91af;">Dog</span>&gt;();</pre>
        
        Or use it with the &#8216;match' operator (fully explained in an upcoming post):
        
        <pre class="code"><span style="color:blue;">var </span>r = <span style="color:#2b91af;">F</span>.Match(fr,
    f =&gt; f.Is&lt;<span style="color:#2b91af;">Dog</span>&gt;(), f =&gt; f.As&lt;<span style="color:#2b91af;">Dog</span>&gt;().ToString(),
    f =&gt; f.Is&lt;<span style="color:#2b91af;">Person</span>&gt;(), f =&gt; f.As&lt;<span style="color:#2b91af;">Person</span>&gt;().ToString());
<span style="color:#2b91af;">Assert</span>.AreEqual(r, <span style="color:blue;">new </span><span style="color:#2b91af;">Dog</span>().ToString());</pre>
        
        Or the slightly more pleasing:
        
        <pre class="code">r = <span style="color:#2b91af;">F</span>.Match(fr,
            (<span style="color:#2b91af;">Person </span>p) =&gt; p.ToString(),
            (<span style="color:#2b91af;">Dog </span>d) =&gt; d.ToString());
<span style="color:#2b91af;">Assert</span>.AreEqual(r, <span style="color:blue;">new </span><span style="color:#2b91af;">Dog</span>().ToString());</pre>
        
        You get the idea.
        
        **How they are implemented**
        
        Nothing really sophisticated going on here. Let's take as an example a type union that can represent two types. I have versions that go to 5 types in the zip file.
        
        First of all a TypeUnion is a Record:
        
        <pre class="code"><span style="color:blue;">public class </span><span style="color:#2b91af;">TypeUnion</span>&lt;T1, T2&gt; : <span style="color:#2b91af;">Record</span>&lt;T1, T2&gt; {</pre>
        
        It has overloaded constructors to create a type union of a particular type:
        
        <pre class="code"><span style="color:blue;">public </span>TypeUnion(T1 t1)
    : <span style="color:blue;">base</span>(t1, <span style="color:blue;">default</span>(T2)) {
    UnionType = t1.GetType();
}
<span style="color:blue;">public </span>TypeUnion(T2 t2)
    : <span style="color:blue;">base</span>(<span style="color:blue;">default</span>(T1), t2) {
    UnionType = t2.GetType();
}</pre>
        
        
        
        UnionType is used to &#8216;remember' which type it is:
        
        <pre class="code"><span style="color:blue;">protected </span><span style="color:#2b91af;">Type </span>UnionType;</pre>
        
        It also has properties to return the objects of all the types that can be stored:
        
        <pre class="code"><span style="color:blue;">protected </span>T1 Type1 { <span style="color:blue;">get </span>{ <span style="color:blue;">return </span>state.Item1; } }
<span style="color:blue;">protected </span>T2 Type2 { <span style="color:blue;">get </span>{ <span style="color:blue;">return </span>state.Item2; } }</pre>
        
        The &#8216;Is' operator is simply implemented as:
        
        <pre class="code"><span style="color:blue;">public bool </span>Is&lt;K&gt;() {
    <span style="color:blue;">return typeof</span>(K).IsAssignableFrom(UnionType);
}</pre>
        
        And the &#8216;As' operator looks like so:
        
        <pre class="code"><span style="color:blue;">public </span>K As&lt;K&gt;() {
    <span style="color:blue;">if </span>(!Is&lt;K&gt;())
        <span style="color:blue;">throw new </span><span style="color:#2b91af;">Exception</span>(<span style="color:blue;">string</span>.Format(<br />          <span style="color:#a31515;">"In a TypeUnion cannot cast from {0} to {1}"</span>,<br />          UnionType.Name, <span style="color:blue;">typeof</span>(K).Name));
    <span style="color:blue;">if </span>(<span style="color:blue;">typeof</span>(T1) == UnionType)
        <span style="color:blue;">return </span>(K)(<span style="color:blue;">object</span>) Type1;
    <span style="color:blue;">if </span>(<span style="color:blue;">typeof</span>(T2) == UnionType)
        <span style="color:blue;">return </span>(K)(<span style="color:blue;">object</span>) Type2;
    <span style="color:blue;">throw new </span><span style="color:#2b91af;">Exception</span>(<span style="color:#a31515;">"Shouldn't get here"</span>);
}</pre>
        
        I leave as an exercise to the reader to understand what happens if T1 and T2 are the same type or inherit from the same type. I could have written code to handle this case in a more explicit manner, but didn't.
        
        Also, by reviewing my code I found an obvious bug in my Is<K>/As<K> code. I fixed it and re-posted the zip file in the second post of this series.
        
        Now back to the beach. Next post is on the &#8216;match' operator.