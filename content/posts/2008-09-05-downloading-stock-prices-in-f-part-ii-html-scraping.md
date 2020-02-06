---
id: 433
title: 'Downloading stock prices in F# - Part II - Html scraping'
date: 2008-09-05T14:41:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/09/05/downloading-stock-prices-in-f-part-ii-html-scraping/
permalink: /2008/09/05/downloading-stock-prices-in-f-part-ii-html-scraping/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/09/05/downloading-stock-prices-in-f-part-ii-html-scraping.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "8926690"
orig_parent_id:
  - "8926690"
orig_thread_id:
  - "604540"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/09/05/downloading-stock-prices-in-f-part-ii-html-scraping.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Downloading stock prices in F#  - Part II  - Html scraping" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/09/05/downloading-stock-prices-in-f-part-ii-html-scraping/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other parts: Part I  - Data modeling Part III  - Async loader for prices and divs Part IV  - Async loader for splits Part V  - Adjusting historical data Part VI  - Code posted Getting stock prices and dividends is relatively easy given that, on Yahoo, you can get the info as a CVS file...." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Downloading stock prices in F#  - Part II  - Html scraping" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/09/05/downloading-stock-prices-in-f-part-ii-html-scraping/" />
    <meta name="twitter:description" content="Other parts: Part I  - Data modeling Part III  - Async loader for prices and divs Part IV  - Async loader for splits Part V  - Adjusting historical data Part VI  - Code posted Getting stock prices and dividends is relatively easy given that, on Yahoo, you can get the info as a CVS file...." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - fsharp
---
Other parts:

  * [Part I  - Data modeling](http://blogs.msdn.com/lucabol/archive/2008/08/29/downloading-stock-prices-in-f-part-i-data-modeling.aspx)
  * [Part III  - Async loader for prices and divs](http://blogs.msdn.com/lucabol/archive/2008/09/12/downloading-stock-prices-in-f-part-iii-async-loader-for-prices-and-divs.aspx)
  * [Part IV  - Async loader for splits](http://blogs.msdn.com/lucabol/archive/2008/09/19/downloading-stock-prices-in-f-part-iv-async-loader-for-splits.aspx)
  * [Part V  - Adjusting historical data](http://blogs.msdn.com/lucabol/archive/2008/09/26/downloading-stock-prices-in-f-part-v-adjusting-historical-data.aspx)
  * [Part VI  - Code posted](http://blogs.msdn.com/lucabol/archive/2008/10/20/downloading-stock-prices-in-f-part-vi-code-posted.aspx)

Getting stock prices and dividends is relatively easy given that, on [Yahoo](http://finance.yahoo.com/q/hp?s=GE), you can get the info [as a CVS file](http://ichart.finance.yahoo.com/table.csv?s=GE&a=00&b=2&c=1962&d=08&e=5&f=2008&g=d&ignore=.csv). Getting the splits info is harder. You would think that Yahoo would put that info in the dividends CVS as it does when it displays it on screen, but it doesn't. So I had to write code to scrap it from the multiple web pages where it might reside. In essence, I'm scraping [this](http://finance.yahoo.com/q/hp?s=GE&a=00&b=2&c=1962&d=08&e=5&f=2008&g=v).

**<u>html.fs</u>**

In this file there are utility functions that I will use later on to retrieve split info. 

<pre class="code"><span style="color:blue;">#light
open </span>System
<span style="color:blue;">open </span>System.IO
<span style="color:blue;">open </span>System.Text.RegularExpressions
<span style="color:green;">// It assumes no table inside table ...
</span><span style="color:blue;">let </span>tableExpr = <span style="color:maroon;">"&lt;table[^&gt;]*&gt;(.*?)&lt;/table&gt;"
</span><span style="color:blue;">let </span>headerExpr = <span style="color:maroon;">"&lt;th[^&gt;]*&gt;(.*?)&lt;/th&gt;"
</span><span style="color:blue;">let </span>rowExpr = <span style="color:maroon;">"&lt;tr[^&gt;]*&gt;(.*?)&lt;/tr&gt;"
</span><span style="color:blue;">let </span>colExpr = <span style="color:maroon;">"&lt;td[^&gt;]*&gt;(.*?)&lt;/td&gt;"
</span><span style="color:blue;">let </span>regexOptions = RegexOptions.Multiline ||| RegexOptions.Singleline <br />                                          ||| RegexOptions.IgnoreCase</pre>

This code is straightforward enough (if you know what Regex does). I'm sure that there are better expression to scrap tables and rows on the web, but these work in my case. I really don't need to scrape tables. I put the table expression there in case you need it.

I then write code to scrape all the cells in a piece of html:

<pre class="code"><span style="color:blue;">let </span>scrapHtmlCells html =
  seq { <span style="color:blue;">for </span>x <span style="color:blue;">in </span>Regex.Matches(html, colExpr, regexOptions) <span style="color:blue;">-&gt; </span>x.Groups.Item(1).ToString()}            </pre>

This is a sequence expression. Sequence expressions are used to generate sequences starting from some expression (as the name hints to). In this case <u>Regex.Matches</u> returns a <u>MatchClollection</u>, which is a non-generic <u>IEnumerable</u>. For each element in it, we return the value of the first match. We could as easily have constructed a list or an array, given that there is not much deferred computation going on. But oh well

Always check the type of your functions in F#! With type inference it is easy to get it wrong. Hovering your mouse on top of it in VS shows it. This one is typed: <u>string -> seq<string></u>. It takes a string (html) and return a sequence of strings (the cells in html).

We'll need rows as well.

<pre class="code"><span style="color:blue;">let </span>scrapHtmlRows html =
    seq { <span style="color:blue;">for </span>x <span style="color:blue;">in </span>Regex.Matches(html, rowExpr, regexOptions) <span style="color:blue;">-&gt; </span>scrapHtmlCells x.Value }</pre>

This works about the same. I'm matching all the rows and retrieving the cells for each one of them. I'm getting back a matrix-like structure, that is to say that this function as type: <u>string -> seq<seq<string>></u>.

That's all for today. In the next installment we'll make it happen.