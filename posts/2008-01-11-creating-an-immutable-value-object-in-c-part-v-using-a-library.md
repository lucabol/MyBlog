---
id: 533
title: 'Creating an immutable value object in C# - Part V - Using a library'
date: 2008-01-11T13:36:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/01/11/creating-an-immutable-value-object-in-c-part-v-using-a-library/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/01/11/creating-an-immutable-value-object-in-c-part-v-using-a-library.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "7077713"
orig_parent_id:
  - "7077713"
orig_thread_id:
  - "557308"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/01/11/creating-an-immutable-value-object-in-c-part-v-using-a-library.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Creating an immutable value object in C#  - Part V  - Using a library" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/01/11/creating-an-immutable-value-object-in-c-part-v-using-a-library/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts: Part I  - Using a class Part II  - Making the class better Part III  - Using a struct Part IV  - A class with a special value In the last post we presented a variation of implementing a value object using a class. Everything works (obviously), but the amount of code to..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Creating an immutable value object in C#  - Part V  - Using a library" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/01/11/creating-an-immutable-value-object-in-c-part-v-using-a-library/" />
    <meta name="twitter:description" content="Other posts: Part I  - Using a class Part II  - Making the class better Part III  - Using a struct Part IV  - A class with a special value In the last post we presented a variation of implementing a value object using a class. Everything works (obviously), but the amount of code to..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - csharp
