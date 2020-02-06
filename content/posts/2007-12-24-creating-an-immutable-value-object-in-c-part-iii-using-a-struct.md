---
id: 573
title: 'Creating an immutable value object in C#  - Part III  - Using a struct'
date: 2007-12-24T17:39:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/12/24/creating-an-immutable-value-object-in-c-part-iii-using-a-struct/
permalink: /2007/12/24/creating-an-immutable-value-object-in-c-part-iii-using-a-struct/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/12/24/creating-an-immutable-value-object-in-c-part-iii-using-a-struct.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "6855826"
orig_parent_id:
  - "6855826"
orig_thread_id:
  - "554754"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/12/24/creating-an-immutable-value-object-in-c-part-iii-using-a-struct.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Creating an immutable value object in C#  - Part III  - Using a struct" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/12/24/creating-an-immutable-value-object-in-c-part-iii-using-a-struct/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts: Part I  - Using a class Part II  - Making the class better Part IV  - A class with a special value In Part II I talked about the asymmetry created by using &#8216;null' as the special value for our little DateSpan domain. We also noticed the boredom of having to implement Equals,..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Creating an immutable value object in C#  - Part III  - Using a struct" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/12/24/creating-an-immutable-value-object-in-c-part-iii-using-a-struct/" />
    <meta name="twitter:description" content="Other posts: Part I  - Using a class Part II  - Making the class better Part IV  - A class with a special value In Part II I talked about the asymmetry created by using &#8216;null' as the special value for our little DateSpan domain. We also noticed the boredom of having to implement Equals,..." />
    
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
      * [Part IV  - A class with a special value](http://blogs.msdn.com/lucabol/){.}</ul> 
    In Part II I talked about the asymmetry created by using &#8216;null' as the special value for our little DateSpan domain. We also noticed the boredom of having to implement Equals, GetHashCode, &#8216;==' and &#8216;!=' for our value objects. Let's see if structs solve our problem.
    
    Well, to the untrained eye they do. Structs cannot be null and they implement Equals and GetHashCode by checking the state of the object, not its pointer in memory.
    
    So, have we found the perfect tool to implement our value object?
    
    Unfortunately, no. Here is why a struct is a less than optimal way to implement a value object:
    
      1. <u>Convenience issues</u>  - it is not as convenient as it looks 
          1. You still have to implement &#8216;==' and &#8216;!='. 
              * You still want to implement Equals() and GetHashCode(), if you want to avoid boxing/unboxing.</ol> 
              * <u>Performance issues</u>  - it is not as fast as it looks 
                  1. Structs are allocated on the stack. Every time you pass them as arguments, the state is copied. If your struct has more than a few fields, performance might suffer
                  * <u>Usability issues</u>  - it is not as useful as it looks. 
                      1. Structs always have a public default constructor that &#8216;zeros' all the fields 
                          * Structs cannot be abstract 
                              * Structs cannot extend another structs</ol> </ol> 
                        Don't get me wrong, structs are extremely useful as a way to represent small bundles of data. But if you use value objects extensively, their limitations start to show.
                        
                        A case could be made that you should use struct to implement value objects if the issues exposed above don't apply to your case. When they do apply, you should use classes. I'm a forgetful and lazy programmer, I don't want to remember all these cases. I just want a pattern that I can use whenever I need a value object. It seems to me that structs don't fit the bill.
                        
                        For the sake of completeness, here is the code for DateSpan using a struct. Note that I explicitly introduced a &#8216;special value' instead of using null (which is not available for structs).
                        
                        <pre class="code"><span style="color:rgb(0,0,255);">using</span> System;
<span style="color:rgb(0,0,255);">using</span> System.Collections.Generic;
<span style="color:rgb(0,0,255);">using</span> System.Linq;
<span style="color:rgb(0,0,255);">using</span> System.Text;
<span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">struct</span> <span style="color:rgb(43,145,175);">DateSpan</span> {
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(43,145,175);">DateSpan</span> NoValueDateSpan { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> noValueDateSpan; } }
    <span style="color:rgb(0,0,255);">public</span> DateSpan(<span style="color:rgb(43,145,175);">DateTime</span> pstart, <span style="color:rgb(43,145,175);">DateTime</span> pend) {
        <span style="color:rgb(0,0,255);">if</span> (pend &lt; pstart)
            <span style="color:rgb(0,0,255);">throw</span> <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">ArgumentException</span>(pstart.ToString() + <span style="color:rgb(163,21,21);">" doesn't come before "</span> + pend.ToString());
        start = pstart;
        end = pend;
        hasValue = <span style="color:rgb(0,0,255);">true</span>;
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">DateSpan</span> Union(<span style="color:rgb(43,145,175);">DateSpan</span> other) {
        <span style="color:rgb(0,0,255);">if</span> (!HasValue)
            <span style="color:rgb(0,0,255);">return</span> other;
        <span style="color:rgb(0,0,255);">if</span> (!other.HasValue)
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">this</span>;
        <span style="color:rgb(0,0,255);">if</span> (IsOutside(other))
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(43,145,175);">DateSpan</span>.NoValueDateSpan;
        <span style="color:rgb(43,145,175);">DateTime</span> newStart = other.Start &lt; Start ? other.Start : Start;
        <span style="color:rgb(43,145,175);">DateTime</span> newEnd = other.End &gt; End ? other.End : End;
        <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">DateSpan</span>(newStart, newEnd);
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">DateSpan</span> Intersect(<span style="color:rgb(43,145,175);">DateSpan</span> other) {
        <span style="color:rgb(0,0,255);">if</span> (!HasValue)
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(43,145,175);">DateSpan</span>.NoValueDateSpan;
        <span style="color:rgb(0,0,255);">if</span> (!other.HasValue)
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(43,145,175);">DateSpan</span>.NoValueDateSpan;
        <span style="color:rgb(0,0,255);">if</span> (IsOutside(other))
            <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(43,145,175);">DateSpan</span>.NoValueDateSpan;
        <span style="color:rgb(43,145,175);">DateTime</span> newStart = other.Start &gt; Start ? other.Start : Start;
        <span style="color:rgb(43,145,175);">DateTime</span> newEnd = other.End &lt; End ? other.End : End;
        <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">DateSpan</span>(newStart, newEnd);
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">DateTime</span> Start { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> start; } }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">DateTime</span> End { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> end; } }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">bool</span> HasValue { <span style="color:rgb(0,0,255);">get</span> { <span style="color:rgb(0,0,255);">return</span> hasValue; } }
    <span style="color:rgb(0,128,0);">// Making field explicitely readonly (but cannot use autoproperties)
</span>    <span style="color:rgb(0,128,0);">// BTW: If you want to use autoproperties, given that it is a struct,
</span>    <span style="color:rgb(0,128,0);">// you need to add :this() to the constructor
</span>    <span style="color:rgb(0,0,255);">private</span> <span style="color:rgb(0,0,255);">readonly</span> <span style="color:rgb(43,145,175);">DateTime</span> start;
    <span style="color:rgb(0,0,255);">private</span> <span style="color:rgb(0,0,255);">readonly</span> <span style="color:rgb(43,145,175);">DateTime</span> end;
    <span style="color:rgb(0,0,255);">private</span> <span style="color:rgb(0,0,255);">readonly</span> <span style="color:rgb(0,0,255);">bool</span> hasValue;
    <span style="color:rgb(0,0,255);">private</span> <span style="color:rgb(0,0,255);">bool</span> IsOutside(<span style="color:rgb(43,145,175);">DateSpan</span> other) {
        <span style="color:rgb(0,0,255);">return</span> other.start &gt; end || other.end &lt; start;
    }
    <span style="color:rgb(0,128,0);">// Changing the internal machinery so that hasValue default is false
</span>    <span style="color:rgb(0,128,0);">// This way the automatically generated empty constructor returns the right thing
</span>    <span style="color:rgb(0,0,255);">private</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(43,145,175);">DateSpan</span> noValueDateSpan = <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">DateSpan</span>();
<span style="color:rgb(0,0,255);">    #region</span> Boilerplate Equals, ToString Implementation
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">override</span> <span style="color:rgb(0,0,255);">string</span> ToString() {
        <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">string</span>.Format(<span style="color:rgb(163,21,21);">"Start:{0} End:{1}"</span>, start, end);
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(43,145,175);">Boolean</span> <span style="color:rgb(0,0,255);">operator</span> ==(<span style="color:rgb(43,145,175);">DateSpan</span> v1, <span style="color:rgb(43,145,175);">DateSpan</span> v2) {
        <span style="color:rgb(0,0,255);">return</span> (v1.Equals(v2));
    }
    <span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(43,145,175);">Boolean</span> <span style="color:rgb(0,0,255);">operator</span> !=(<span style="color:rgb(43,145,175);">DateSpan</span> v1, <span style="color:rgb(43,145,175);">DateSpan</span> v2) {
        <span style="color:rgb(0,0,255);">return</span> !(v1 == v2);
    }
    <span style="color:rgb(0,128,0);">//public override bool Equals(object obj) {
</span>    <span style="color:rgb(0,128,0);">//    if (this.GetType() != obj.GetType()) return false;
</span>    <span style="color:rgb(0,128,0);">//    DateSpan other = (DateSpan) obj;
</span>    <span style="color:rgb(0,128,0);">//    return other.end == end && other.start == start;
</span>    <span style="color:rgb(0,128,0);">//}
</span>    <span style="color:rgb(0,128,0);">//public override int GetHashCode() {
</span>    <span style="color:rgb(0,128,0);">//    return start.GetHashCode() | end.GetHashCode();
</span>    <span style="color:rgb(0,128,0);">//}
</span><span style="color:rgb(0,0,255);">    #endregion
</span>}
</pre>
                        
                        
                        
                        [TimeLineAsStruct.zip](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/06/85/58/26/TimeLineAsStruct.zip)