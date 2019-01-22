---
id: 803
title: 'Apparently simple code'
date: 2007-02-01T14:54:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/02/01/apparently-simple-code/
permalink: /2007/02/01/apparently-simple-code/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/02/01/apparently-simple-code.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "1574979"
orig_parent_id:
  - "1574979"
orig_thread_id:
  - "493385"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/02/01/apparently-simple-code.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Apparently simple code" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/02/01/apparently-simple-code/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Sometimes what looks simple is complex and what looks complex is simple. See if you can understand how this one calculates all the possible ways to give change for a certain amount of money given some kinds of coins. You MIT guys out there don't count, you probably have read the solution in the same..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Apparently simple code" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/02/01/apparently-simple-code/" />
    <meta name="twitter:description" content="Sometimes what looks simple is complex and what looks complex is simple. See if you can understand how this one calculates all the possible ways to give change for a certain amount of money given some kinds of coins. You MIT guys out there don't count, you probably have read the solution in the same..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - 'C# Programming'
---
Sometimes what looks simple is complex and what looks complex is simple. See if you can understand how this one calculates all the possible ways to give change for a certain amount of money given some kinds of coins. You MIT guys out there don't count, you probably have read the solution in the same book I have.

BTW: the code works with the LINQ May CTP ...

~~~csharp
using System;

using System.Collections.Generic;

using System.Text;

using System.Query;

using System.Xml.XLinq;
class Program
{
static void Main(string[] args)
{
var coins = new int[] { 1, 5, 10, 25, 50 };

var i = ChangeComb(100, coins);
Console.WriteLine(i);
}

static int ChangeComb(int amount, IEnumerable<int> coins)
{
if (amount == 0) return 1;
if (amount < 0) return 0;
if (coins.Count() == 0) return 0;

return ChangeComb(amount, coins.Skip(1)) +
ChangeComb(amount - coins.First(), coins);
}
}
~~~