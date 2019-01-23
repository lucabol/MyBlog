---
id: 663
title: 'Retrieve prices, dividends and splits for a stock in C#'
date: 2007-08-30T16:25:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/08/30/retrieve-prices-dividends-and-splits-for-a-stock-in-c/
permalink: /2007/08/30/retrieve-prices-dividends-and-splits-for-a-stock-in-c/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/08/30/retrieve-prices-dividends-and-splits-for-a-stock-in-c.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "4654000"
orig_parent_id:
  - "4654000"
orig_thread_id:
  - "532738"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/08/30/retrieve-prices-dividends-and-splits-for-a-stock-in-c.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Retrieve prices, dividends and splits for a stock in C#" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/08/30/retrieve-prices-dividends-and-splits-for-a-stock-in-c/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="I wrote this code very quickly and I'm kind of ashamed of it, but it gets the job done (I think). You need the HTML Agility Pack for the stock splits retrieving code. You can download it from here&nbsp;or you can simply comment out the code. I wrote it against Visual Studio 2008 beta 2,..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Retrieve prices, dividends and splits for a stock in C#" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/08/30/retrieve-prices-dividends-and-splits-for-a-stock-in-c/" />
    <meta name="twitter:description" content="I wrote this code very quickly and I'm kind of ashamed of it, but it gets the job done (I think). You need the HTML Agility Pack for the stock splits retrieving code. You can download it from here&nbsp;or you can simply comment out the code. I wrote it against Visual Studio 2008 beta 2,..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - 'C#'
  - Financial
---
I wrote this code very quickly and I'm kind of ashamed of it, but it gets the job done (I think). You need the HTML Agility Pack for the stock splits retrieving code. You can download it from [here](http://www.codeplex.com/htmlagilitypack/Release/ProjectReleases.aspx?ReleaseId=272){.}&nbsp;or you can simply comment out the code. I wrote it against [Visual Studio 2008 beta 2](http://msdn2.microsoft.com/en-us/vstudio/aa700831.aspx){.}, but it should be trivial to port it to previous versions.

You run it from a command window like this: priceretriever msft 1/1/1990 2/3/2003. The last two parameters are optional and default to 1/1/1980 and today.

Enjoy.

[PriceRetriever.zip](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/04/65/40/00/PriceRetriever.zip)