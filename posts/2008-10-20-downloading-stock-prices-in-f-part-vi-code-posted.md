---
id: 393
title: 'Downloading stock prices in F# - Part VI - Code posted'
date: 2008-10-20T18:45:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/10/20/downloading-stock-prices-in-f-part-vi-code-posted/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/10/20/downloading-stock-prices-in-f-part-vi-code-posted.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9008275"
orig_parent_id:
  - "9008275"
orig_thread_id:
  - "612956"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/10/20/downloading-stock-prices-in-f-part-vi-code-posted.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Downloading stock prices in F#  - Part VI  - Code posted" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/10/20/downloading-stock-prices-in-f-part-vi-code-posted/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other parts: Part I  - Data modeling Part II  - Html scraping Part III  - Async loader for prices and divs Part IV  - Async loader for splits Part V  - Adjusting historical data An unnamed friend told me that I should stop posting small snippets of code and instead post entire solutions on CodeGallery...." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Downloading stock prices in F#  - Part VI  - Code posted" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/10/20/downloading-stock-prices-in-f-part-vi-code-posted/" />
    <meta name="twitter:description" content="Other parts: Part I  - Data modeling Part II  - Html scraping Part III  - Async loader for prices and divs Part IV  - Async loader for splits Part V  - Adjusting historical data An unnamed friend told me that I should stop posting small snippets of code and instead post entire solutions on CodeGallery...." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - fsharp
  - Financial
---
Other parts:

  * [Part I  - Data modeling](http://blogs.msdn.com/lucabol/archive/2008/08/29/downloading-stock-prices-in-f-part-i-data-modeling.aspx)
  * [Part II  - Html scraping](http://blogs.msdn.com/lucabol/archive/2008/09/05/downloading-stock-prices-in-f-part-ii-html-scraping.aspx)
  * [Part III  - Async loader for prices and divs](http://blogs.msdn.com/lucabol/archive/2008/09/12/downloading-stock-prices-in-f-part-iii-async-loader-for-prices-and-divs.aspx)
  * [Part IV  - Async loader for splits](http://blogs.msdn.com/lucabol/archive/2008/09/19/downloading-stock-prices-in-f-part-iv-async-loader-for-splits.aspx)
  * [Part V  - Adjusting historical data](http://blogs.msdn.com/lucabol/archive/2008/09/26/downloading-stock-prices-in-f-part-v-adjusting-historical-data.aspx)

[An unnamed friend](http://blogs.msdn.com/lukeh/default.aspx) told me that I should stop posting small snippets of code and instead post entire solutions on [CodeGallery](http://code.msdn.microsoft.com/). I did it for this one and [here](http://code.msdn.microsoft.com/DownloadStockPrices) is the link.

Here is what's in the zip file:

  * **BackTestF**  - main library to download stock prices
  * Common.fs  - common things used in the rest of the project (i.e. data modeling and common funcs)
  * html.fs  - functions to scrap html tables, rows and cells
  * loader.fs  - this is where the main async downloading algorithms are implemented
  * persistence.fs  - async saving and loading of stock prices to files
  * algorithms.fs  - async calculations of compound yearly returns given tickers and dates
  * dotNetWrapper.fs  - gives a .NET friendly interface to the whole library so that you can use it from C#/VB.NET

  * **Tests**  - too few testcases running on xUnit (you need to download xUnit separately to run them
  * **ReturnCalculator**  - simple console application to show usage of the library
  * **Bob**  - rough winforms UI application that uses the library. An unnamed friend ([Jonathan](http://msdn.microsoft.com/en-us/vbasic/bb735849.aspx)) promised me that he was going to create a UI for my little library. My requirements were very simple: I want the best UI app of this century, one that fully takes advantage of the async nature of my code. Bob doesn't fully satisfy my requirements yet 🙂

The code in persistence.fs, algorithms.fs and especially dotnetwrapper.fs is pretty rough and uninteresting. This is why I don't blog about it. I reserve the right to do it if I get around to clean it up.