---
id: 1073
title: 'Simulating INumeric with dynamic in C# 4.0'
date: 2009-02-05T11:47:26+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/02/05/simulating-inumeric-with-dynamic-in-c-4-0/
permalink: /2009/02/05/simulating-inumeric-with-dynamic-in-c-4-0/
orig_url:
  - 'http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/02/05/simulating-inumeric-with-dynamic-in-c-%204-0.aspx'
orig_site_id:
  - "3896"
orig_post_id:
  - "9399063"
orig_parent_id:
  - "9399063"
orig_thread_id:
  - "634098"
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
  - http://blogs.msdn.com/b/lucabol/archive/2009/02/05/simulating-inumeric-with-dynamic-in-c-4-0.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Simulating INumeric with dynamic in C# 4.0" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/02/05/simulating-inumeric-with-dynamic-in-c-4-0/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="When I wrote my Excel financial library I agonized over the decision of which numeric type to use to represent money. Logic would push me toward decimal, but common usage among financial library writers would push me toward double. I ended up picking double, but I regret having to make that choice in the first..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Simulating INumeric with dynamic in C# 4.0" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/02/05/simulating-inumeric-with-dynamic-in-c-4-0/" />
    <meta name="twitter:description" content="When I wrote my Excel financial library I agonized over the decision of which numeric type to use to represent money. Logic would push me toward decimal, but common usage among financial library writers would push me toward double. I ended up picking double, but I regret having to make that choice in the first..." />
    
restapi_import_id:
  - 5c011e0505e67
original_post_id:
  - "293"
categories:
  - Uncategorized
tags:
  - csharp