---
Other posts:

  * [Part I  - Using a class](http://blogs.msdn.com/lucabol/archive/2007/12/03/creating-an-immutable-value-object-in-c-part-i-using-a-class.aspx) 
      * [Part II  - Making the class better](http://blogs.msdn.com/lucabol/archive/2007/12/06/creating-an-immutable-value-object-in-c-part-ii-making-the-class-better.aspx) 
          * [Part III  - Using a struct](http://blogs.msdn.com/lucabol/archive/2007/12/24/creating-an-immutable-value-object-in-c-part-iii-using-a-struct.aspx)
          * [Part IV  - A class with a special value](http://blogs.msdn.com/lucabol/)
        In the last post we presented a variation of implementing a value object using a class. Everything works (obviously), but the amount of code to write is unpleasing. In this post we examine a library based solution. I just describe how to use the Record class, not how it is implemented. You can read the attached implementation code (it is in functional.cs). There is much more in there than Record<>. I'll talk about the rest in a (hopefully) upcoming series.
        
        To use the record class you need to inherit from it, as in:
        
        <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">class</span> <span style="color:rgb(43,145,175);">DateSpan</span>: <span style="color:rgb(43,145,175);">Record</span>&lt;<span style="color:rgb(43,145,175);">DateTime</span>, <span style="color:rgb(43,145,175);">DateTime</span>, <span style="color:rgb(0,0,255);">bool</span>&gt; {...}</pre>
        
        The generic argument types represent the types that comprise the (immutable) state of the object. You then need a friendly way for folks to access this state:
        
        <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">DateTime</span> Start { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> state.Item1; } }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">DateTime</span> End { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> state.Item2; } }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">bool</span> HasValue { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> state.Item3; } }
</pre>
        
        This is all you have to do. You don't need to implement Equals, ==, != and GetHashCode. Structural equivalence is given to you by the Record class. Such a property is recursive, in the sense that you can embed value objects inside other value objects and the implementation would walk your object graph as necessary.
        
        For example, given the following class hierarchy:
        
        <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">class</span> <span style="color:rgb(43,145,175);">Order</span>: <span style="color:rgb(43,145,175);">Record</span>&lt;<span style="color:rgb(0,0,255);">string</span>, <span style="color:rgb(0,0,255);">int</span>&gt; {
        <span style="color:rgb(0,0,255);">public</span> Order(<span style="color:rgb(0,0,255);">string</span> item, <span style="color:rgb(0,0,255);">int</span> qty): <span style="color:rgb(0,0,255);">base</span>(item,qty) {}
        <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">string</span> Item { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> state.Item1;}}
        <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">int</span> Quantity { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> state.Item2; } }
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">class</span> <span style="color:rgb(43,145,175);">Customer</span>: <span style="color:rgb(43,145,175);">Record</span>&lt;<span style="color:rgb(0,0,255);">string</span>, <span style="color:rgb(43,145,175);">IEnumerable</span>&lt;<span style="color:rgb(43,145,175);">Order</span>&gt;&gt; {
        <span style="color:rgb(0,0,255);">public</span> Customer(<span style="color:rgb(0,0,255);">string</span> name, <span style="color:rgb(43,145,175);">IEnumerable</span>&lt;<span style="color:rgb(43,145,175);">Order</span>&gt; orders) : <span style="color:rgb(0,0,255);">base</span>(name, orders) { }
        <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">string</span> Name { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> state.Item1; } }
        <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">IEnumerable</span>&lt;<span style="color:rgb(43,145,175);">Order</span>&gt; Orders { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> state.Item2; } }
    }</pre>
        
        The following test case succeed:
        
        <pre class="code">[<span style="color:rgb(43,145,175);">TestMethod</span>]
        <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">void</span> Record2Test() {
            <span style="color:rgb(0,0,255);">var</span> c1 = <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Customer</span>(<span style="color:rgb(163,21,21);">"Luca"</span>, <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Order</span>[] { <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Order</span>(<span style="color:rgb(163,21,21);">"car"</span>,1), <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Order</span>(<span style="color:rgb(163,21,21);">"stereo"</span>, 3)});
            <span style="color:rgb(0,0,255);">var</span> c11 = <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Customer</span>(<span style="color:rgb(163,21,21);">"Luca"</span>, <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Order</span>[] { <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Order</span>(<span style="color:rgb(163,21,21);">"car"</span>, 1), <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Order</span>(<span style="color:rgb(163,21,21);">"stereo"</span>, 3) });
            <span style="color:rgb(0,0,255);">var</span> c2 = <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Customer</span>(<span style="color:rgb(163,21,21);">"Bob"</span>, <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Order</span>[] { <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Order</span>(<span style="color:rgb(163,21,21);">"car"</span>, 1), <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Order</span>(<span style="color:rgb(163,21,21);">"stereo"</span>, 3) });
            <span style="color:rgb(0,0,255);">var</span> c3 = <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Customer</span>(<span style="color:rgb(163,21,21);">"Bob"</span>, <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Order</span>[] { <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Order</span>(<span style="color:rgb(163,21,21);">"car"</span>, 1), <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">Order</span>(<span style="color:rgb(163,21,21);">"stereo"</span>, 2) });
            <span style="color:rgb(43,145,175);">Assert</span>.AreEqual(c1, c11);
            <span style="color:rgb(43,145,175);">Assert</span>.AreNotEqual(c1, c2);
            <span style="color:rgb(43,145,175);">Assert</span>.AreNotEqual(c1, c3);
            <span style="color:rgb(43,145,175);">Assert</span>.AreNotEqual(c2, c3);
        }</pre>
        
        Please don't take my library as production ready code. The amount of test I put into it is limited. You can probably find obvious bugs with it. 
        
        Let's look at other drawbacks. The biggest one is that I'm stealing your base class. If you want your value object to inherit from something else, you cannot. You cannot even have value objects inherit from each other. In that case you are back to implementing your own Equals, == and so on. The only tools at your disposal are interfaces and composition.
        
        Another drawback is that writing classes in this way is slightly unnatural. You have to think about the &#8216;type' of your state in the declaration of the class itself instead of more naturally writing it closer to where you assign names to it (property/field declaration).
        
        Having considered these drawbacks, I'm using this library in all my code wherever I need value objects (which is almost everywhere these days). Writing all the Equals explicitly is too error prone for my taste. I will also be creating IDE snippets for myself that make writing these classes easier.
        
        I don't think I have anything else to say on this topic, so this will be my last post on it. If something else comes up, I'll let you know.
        
        [TimeLineUsingRecord.zip](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/07/07/77/13/TimeLineUsingRecord.zip)