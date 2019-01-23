---
id: 723
title: 'ObjectSpaces early days'
date: 2007-06-07T10:40:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/06/07/objectspaces-early-days/
permalink: /2007/06/07/objectspaces-early-days/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/06/07/objectspaces-early-days.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "3142658"
orig_parent_id:
  - "3142658"
orig_thread_id:
  - "518019"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/06/07/objectspaces-early-days.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="ObjectSpaces early days" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/06/07/objectspaces-early-days/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Matt has a very good post on the history of object relational framework inside Microsoft. He and I started the whole ObjectSpaces thing together very many years ago (about six and a half). I thought I should add my two cents. &nbsp; You might be wondering how a project starts inside Microsoft (or you might..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="ObjectSpaces early days" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/06/07/objectspaces-early-days/" />
    <meta name="twitter:description" content="Matt has a very good post on the history of object relational framework inside Microsoft. He and I started the whole ObjectSpaces thing together very many years ago (about six and a half). I thought I should add my two cents. &nbsp; You might be wondering how a project starts inside Microsoft (or you might..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - 'C#'
---
<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">Matt has </font><a href="http://blogs.msdn.com/mattwar/archive/2007/05/31/the-origin-of-linq-to-sql.aspx"><font face="Tahoma" color="#0000ff">a very good post</font></a><font face="Tahoma"> on the history of object relational framework inside Microsoft. He and I started the whole ObjectSpaces thing together very many years ago (about six and a half). I thought I should add my two cents. <s></s></font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">&nbsp;</font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">You might be wondering how a project starts inside Microsoft (or you might not). In this case, I was hired in the ADO.NET team to build an object relational framework. That was my assignment. The problem was that I had no dev or tester to work with. I also had just arrived in the US from Italy and my English was terrible (that hasn’t changed much). My only qualifications for the job were that I was incredibly passionate about the topic; I had built a couple of small ones in my spare time and have used many more in various projects. But still I had no idea on how to make things happen in this big company. Hell, I could barely understand what people were talking about at lunch.</font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">&nbsp;</font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">Anyhow, my boss told me that there was a guy who was relatively free, but I had to come up with an idea, convince him that the idea was a good one and that he should go ahead and prototype it. That guy was Matt Warren, already one of the best developers in the SQL team and the dev lead of plenty of our .NET stack.</font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">&nbsp;</font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">The first time I entered his office and started talking, he immediately told me: “Not now, I’m debugging”. A good start … But after that, we hit it off immediately. We talked about what an OR framework is, what it should be, how we could innovate in the space and so on. After a while, Matt started working on the very first ObjectSpaces prototype. Our modus operandi was peculiar. I would go to Matt’s office and we would discuss a particular feature or scenario. He would tell me: “Ok, we are on the same page, I’ll see you tomorrow”. The next day the feature would be implemented. If he told me: “It is going to take me 5 days to code it” I knew he didn’t like the feature and I had some more convincing to do. Sometime we would agree, sometime we wouldn’t. Sometime I came up with staff to implement, sometimes Matt did. We figured out a lot of stuff in those days.</font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">&nbsp;</font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">Also I learned how to work with different categories of programmers. If you work with a bad programmer you have to tell him how to implement something. If you work with a good programmer you have to tell him what you want the feature to look like. If you work with an excellent programmer, you just have to tell him what your final goal is. I quickly realized that the latter was the most productive strategy with Matt. I had just to convince him of the business need for something. Implementing it ended up to be a detail.</font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">&nbsp;</font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">That initial prototype grew to become ObjectSpaces (it was called Cheops initially). The team grew to be about 25 people, growing and stretching me personally. We went through two painful rounds of unifications with bigger products. In the end ObjectSpaces was cut. Matt moved to the C# team to work on LINQ. Dinesh and I followed after a short while. The whole ObjectSpaces team scattered in various places around the company. The object relational thing started again in the C# team as part of the LINQ project. This time around we also had a compiler to play with. Plus Anders was on board to sprinkle his design magic over the whole thing.</font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">&nbsp;</font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">As </font><a href="http://en.wikipedia.org/wiki/The_Dark_Tower_(series)"><font face="Tahoma" color="#0000ff">Roland</font></a><font face="Tahoma"> would say, the world has moved on. Matt is now a big shot architect and I lead a team of amazingly smart individuals (they are forced to act as if my words make sense, imagine that …). We are shipping a game changing product in LINQ and a wonderful object relational framework in LINQ to SQL. Things turned out for the best (even if five years too late).</font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">&nbsp;</font>
</p>

<p class="MsoNormal" style="margin:0;">
  <font face="Tahoma">Still it is a pleasure to think back at those early days (and nights) of ‘figuring out stuff’ six years ago. A lot of that ‘stuff’ is inside our products today, and that is something to be proud of.</font>
</p>