---
id: 303
title: New release of Financial Functions .NET uploaded on MSDN Code Gallery
date: 2009-01-27T14:18:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/01/27/new-release-of-financial-functions-net-uploaded-on-msdn-code-gallery/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/01/27/new-release-of-financial-functions-net-uploaded-on-msdn-code-gallery.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9376122"
orig_parent_id:
  - "9376122"
orig_thread_id:
  - "631837"
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
  - http://blogs.msdn.com/b/lucabol/archive/2009/01/27/new-release-of-financial-functions-net-uploaded-on-msdn-code-gallery.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="New release of Financial Functions .NET uploaded on MSDN Code Gallery" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/01/27/new-release-of-financial-functions-net-uploaded-on-msdn-code-gallery/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="I fixed the bug described in this thread and cleaned up the root finding algorithm. I’m still unhappy about it, but I have no time to code a better one right now (i.e. Ridder, Brent). I also added changes.txt and todo.txt to keep track of things. Changes.txt V1 1. Fixed call to throw in bisection..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="New release of Financial Functions .NET uploaded on MSDN Code Gallery" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/01/27/new-release-of-financial-functions-net-uploaded-on-msdn-code-gallery/" />
    <meta name="twitter:description" content="I fixed the bug described in this thread and cleaned up the root finding algorithm. I’m still unhappy about it, but I have no time to code a better one right now (i.e. Ridder, Brent). I also added changes.txt and todo.txt to keep track of things. Changes.txt V1 1. Fixed call to throw in bisection..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - fsharp
  - Financial
---
I fixed the bug described in [this](https://code.msdn.microsoft.com/Thread/View.aspx?ProjectName=FinancialFunctions&ThreadId=1060) thread and cleaned up the root finding algorithm. I’m still unhappy about it, but I have no time to code a better one right now (i.e. Ridder, Brent). I also added changes.txt and todo.txt to keep track of things.

_<u>Changes.txt</u>_

V1   
1. Fixed call to throw in bisection   
2. Changed findBounds algo   
3. Added TestXirrBugs function   
4. Removed the NewValue functions everywhere

_<u>ToDo.txt</u>_

1. The interaction of Bisection and Newton algo in findRoot needs review. It seems like it is working now, but it could use some love. Maybe I should switch to a better root finding algo (i.e. Rudder or Brent)