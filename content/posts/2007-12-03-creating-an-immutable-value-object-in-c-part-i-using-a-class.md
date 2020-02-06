---
id: 603
title: 'Creating an immutable value object in C#  - Part I  - Using a class'
date: 2007-12-03T13:22:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/12/03/creating-an-immutable-value-object-in-c-part-i-using-a-class/
permalink: /2007/12/03/creating-an-immutable-value-object-in-c-part-i-using-a-class/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/12/03/creating-an-immutable-value-object-in-c-part-i-using-a-class.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "6646807"
orig_parent_id:
  - "6646807"
orig_thread_id:
  - "550469"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/12/03/creating-an-immutable-value-object-in-c-part-i-using-a-class.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Creating an immutable value object in C#  - Part I  - Using a class" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/12/03/creating-an-immutable-value-object-in-c-part-i-using-a-class/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts: Part II  - Making the class better Part III  - Using a struct Part IV  - A class with a special value Value objects are objects for which the identity is based on their state instead of their pointer in memory. For example, a numeric Complex class is, most of the time, a..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Creating an immutable value object in C#  - Part I  - Using a class" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/12/03/creating-an-immutable-value-object-in-c-part-i-using-a-class/" />
    <meta name="twitter:description" content="Other posts: Part II  - Making the class better Part III  - Using a struct Part IV  - A class with a special value Value objects are objects for which the identity is based on their state instead of their pointer in memory. For example, a numeric Complex class is, most of the time, a..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - csharp