---
When I wrote my [Excel financial library](http://blogs.msdn.com/lucabol/archive/2008/12/04/financial-functions-for-net-released.aspx) I agonized over the decision of which numeric type to use to represent money. Logic would push me toward _decimal_, but common usage among financial library writers would push me toward _double_. I ended up picking double, but I regret having to make that choice in the first place.

Conceptually, I'd like my numeric functions to work for anything that supports the basic arithmetic operators (i.e. +, -, *). Unfortunately that is not possible in .NET at this point in time. In essence you have to write your code twice as below.

<pre class="code"><span style="background:white;">   </span><span style="background:white;color:blue;">static double </span><span style="background:white;">SumDouble(</span><span style="background:white;color:blue;">double </span><span style="background:white;">a, </span><span style="background:white;color:blue;">double </span><span style="background:white;">b) { </span><span style="background:white;color:blue;">return </span><span style="background:white;">a + b; }
   </span><span style="background:white;color:blue;">static decimal </span><span style="background:white;">SumDecimal(</span><span style="background:white;color:blue;">decimal </span><span style="background:white;">a, </span><span style="background:white;color:blue;">decimal </span><span style="background:white;">b) {</span><span style="background:white;color:blue;">return </span><span style="background:white;">a + b;}</span></pre>



Granted, this is not a good state of affairs. We often discussed how to make it work, but we couldn't find a solution that was both fast to run and cheap for us to implement. More often than not we speculated about having the numeric types implement a specific _INumeric_ interface and add a generic constraint to the C#/VB languages to make it work. Hence the title of this post.

With we implemented _dynamic_ in C# 4.0 it occurred to me that you can fake your way into writing your code just once. For sure, this solution doesn't have the same performance characteristics of &#8216;writing your code twice', but at least it doesn't duplicate your code.

This is how it looks like:

<pre class="code"><span style="background:white;">    </span><span style="background:white;color:blue;">static dynamic </span><span style="background:white;">Sum1(</span><span style="background:white;color:blue;">dynamic </span><span style="background:white;">a, </span><span style="background:white;color:blue;">dynamic </span><span style="background:white;">b) { </span><span style="background:white;color:blue;">return </span><span style="background:white;">a + b; }</span></pre>

The call to the &#8216;+' operator is resolved at runtime, by the C# binder, hence a performance penalty is incurred. The penalty is less than you might think, given that the [DLR](http://www.codeplex.com/dlr) caches things under the cover so that no v-table lookup is performed the second time around. The whole thing is explained in more detail [here](http://blogs.msdn.com/cburrows/archive/2008/10/27/c-dynamic.aspx). But still, it is not as fast as a normal &#8216;+' operator over a primitive type. I'll let you enjoy micro performance testing this one 🙂

A slight refinement is to make the code generic so that a caller doesn't see a signature with dynamic types as arguments.

<pre class="code"><span style="background:white;">   </span><span style="background:white;color:blue;">static dynamic </span><span style="background:white;">Sum2&lt;T1, T2&gt;(T1 a, T2 b)
   {
       </span><span style="background:white;color:blue;">dynamic </span><span style="background:white;">ad = a;
       </span><span style="background:white;color:blue;">dynamic </span><span style="background:white;">bd = b;
       </span><span style="background:white;color:blue;">return </span><span style="background:white;">ad + bd;
   }</span></pre>

I could make the return type generic as well, but that would force the caller to be explicit about the types, making the calling code much less readable. The other good thing about this signature is that you get a different call site with each combination of type arguments and, since they are separate, the binding caches should stay small. With the former signature there is only one call site and the cache could pile up to the point where the DLR decides to discard it.

Here is how the calling code looks like right now:

<pre class="code"><span style="background:white;">       </span><span style="background:white;color:#2b91af;">Console</span><span style="background:white;">.WriteLine(Sum2(2m, 4m));
       </span><span style="background:white;color:#2b91af;">Console</span><span style="background:white;">.WriteLine(Sum2(2.0, 4.0));
       </span><span style="background:white;color:#2b91af;">Console</span><span style="background:white;">.WriteLine(Sum2(</span><span style="background:white;color:blue;">new </span><span style="background:white;color:#2b91af;">DateTime</span><span style="background:white;">(2000,12,1), </span><span style="background:white;color:blue;">new </span><span style="background:white;color:#2b91af;">TimeSpan</span><span style="background:white;">(24,0,0)));</span></pre>

Yet another way to write this code is as follows:

<pre class="code"><span style="background:white;">   </span><span style="background:white;color:blue;">public static </span><span style="background:white;">T Sum3&lt;T&gt;(T a, T b)
   {
       </span><span style="background:white;color:blue;">dynamic </span><span style="background:white;">ad = a;
       </span><span style="background:white;color:blue;">dynamic </span><span style="background:white;">bd = b;
       </span><span style="background:white;color:blue;">return </span><span style="background:white;">ad + bd;
   }</span></pre>

This gets around the problem of showing a dynamic return value and give you some more compile time type checking. But it prevents summing not coercible types. The compiler doesn't let you get there. The last line below wont' compile:

<pre class="code"><span style="background:white;">       </span><span style="background:white;color:#2b91af;">Console</span><span style="background:white;">.WriteLine(Sum3(2m, 4m));
       </span><span style="background:white;color:#2b91af;">Console</span><span style="background:white;">.WriteLine(Sum3(2.0, 4.0));
       </span><span style="background:white;color:green;">//Console.WriteLine(Sum3(new DateTime(2000,12,1), new TimeSpan(24,0,0)));</span></pre>



Also notice that in VB you could have done this a long time ago 🙂

<pre class="code"><span style="background:white;">   </span><span style="background:white;color:blue;">Function </span><span style="background:white;">Sum(Of T1, T2)(</span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">a </span><span style="background:white;color:blue;">As </span><span style="background:white;color:#2b91af;">T1</span><span style="background:white;">, </span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">b </span><span style="background:white;color:blue;">As </span><span style="background:white;color:#2b91af;">T2</span><span style="background:white;">)
       </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">aa </span><span style="background:white;color:blue;">As Object </span><span style="background:white;">= a
       </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">bb </span><span style="background:white;color:blue;">As Object </span><span style="background:white;">= b
       </span><span style="background:white;color:blue;">Return </span><span style="background:white;">aa + bb
   </span><span style="background:white;color:blue;">End Function</span></pre>

In summary, by using dynamic you can write your numeric code just once, but you pay a performance price. You are the only one who can decide if the price is worth paying in your particular application. As often, the profiler is your friend.