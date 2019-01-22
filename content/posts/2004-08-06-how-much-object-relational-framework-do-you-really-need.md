---
id: 973
title: How much object relational framework do you really need?
date: 2004-08-06T09:05:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2004/08/06/how-much-object-relational-framework-do-you-really-need/
permalink: /2004/08/06/how-much-object-relational-framework-do-you-really-need/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2004/08/06/209931.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "209931"
orig_parent_id:
  - "209931"
orig_thread_id:
  - "209931"
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
  - http://blogs.msdn.com/b/lucabol/archive/2004/08/06/how-much-object-relational-framework-do-you-really-need.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="How much object relational framework do you really need?" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2004/08/06/how-much-object-relational-framework-do-you-really-need/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="It is always interesting for me to look at debates about object relational layers. I propose we define different levels of object relational support: No support: all the objects are persisted and queried by writing ADO.NET code by hand Code generation: you run a tool on your database (or on an abstract description of your..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="How much object relational framework do you really need?" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2004/08/06/how-much-object-relational-framework-do-you-really-need/" />
    <meta name="twitter:description" content="It is always interesting for me to look at debates about object relational layers. I propose we define different levels of object relational support: No support: all the objects are persisted and queried by writing ADO.NET code by hand Code generation: you run a tool on your database (or on an abstract description of your..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - 'C# Programming'
  - Object Orientation
---
It is always interesting for me to look at debates about object relational layers. I propose we define different levels of object relational support:

  1. No support: all the objects are persisted and queried by writing ADO.NET code by hand
  2. Code generation: you run a tool on your database (or on an abstract description of your schema)&nbsp;and the tool generates a bunch of objects for your tables and some ADO.NET code to retrieve/persist their state
  1. Total code gen: the tool generates all the ADO.NET code
  2. Partial code gen: the tool generates just code to intercept property accessors and provide delay loading, but all the data access code is in a separate compiled component

  3. Metadata based: no code generation phase. The access to fields and property goes through reflection and the data access code is not exposed in the user code
  1. Semi transparent: the persistent classes or properties need to be marked in some special way to be persisted (attributes, inherit from a special class or such)
  2. Transparent: the classes don't need to be modified at all to be persisted

Things get fuzzy, though. It is sometime unclear the difference between 2.2 and 3.1 and&nbsp;various creative solutions can be hard to classify. But in a general sense,&nbsp;this classification is probably about right.&nbsp;In a generic sense EJB1.1-2.0 is a 2.2, EJB3.0 is a 3.1, JDO is 3.2 (if you don't consider post-compilation) and ObjectSpaces is a 3.2. Hibernate and Toplink are squarely 3.2.

But do you really need to go all the way to 3.2? All the times? I'll try to post more about trade-offs in all these solutions, but if you have an idea of a better categorization, please let me know. The one I propose is right out of my head and I'm not to happy about it either.