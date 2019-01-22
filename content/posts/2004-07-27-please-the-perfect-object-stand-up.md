---
id: 1043
title: Please the perfect object stand up!!
date: 2004-07-27T15:21:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2004/07/27/please-the-perfect-object-stand-up/
permalink: /2004/07/27/please-the-perfect-object-stand-up/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2004/07/27/199102.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "199102"
orig_parent_id:
  - "199102"
orig_thread_id:
  - "199102"
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
  - http://blogs.msdn.com/b/lucabol/archive/2004/07/27/please-the-perfect-object-stand-up.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Please the perfect object stand up!!" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2004/07/27/please-the-perfect-object-stand-up/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="I always thought: why people write this very long posts? Here you have it. &nbsp; How do I design my objects? What is the set of constraints that dictate my design decisions? People talk about objects in very different contexts. A certain amount of confusion derives from not identifying the contexts for our objects. &nbsp;..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Please the perfect object stand up!!" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2004/07/27/please-the-perfect-object-stand-up/" />
    <meta name="twitter:description" content="I always thought: why people write this very long posts? Here you have it. &nbsp; How do I design my objects? What is the set of constraints that dictate my design decisions? People talk about objects in very different contexts. A certain amount of confusion derives from not identifying the contexts for our objects. &nbsp;..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - 'C# Programming'
  - Object Orientation
---
<p class="MsoNormal" style="margin:0;">
  I always thought: why people write this very long posts? Here you have it.
</p>

<p class="MsoNormal" style="margin:0;">
  &nbsp;
</p>

<p class="MsoNormal" style="margin:0;">
  How do I design my objects? What is the set of constraints that dictate my design decisions? People talk about objects in very different contexts. A certain amount of confusion derives from not identifying the contexts for our objects.
</p>

<p class="MsoNormal" style="margin:0;">
  &nbsp;
</p>

<p class="MsoNormal" style="margin:0;">
  First, kings of them all, there are business objects. My library is full of OO books that describe how to design these guys. We have patterns and anti-patterns. Everybody is out there promoting their own methodology. But if we go deep enough, the most important design task in creating them is assigning responsibilities. This concept is as old as OO itself; it finds its roots in CRC cards. But I digress. Once again, when you design your business objects you have to be very careful to assign responsibilities to the objects that have the right information to perform them.
</p>

<p class="MsoNormal" style="margin:0;">
  &nbsp;
</p>

<p class="MsoNormal" style="margin:0;">
  It would be nice if this was all you have to code. A crazy bigot (like me) would think that all the rest is infrastructure (ala <a href="http://www.nakedobjects.org/">naked objects</a>). But we live in the real world, so let's get down to it.
</p>

<p class="MsoNormal" style="margin:0;">
  &nbsp;
</p>

<p class="MsoNormal" style="margin:0;">
  A second category of objects I often encounter are network objects. These are the guys you use to communicate data across tiers (logical, physical, webservices). They are usually quite dumb objects, not too much logic in them (if any), and your application creates them by filling their properties from the more noble business objects. Something along the line of the <a href="http://java.sun.com/blueprints/corej2eepatterns/Patterns/TransferObject.html">value object pattern</a>. Is assigning responsibilities a very important task here? Heck no!! They don't even have methods!! The most important characteristic they have is bandwidth optimization; you want to retrieve a whole bunch of stuff in one single round trip. More often than not you sacrifice everything else (manageability, good design) to achieve that.
</p>

<p class="MsoNormal" style="margin:0;">
  &nbsp;
</p>

<p class="MsoNormal" style="margin:0;">
  This is why I don't believe the quite common ideal of remoting your business objects. The set of constraints you use to design them is completely different (often opposite) to the constraints needed to go over the wire. When anything goes over the wire it becomes just data. Moreover not all of your business state needs to go on the network, but this is another story
</p>

<p class="MsoNormal" style="margin:0;">
  &nbsp;
</p>

<p class="MsoNormal" style="margin:0;">
  Another common object category is database objects. There is a big debate if they are the same as business objects or not. I dont' want to go there, but If you want them to be the same you usually pragmatically sacrifice a bit of OO purity to make them more similar to the database tables (you don't want to fight your object relational mapping layer, you want to help it out). To say this in a more positive way, you design your domain model with an eye on how you are going to persist it. If, on the other end, you are willing to create a separate set of objects to represent data coming from the database, then the main constraint for these guys is the same as your database tables: normalization. This is not surprising as they are mirrors of your database. Again assigning responsibilities and being network friendly take the back seat in this case.
</p>

<p class="MsoNormal" style="margin:0;">
  &nbsp;
</p>

<p class="MsoNormal" style="margin:0;">
  There are many other object categories I often found useful (i.e. fa&#231;ade objects). I don't want to discuss all of them here. Things are already boring as they are. The central point is that it is very hard to&nbsp;define generic guidelines that work well in all the different contexts. You got to think about your context first.
</p>

<p class="MsoNormal" style="margin:0;">
  &nbsp;
</p>

<p class="MsoNormal" style="margin:0;">
  The funny thing is that I work in a place where we are supposed to design features that are generically interesting in all these scenarios. You use C# to code all of them. Oh well, design is the art of choosing trade offs
</p>