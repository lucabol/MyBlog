---
id: 643
title: 'Parsing QIF Quicken files in C#'
date: 2007-08-31T16:43:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/08/31/parsing-qif-quicken-files-in-c/
permalink: /2007/08/31/parsing-qif-quicken-files-in-c/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/08/31/parsing-qif-quicken-files-in-c.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "4675458"
orig_parent_id:
  - "4675458"
orig_thread_id:
  - "532924"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/08/31/parsing-qif-quicken-files-in-c.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Parsing QIF Quicken files in C#" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/08/31/parsing-qif-quicken-files-in-c/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="I'm slightly prouder of the structure of this code than&nbsp;the&nbsp;one in the previous blog post. You can simply inherit from QIFParserBase and override a couple of abstract methods to customize the behavior. Still, I just tested it on a couple of test QIF files. It is not production quality at all. Notice that I don't..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Parsing QIF Quicken files in C#" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/08/31/parsing-qif-quicken-files-in-c/" />
    <meta name="twitter:description" content="I'm slightly prouder of the structure of this code than&nbsp;the&nbsp;one in the previous blog post. You can simply inherit from QIFParserBase and override a couple of abstract methods to customize the behavior. Still, I just tested it on a couple of test QIF files. It is not production quality at all. Notice that I don't..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - 'C#'
  - Financial
---
I'm slightly prouder of the structure of this code than&nbsp;the&nbsp;one in [the previous blog post](http://blogs.msdn.com/lucabol/archive/2007/08/30/retrieve-prices-dividends-and-splits-for-a-stock-in-c.aspx). You can simply inherit from QIFParserBase and override a couple of abstract methods to customize the behavior. Still, I just tested it on a couple of test QIF files. It is not production quality at all.

Notice that I don't even have Quicken. I'm producing these test file with [FundManager](http://www.fundmanagersoftware.com/), which I use for my investments. If your software generates QIF files differently, than you have to modify the code. It shouldn't be too hard.

It works with [VS 2008 beta 2](http://msdn2.microsoft.com/en-us/vstudio/aa700831.aspx).

[ParseQIF.zip](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/04/67/54/58/ParseQIF.zip)