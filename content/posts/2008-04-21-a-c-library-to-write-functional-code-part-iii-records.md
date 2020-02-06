---
id: 473
title: 'A C# library to write functional code - Part III - Records'
date: 2008-04-21T13:34:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/04/21/a-c-library-to-write-functional-code-part-iii-records/
permalink: /2008/04/21/a-c-library-to-write-functional-code-part-iii-records/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/04/21/a-c-library-to-write-functional-code-part-iii-records.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "8415052"
orig_parent_id:
  - "8415052"
orig_thread_id:
  - "578137"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/04/21/a-c-library-to-write-functional-code-part-iii-records.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="A C# library to write functional code  - Part III  - Records" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/04/21/a-c-library-to-write-functional-code-part-iii-records/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator Now that we know what Tuples are, we can start talking about Record, as they use a derivative of Tuples under the cover. But first, what is..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="A C# library to write functional code  - Part III  - Records" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/04/21/a-c-library-to-write-functional-code-part-iii-records/" />
    <meta name="twitter:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator Now that we know what Tuples are, we can start talking about Record, as they use a derivative of Tuples under the cover. But first, what is..." />
    
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
        Now that we know what Tuples are, we can start talking about Record, as they use a derivative of Tuples under the cover. But first, what is a record?
        
        Well, in C# parlance a Record is a&nbsp;sort of&nbsp;immutable value object. I talked at length about these fellows in <a href="http://blogs.msdn.com/lucabol/archive/2007/12/03/creating-an-immutable-value-object-in-c-part-i-using-a-class.aspx" target="_blank"><strong><font color="#006bad">this series of blog posts</font></strong></a>. In functional parlance, a Record is a Tuple that lets you access its items by name.
        
        You code Records like this:
        
        <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">class</span> <span style="color:rgb(43,145,175);">Order</span>: <span style="color:rgb(43,145,175);">Record</span>&lt;<span style="color:rgb(0,0,255);">string</span>, <span style="color:rgb(0,0,255);">int</span>&gt; {
        <span style="color:rgb(0,0,255);">public</span> Order(<span style="color:rgb(0,0,255);">string</span> item, <span style="color:rgb(0,0,255);">int</span> qty): <span style="color:rgb(0,0,255);">base</span>(item,qty) {}
        <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">string</span> Item { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> state.Item1;}}
        <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">int</span> Quantity { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> state.Item2; } }
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">class</span> <span style="color:rgb(43,145,175);">Customer</span>: <span style="color:rgb(43,145,175);">Record</span>&lt;<span style="color:rgb(0,0,255);">string</span>, <span style="color:rgb(43,145,175);">IEnumerable</span>&lt;<span style="color:rgb(43,145,175);">Order</span>&gt;&gt; {
        <span style="color:rgb(0,0,255);">public</span> Customer(<span style="color:rgb(0,0,255);">string</span> name, <span style="color:rgb(43,145,175);">IEnumerable</span>&lt;<span style="color:rgb(43,145,175);">Order</span>&gt; orders) : <span style="color:rgb(0,0,255);">base</span>(name, orders) { }
        <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">string</span> Name { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> state.Item1; } }
        <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">IEnumerable</span>&lt;<span style="color:rgb(43,145,175);">Order</span>&gt; Orders { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> state.Item2; } }
    }</pre>
        
        You need to do three things:
        
          1. Inherit from a generic Record class specifying the types&nbsp;of the properties as parameters
          2. Add a constructor that calls back to the&nbsp;Record constructor
          3. Add getters to retrieve the values of the properties (no setters as it is immutable)
        
        This may seem like plenty of work, but in return you get structural equality. Coding that by hand every time you use a record would be a royal pain. You lose control of the base class, but that is often not a problem as in functional-land you more often use type unions than inheritance.
        
        How is it implemented?
        
        First of all it is an abstract class with as many generic parameters as properties that you need in your Record. Let's use two as an example.
        
        <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">abstract</span> <span style="color:rgb(0,0,255);">class</span> <span style="color:rgb(43,145,175);">Record</span>&lt;T1, T2&gt; {
</pre>
        
        This abstract class has a field of type STuple:
        
        <pre class="code"><span style="color:rgb(0,0,255);">protected</span> <span style="color:rgb(0,0,255);">readonly</span> <span style="color:rgb(43,145,175);">STuple</span>&lt;T1, T2&gt; state;
</pre>
        
        What is a STuple? Well it is exactly the same as the Tuple described in Part II, but coded as a struct instead of a class. The reason to use a struct is to not allocate an additional object on the stack. This allows this solution to be as &#8216;performant' as simply having coded the fields on the class itself. Or at least I think so
        
        The Record class also has a constructor that simply initialize the STuple:
        
        <pre class="code"><span style="color:rgb(0,0,255);">public</span> Record(T1 t1, T2 t2) { state = <span style="color:rgb(43,145,175);">F</span>.STuple(t1, t2); }</pre>
        
        <pre class="code"><font face="Verdana">where</font></pre>
        
        <pre class="code"><span style="color:rgb(0,0,255);">internal</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(43,145,175);">STuple</span>&lt;T1, T2&gt; STuple&lt;T1, T2&gt;(T1 t1, T2 t2) {
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">STuple</span>&lt;T1, T2&gt;(t1, t2);
        }</pre>
        
        The Equals method is very much the same as the Tuple's one, just delegating to the same DSEqual function that checks equality for Tuples.
        
        <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">override</span> <span style="color:rgb(0,0,255);">bool</span> Equals(<span style="color:rgb(0,0,255);">object</span> right) {
            <span style="color:rgb(43,145,175);">Utils</span>.CheckNull(right);
            <span style="color:rgb(0,0,255);">if</span> (<span style="color:rgb(0,0,255);">object</span>.ReferenceEquals(<span style="color:rgb(0,0,255);">this</span>, right))
                <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">true</span>;
            <span style="color:rgb(0,0,255);">if</span> (<span style="color:rgb(0,0,255);">this</span>.GetType() != right.GetType())
                <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">false</span>;
            <span style="color:rgb(0,0,255);">var</span> rightT = right <span style="color:rgb(0,0,255);">as</span> <span style="color:rgb(43,145,175);">Record</span>&lt;T1, T2&gt;;
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(43,145,175);">F</span>.DSEquals(<span style="color:rgb(0,0,255);">this</span>.state, rightT.state);
        }</pre>
        
        That's it. Not too difficult as most of the implementation is based on the Tuple's code. Next post will hopefully be more interesting. It is about Type Unions.