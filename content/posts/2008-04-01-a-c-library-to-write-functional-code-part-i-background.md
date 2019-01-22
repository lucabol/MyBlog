---
id: 503
title: 'A C# library to write functional code - Part I - Background'
date: 2008-04-01T13:36:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/04/01/a-c-library-to-write-functional-code-part-i-background/
permalink: /2008/04/01/a-c-library-to-write-functional-code-part-i-background/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/04/01/a-c-library-to-write-functional-code-part-i-background.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "8348521"
orig_parent_id:
  - "8348521"
orig_thread_id:
  - "573774"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/04/01/a-c-library-to-write-functional-code-part-i-background.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="A C# library to write functional code  - Part I  - Background" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/04/01/a-c-library-to-write-functional-code-part-i-background/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator In December (slow time in msft) I decided to understand what functional programming is all about. When I say &#8216;understanding' I don't mean just paying lip service..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="A C# library to write functional code  - Part I  - Background" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/04/01/a-c-library-to-write-functional-code-part-i-background/" />
    <meta name="twitter:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator In December (slow time in msft) I decided to understand what functional programming is all about. When I say &#8216;understanding' I don't mean just paying lip service..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - 'C# Programming'
---
Other posts in the series:

  * [**<font color="#006bad">Part I  - Background</font>**](http://blogs.msdn.com/lucabol/archive/2008/04/01/a-c-library-to-write-functional-code-part-i-background.aspx) 
      * [**<font color="#006bad">Part II  - Tuples</font>**](http://blogs.msdn.com/lucabol/archive/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples.aspx) 
          * **[<font color="#006bad">Part III  - Records</font>](http://blogs.msdn.com/lucabol/archive/2008/04/21/a-c-library-to-write-functional-code-part-iii-records.aspx)**
          * **[Part IV  - Type Unions](http://blogs.msdn.com/lucabol/archive/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions.aspx){.}**
          * **[Part V  - The Match operator](http://blogs.msdn.com/lucabol/archive/2008/07/15/a-c-library-to-write-functional-code-part-v-the-match-operator.aspx){.}**
        In December (slow time in msft) I decided to understand what functional programming is all about. When I say &#8216;understanding' I don't mean just paying lip service to the main concepts by knowingly mentioning them in casual conversations (i.e. look at this memoization, man! or this lambda function is so hot!. I can already do that. I intellectually know what the thing is.
        
        I wanted to \*really\* understand it. For me that means writing plenty of code. I had a medium size application in my mind that I've been wanting to write for quite some time (stock price, dividends, splits downloading and various return calculations), so I went ahead and wrote it. I also wanted to use C#. It would have been easier in F#, but I work on the C# team and love using our own product.
        
        My early attempts were unpleasing. I would fall back to my OO background and my functional code slowly reverted to OO code. My way of thinking about it, even if starting with the best intentions, would go back to: what are the objects, what are their responsibilities and such.
        
        I needed to force myself somehow; kind of overcompensate on the other side. I hit on the idea of pragmatically defining functional programming and try to limit myself to the subset of language constructs inside my definition. As a way to define it, I used Chapter 3 of <a href="http://www.amazon.com/Expert-F-Experts-Voice-Net/dp/1590598504/ref=sr_1_1?ie=UTF8&s=books&qid=1207069956&sr=8-1" target="_blank"><strong><font color="#006bad">Expert F#</font></strong></a>. I know, I know, I could have read 1,000s of academic papers and come up with a meta-analysis of all of them that formally defines what &#8216;functional programming' really is. But life is too short. I trusted Don.
        
        The problem is, several of the language constructs in my small definition of functional programming don't exist in C#. So I went ahead and created them. I built a little library to represent them and forced myself to write code using just this library. It worked.
        
        In this series of posts I will describe what's inside this library. I want to emphasize that I built it for educational purpose only, not for performance or production code. Caveat emptor.
        
        My plan is to cover the following:
        
          1. Tuples 
              * Records 
                  * Type Unions 
                      * Match</ol> 
                    Let's see if I can find the time to actually write these posts 🙂