---
Other posts:

  * [Part II  - Making the class better](http://blogs.msdn.com/lucabol/archive/2007/12/06/creating-an-immutable-value-object-in-c-part-ii-making-the-class-better.aspx){.}
  * [Part III  - Using a struct](http://blogs.msdn.com/lucabol/archive/2007/12/24/creating-an-immutable-value-object-in-c-part-iii-using-a-struct.aspx){.}
  * [Part IV  - A class with a special value](http://blogs.msdn.com/lucabol/){.}

Value objects are objects for which the identity is based on their state instead of their pointer in memory. For example, a numeric Complex class is, most of the time, a value object because you can treat two instances as the same if their state (real and img fields in this case) is the same. An immutable value object is a value object that cannot be changed. You cannot modify its state, you&nbsp;have to&nbsp;create new ones.

I'm using these guys more and more in my code for a number of reasons, both practical and philosophical. The practical ones revolve around the greater robustness of programming without side effects and the greater simplicity of parallelizing your code. The philosophical ones are more interesting (and subjective). When in&nbsp;my design process&nbsp;I spend the time to aggressively looking for these kinds of objects, the resulting design ends up cleaner. I especially like when I can define some sort of close algebra for these guys (i.e. a set of functions that operate over them and produces new ones, not unlike &#8216;+' and &#8216;-&#8216; for numbers).

This series describes how to create immutable value objects in C# and the design decisions involved. This is a summary of an email thread I had with <a href="http://blogs.msdn.com/madst/default.aspx" target="_blank">Mads</a> and <a href="http://blogs.msdn.com/lukeh/default.aspx" target="_blank">Luke</a>.

The concept I will use for this series is&nbsp;a **DateSpan**. As I define it, a DateSpan has a **Start** and an **End** date. You can ask for the&nbsp;DataSpan that represents the&nbsp;**Union** and **Intersection** of two DateSpans. The tests in the attached code better define the behavior of these operations.

Given that I never use structs in my code (I'm a minimalist language user), I'll start by using a class to represent it. We'll make this class better in part II and use a struct in part III. A first stab at it is as follows:

<pre class="code"><span style="color:rgb(0,0,255);">using</span> System;
<span style="color:rgb(0,0,255);">using</span> System.Collections.Generic;
<span style="color:rgb(0,0,255);">using</span> System.Linq;
<span style="color:rgb(0,0,255);">using</span> System.Text;
<span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">class</span> <span style="color:rgb(43,145,175);">DateSpan</span> {
    <span style="color:rgb(0,0,255);">public</span> DateSpan(<span style="color:rgb(43,145,175);">DateTime</span> start, <span style="color:rgb(43,145,175);">DateTime</span> end) {
        <span style="color:rgb(0,0,255);">if</span> (end &lt; start)
            <span style="color:rgb(0,0,255);">throw</span> <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">ArgumentException</span>(start.ToString() + <span style="color:rgb(163,21,21);">" doesn't come before "</span> + end.ToString());
        Start = start;
        End = end;
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">DateSpan</span> Union(<span style="color:rgb(43,145,175);">DateSpan</span> other) {
        <span style="color:rgb(0,0,255);">if</span> (other == <span style="color:rgb(0,0,255);">null</span>)
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">DateSpan</span>(Start, End);
        <span style="color:rgb(0,0,255);">if</span> (IsOutside(other))
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">null</span>;
        <span style="color:rgb(43,145,175);">DateTime</span> start = other.Start &lt; Start ? other.Start : Start;
        <span style="color:rgb(43,145,175);">DateTime</span> end = other.End &gt; End ? other.End : End;
        <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">DateSpan</span>(start, end);
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">DateSpan</span> Intersect(<span style="color:rgb(43,145,175);">DateSpan</span> other) {
        <span style="color:rgb(0,0,255);">if</span> (other == <span style="color:rgb(0,0,255);">null</span>)
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">null</span>;
        <span style="color:rgb(0,0,255);">if</span> (IsOutside(other))
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">null</span>;
        <span style="color:rgb(43,145,175);">DateTime</span> start = other.Start &gt; Start ? other.Start : Start;
        <span style="color:rgb(43,145,175);">DateTime</span> end = other.End &lt; End ? other.End : End;
        <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">DateSpan</span>(start, end);
    }
    <span style="color:rgb(0,0,255);">private</span> <span style="color:rgb(0,0,255);">bool</span> IsOutside(<span style="color:rgb(43,145,175);">DateSpan</span> other) {
        <span style="color:rgb(0,0,255);">return</span> other.Start &gt; End || other.End &lt; Start;
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">DateTime</span> Start { <span style="color:rgb(0,0,255);">get</span>; <span style="color:rgb(0,0,255);">private</span> <span style="color:rgb(0,0,255);">set</span>; }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">DateTime</span> End { <span style="color:rgb(0,0,255);">get</span>; <span style="color:rgb(0,0,255);">private</span> <span style="color:rgb(0,0,255);">set</span>; }
<span style="color:rgb(0,0,255);">    #region</span> Boilerplate Equals, ToString Implementation
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">override</span> <span style="color:rgb(0,0,255);">string</span> ToString() {
        <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">string</span>.Format(<span style="color:rgb(163,21,21);">"Start:{0} End:{1}"</span>, Start, End);
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">override</span> <span style="color:rgb(0,0,255);">bool</span> Equals(<span style="color:rgb(0,0,255);">object</span> obj) {
        <span style="color:rgb(0,0,255);">if</span> (obj == <span style="color:rgb(0,0,255);">null</span>) <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">false</span>;
        <span style="color:rgb(0,0,255);">if</span> (<span style="color:rgb(0,0,255);">this</span>.GetType() != obj.GetType()) <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">false</span>;
        <span style="color:rgb(43,145,175);">DateSpan</span> other = obj <span style="color:rgb(0,0,255);">as</span> <span style="color:rgb(43,145,175);">DateSpan</span>;
        <span style="color:rgb(0,0,255);">return</span> other.End == End && other.Start == Start;
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">override</span> <span style="color:rgb(0,0,255);">int</span> GetHashCode() {
        <span style="color:rgb(0,0,255);">return</span> Start.GetHashCode() | End.GetHashCode();
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(43,145,175);">Boolean</span> <span style="color:rgb(0,0,255);">operator</span> ==(<span style="color:rgb(43,145,175);">DateSpan</span> v1, <span style="color:rgb(43,145,175);">DateSpan</span> v2) {
        <span style="color:rgb(0,0,255);">if</span> ((<span style="color:rgb(0,0,255);">object</span>)v1 == <span style="color:rgb(0,0,255);">null</span>)
            <span style="color:rgb(0,0,255);">if</span> ((<span style="color:rgb(0,0,255);">object</span>)v2 == <span style="color:rgb(0,0,255);">null</span>)
                <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">true</span>;
            <span style="color:rgb(0,0,255);">else
</span>                <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">false</span>;
        <span style="color:rgb(0,0,255);">return</span> (v1.Equals(v2));
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(43,145,175);">Boolean</span> <span style="color:rgb(0,0,255);">operator</span> !=(<span style="color:rgb(43,145,175);">DateSpan</span> v1, <span style="color:rgb(43,145,175);">DateSpan</span> v2) {
        <span style="color:rgb(0,0,255);">return</span> !(v1 == v2);
    }
<span style="color:rgb(0,0,255);">    #endregion
</span>}</pre>

<pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(0,0,255);">class</span> <span style="color:rgb(43,145,175);">TimeLineExtensions</span> {
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(0,0,255);">bool</span> IsSuperSet(<span style="color:rgb(0,0,255);">this</span> <span style="color:rgb(43,145,175);">DateSpan</span> span, <span style="color:rgb(43,145,175);">DateSpan</span> other) {
        <span style="color:rgb(0,0,255);">if</span> (span.Intersect(other) == other)
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">true</span>;
        <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">false</span>;
    }
}
</pre>

</p> 

Some&nbsp;things to notice in this code:

  1. Defining a value object&nbsp;with a&nbsp;C# class involves overriding Equals, Hashcode, == and !=.&nbsp;It is tricky, but usually boilerplate stuff, well described in <a href="http://www.amazon.com/Effective-Specific-Improve-Software-Development/dp/0321245660" target="_blank">Wagner (2004)</a>. I don't have Bill's book in my office, so I kind of made it up on the fly. It could be very wrong (the &#8216;==' one looks very suspicious). Don't copy it, read Bill's book instead 
      * Defining an immutable object with&nbsp;a C# class involves discipline in not changing the private state (we'll see in Part II that we can do better than &#8216;discipline') 
          * Notice the extension method IsSuperSet. This is something I picked up from an old Coplien book, <a href="http://www.amazon.com/Multi-Paradigm-Design-James-O-Coplien/dp/0201824671" target="_blank">probably this one</a>. The concept is to keep methods that don't use internal state of an object external to the object itself for the sake of future maintainability. The syntax for doing that was awkward before, but extension methods make it easier</ol> 
        This works (it passes all the tests), but it has a number of problems. We'll talk about these in Part II.
        
        [TimeLineAsClass  - 1.zip](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/06/64/68/07/TimeLineAsClass%20-%201.zip)