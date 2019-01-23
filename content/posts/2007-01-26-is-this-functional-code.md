---
id: 823
title: Is this functional code?
date: 2007-01-26T12:54:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/01/26/is-this-functional-code/
permalink: /2007/01/26/is-this-functional-code/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/01/26/is-this-functional-code.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "1537558"
orig_parent_id:
  - "1537558"
orig_thread_id:
  - "492225"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/01/26/is-this-functional-code.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Is this functional code?" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/01/26/is-this-functional-code/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="&nbsp; I'm an Object Oriented (OO)&nbsp;kind of guy, maybe a bigot.&nbsp;I have read a very large number of OO books and I've written a fair amount of OO code in my 10+ years in this industry. I'm afraid my mind is wired for OO at this point, for good or bad. Recently, I've been&nbsp;getting interested..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Is this functional code?" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/01/26/is-this-functional-code/" />
    <meta name="twitter:description" content="&nbsp; I'm an Object Oriented (OO)&nbsp;kind of guy, maybe a bigot.&nbsp;I have read a very large number of OO books and I've written a fair amount of OO code in my 10+ years in this industry. I'm afraid my mind is wired for OO at this point, for good or bad. Recently, I've been&nbsp;getting interested..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - 'C#'
---

I'm an Object Oriented (OO) kind of guy, maybe a bigot. I have read a very large number of OO books and I've written a fair amount of OO code in my 10+ years in this industry. I'm afraid my mind is wired for OO at this point, for good or bad.

Recently, I've been getting interested in functional languages. The most functional guys around here are Wes and Luke, while Dr. T has somehow transcended the whole thing.

Here is the text of one of my newbie emails to Dr.T. I'll let you think about it for a bit before posting his reply. The phrase: "Is this it?" has to be read as "Is this what functional programming is all about?".

/// EMAIL TEXT BELOW

Is this it? I have about four of these ‘delegate taking’ functions in my excel addin ….
~~~csharp
    delegate bool PredWithPrevious<T>(T value, T previous);
static int CountWithPrevious<T>(IEnumerable<T> en, PredWithPrevious<T> pred) {

int count = 0;
T previous = default(T);
bool isPrevious = false;

foreach (T val in en) {

if (isPrevious)
if (pred(val, previous))
count++;
previous = val;
isPrevious = true;
}
return count;
}
~~~