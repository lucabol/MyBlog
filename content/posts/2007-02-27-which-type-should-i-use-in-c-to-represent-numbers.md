---
id: 783
title: 'Which type should I use in C# to represent numbers?'
date: 2007-02-27T18:09:57+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/02/27/which-type-should-i-use-in-c-to-represent-numbers/
permalink: /2007/02/27/which-type-should-i-use-in-c-to-represent-numbers/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/02/27/which-type-should-i-use-in-c-to-represent-numbers.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "1771165"
orig_parent_id:
  - "1771165"
orig_thread_id:
  - "498306"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/02/27/which-type-should-i-use-in-c-to-represent-numbers.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Which type should I use in C# to represent numbers?" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/02/27/which-type-should-i-use-in-c-to-represent-numbers/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Yesterday I found an old email in my mail box that I thought might be generally interesting. I was asking&nbsp;the&nbsp;technical lead&nbsp;on the C# compiler which algorithm/shortcut people should use to choose their &#8216;number types' among the many available in the language. I was asking for something that works the majority of times, even if not..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Which type should I use in C# to represent numbers?" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/02/27/which-type-should-i-use-in-c-to-represent-numbers/" />
    <meta name="twitter:description" content="Yesterday I found an old email in my mail box that I thought might be generally interesting. I was asking&nbsp;the&nbsp;technical lead&nbsp;on the C# compiler which algorithm/shortcut people should use to choose their &#8216;number types' among the many available in the language. I was asking for something that works the majority of times, even if not..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - 'C# Programming'
---
Yesterday I found an old email in my mail box that I thought might be generally interesting.

I was asking&nbsp;the&nbsp;technical lead&nbsp;on the C# compiler which algorithm/shortcut people should use to choose their &#8216;number types' among the many available in the language. I was asking for something that works the majority of times, even if not always. I'm sure there are other scenarios we haven't consider. Anyhow, here is his algorithm.

If you need fractions: 

  * Use decimal when intermediate results need to be rounded to fixed precision  - this is almost always limited to calculations involving money.
  * Otherwise use double  - you will get the rounding of your calculations wrong, but the extra precision of double will ensure that your results will be good enough.
  * Only use float if you know you have a space issue, and you know the precision implications. If you don't have a PhD in numeric computation you don't qualify.

Otherwise: 

  * Use int whenever your values can fit in an int, even for values which can never be negative. This is so that subtraction operations don't get you confused.
  * Use long when your values can't fit in an int.

Byte, sbyte, short, ushort, uint, and ulong should only ever be used for interop with C code. Otherwise they're not worth the hassle.