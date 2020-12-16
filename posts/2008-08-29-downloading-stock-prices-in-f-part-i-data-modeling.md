---
id: 443
title: 'Downloading stock prices in F# - Part I - Data modeling'
date: 2008-08-29T19:13:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/08/29/downloading-stock-prices-in-f-part-i-data-modeling/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/08/29/downloading-stock-prices-in-f-part-i-data-modeling.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "8907294"
orig_parent_id:
  - "8907294"
orig_thread_id:
  - "603239"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/08/29/downloading-stock-prices-in-f-part-i-data-modeling.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Downloading stock prices in F#  - Part I  - Data modeling" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/08/29/downloading-stock-prices-in-f-part-i-data-modeling/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other parts: Part II  - Html scraping Part III  - Async loader for prices and divs Part IV  - Async loader for splits Part V  - Adjusting historical data Part VI  - Code posted Today we shipped the September CTP of F# !!!! Evviva !! Read this blog post about it. To celebrate I decided..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Downloading stock prices in F#  - Part I  - Data modeling" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/08/29/downloading-stock-prices-in-f-part-i-data-modeling/" />
    <meta name="twitter:description" content="Other parts: Part II  - Html scraping Part III  - Async loader for prices and divs Part IV  - Async loader for splits Part V  - Adjusting historical data Part VI  - Code posted Today we shipped the September CTP of F# !!!! Evviva !! Read this blog post about it. To celebrate I decided..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - fsharp
---
Other parts:

  * [Part II  - Html scraping](http://blogs.msdn.com/lucabol/archive/2008/09/05/downloading-stock-prices-in-f-part-ii-html-scraping.aspx) 
  * [**<font color="#006bad">Part III  - Async loader for prices and divs</font>**](http://blogs.msdn.com/lucabol/archive/2008/09/12/downloading-stock-prices-in-f-part-iii-async-loader-for-prices-and-divs.aspx)
  * [Part IV  - Async loader for splits](http://blogs.msdn.com/lucabol/archive/2008/09/19/downloading-stock-prices-in-f-part-iv-async-loader-for-splits.aspx)
  * [Part V  - Adjusting historical data](http://blogs.msdn.com/lucabol/archive/2008/09/26/downloading-stock-prices-in-f-part-v-adjusting-historical-data.aspx)
  * [Part VI  - Code posted](http://blogs.msdn.com/lucabol/archive/2008/10/20/downloading-stock-prices-in-f-part-vi-code-posted.aspx)

Today we shipped the September CTP of F# !!!! Evviva !! Read [this](http://blogs.msdn.com/dsyme/archive/2008/08/29/the-f-september-2008-ctp-is-now-available.aspx) blog post about it. To celebrate I decided to share one of my several F# project. It might make for a good sample; sort of a crash course on F#.

This application downloads stock prices, dividends and splits from [Yahoo Historical Prices](http://finance.yahoo.com/q/hp?s=MSFT) and performs computations on them. I will describe it file by file.

<u>**common.fs**</u>

I always have such a file in my projects. It is a repository for the types that I'm going to use in my program and the functions that are common across multiple modules. If I have a large program I also have a types.fs just for the types.

This one starts like this:

<pre class="code"><span style="color:blue;">#light
open </span>System
[&lt;Measure&gt;] <span style="color:blue;">type </span>money
<span style="color:blue;">let </span>money (f:float) = f * 1.&lt;money&gt;
[&lt;Measure&gt;] <span style="color:blue;">type </span>shares
<span style="color:blue;">let </span>shares (f:float) = f * 1.&lt;shares&gt;
[&lt;Measure&gt;] <span style="color:blue;">type </span>volume
<span style="color:blue;">let </span>volume (f:float) = f * 1.&lt;volume&gt;
[&lt;Measure&gt;] <span style="color:blue;">type </span>rateOfReturn
<span style="color:blue;">let </span>rateOfReturn (f:float) = f * 1.&lt;rateOfReturn&gt;</pre>



<p align="left">
  The first line instructs the compiler to use the lightweight syntax. You don't want to know what the heavyweight syntax is. Just always put such a line at the start of your files. The next line opens up the System namespace. Then the good stuff starts.
</p>

I'm defining some units of measures. The simplest way to think about units of measures is: they are a type system for floats. You can do much more than that, but it is a good first approximation. For example, you cannot now sum a <u>money</u> type and a <u>volume</u> type. Also for each one I define a function that converts from a normal <u>float</u> type to it (if you come from a C# background, floats are doubles).

Then I define the data model for my application:

<pre class="code"><span style="color:blue;">type </span>Span = { Start: DateTime; End: DateTime }
<span style="color:blue;">type </span>Price = { Open: float&lt;money&gt;; High: float&lt;money&gt;; Low:float&lt;money&gt;; <br />                                                Close:float&lt;money&gt;; Volume: float&lt;volume&gt;}
<span style="color:blue;">type </span>Event =
    | Price <span style="color:blue;">of </span>Price
    | Split <span style="color:blue;">of </span>float
    | Div <span style="color:blue;">of </span>float&lt;money&gt;
<span style="color:blue;">type </span>Observation = { Date: DateTime; Event: Event}</pre>

The first record that I define, <u>Span</u>,&nbsp; represents the difference between two dates. It is just a little useful thing. A more fundamental record is <u>Observation</u>. An <u>Observation</u> is defined as something that happens on a particular <u>Date</u>. That something, an <u>Event</u>, can be one of three things: a <u>Price</u>, a <u>Split</u> or a <u>Div</u>. A <u>Price</u> is another record with a bunch of <u>float<money></u> fields and on <u>float<volume></u> field. If you go to the Yahoo site, you'll see what it represents.

A <u>Split</u> is simply a <u>float</u>. Why not a <u>float<></u>? Because it is just a number, a factor to be precise. It represents the number of new shares divided by the number of old shares. <u>float<shares> / float<shares> = float</u>. A <u>Div</u> is a <u>float<money></u>.

This is one way to model the problem. Infinite other ways are possible (and I tried many of them in a C# version of this code that ended up using polymorphism). Note that all of the types are records except <u>Event</u> that is a discriminated union.

Records are read only containers of data. Discriminated unions are what the name says: things that can be one of multiple things (even recursively). They are rather handy to represent the structure of the data. We will see how you use them using the <u>match</u> operator in upcoming posts.

Also notice the following common pattern in F# (and functional programming in general). You define your data and then you define transformations over it. F# has a third optional step, that is to expose these transformations as methods of a .NET objects.

We are almost done here. A handful of other functions are in my file :

<pre class="code"><span style="color:blue;">let </span>span sy sm sd ey em ed =<br />                   {Start = <span style="color:blue;">new </span>DateTime(sy, sm, sd); End = <span style="color:blue;">new </span>DateTime(ey, em, ed)}
<span style="color:blue;">let </span>date y m d = <span style="color:blue;">new </span>DateTime(y, m, d)
<span style="color:blue;">let </span>now () = DateTime.Now
<span style="color:blue;">let </span>idem x = x
<span style="color:blue;">let </span>someIdem x = Some(x)</pre>

<u>Span</u> is a function that creates a span given the relevant info. <u>date</u> creates a date given year, month and day. <u>now</u> is a value that corresponds to the current date. <u>idem</u> is a function that returns its parameter (you'll see how that can possibly be useful). <u>someIdem</u> is a function that unpack an Option type and gives his value. I could write all my code without these things, but it looks better (to me) with them.

Notice that in the F# code you have access to all the functions and type in the .NET framework. It is just another .NET language: it can create or consume .NET types.

All right, we are done for part one. In part II there will be some real code.