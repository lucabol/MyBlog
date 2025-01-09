---
id: 573
title: 'Creating an immutable value object in C#  - Part III  - Using a struct'
date: 2007-12-24T17:39:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/12/24/creating-an-immutable-value-object-in-c-part-iii-using-a-struct/
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
  * [Part IV  - A class with a special value](http://blogs.msdn.com/lucabol/)

In Part II I talked about the asymmetry created by using 'null' as the special value for our little DateSpan domain. We also noticed the boredom of having to implement Equals, GetHashCode, '==' and '!=' for our value objects. Let's see if structs solve our problem.

Well, to the untrained eye they do. Structs cannot be null and they implement Equals and GetHashCode by checking the state of the object, not its pointer in memory.

So, have we found the perfect tool to implement our value object?

Unfortunately, no. Here is why a struct is a less than optimal way to implement a value object:

1. <u>Convenience issues</u>  - it is not as convenient as it looks
   1. You still have to implement '==' and '!='
   2. You still want to implement Equals() and GetHashCode(), if you want to avoid boxing/unboxing.

2. <u>Performance issues</u>  - it is not as fast as it looks
   1. Structs are allocated on the stack. Every time you pass them as arguments, the state is copied. If your struct has more than a few fields, performance might suffer

3. <u>Usability issues</u>  - it is not as useful as it looks.
   1. Structs always have a public default constructor that 'zeros' all the fields
   2. Structs cannot be abstract
   3. Structs cannot extend another structs

Don't get me wrong, structs are extremely useful as a way to represent small bundles of data. But if you use value objects extensively, their limitations start to show.

A case could be made that you should use struct to implement value objects if the issues exposed above don't apply to your case. When they do apply, you should use classes. I'm a forgetful and lazy programmer, I don't want to remember all these cases. I just want a pattern that I can use whenever I need a value object. It seems to me that structs don't fit the bill.

For the sake of completeness, here is the code for DateSpan using a struct. Note that I explicitly introduced a 'special value' instead of using null (which is not available for structs).

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

public struct DateSpan {
    public static DateSpan NoValueDateSpan { get { return noValueDateSpan; } }
    public DateSpan(DateTime pstart, DateTime pend) {
        if (pend < pstart)
            throw new ArgumentException(pstart.ToString() + " doesn't come before " + pend.ToString());
        start = pstart;
        end = pend;
        hasValue = true;
    }
    public DateSpan Union(DateSpan other) {
        if (!HasValue)
            return other;
        if (!other.HasValue)
            return this;
        if (IsOutside(other))
            return DateSpan.NoValueDateSpan;
        DateTime newStart = other.Start < Start ? other.Start : Start;
        DateTime newEnd = other.End > End ? other.End : End;
        return new DateSpan(newStart, newEnd);
    }
    public DateSpan Intersect(DateSpan other) {
        if (!HasValue)
            return DateSpan.NoValueDateSpan;
        if (!other.HasValue)
            return DateSpan.NoValueDateSpan;
        if (IsOutside(other))
            return DateSpan.NoValueDateSpan;
        DateTime newStart = other.Start > Start ? other.Start : Start;
        DateTime newEnd = other.End < End ? other.End : End;
        return new DateSpan(newStart, newEnd);
    }
    public DateTime Start { get { return start; } }
    public DateTime End { get { return end; } }
    public bool HasValue { get { return hasValue; } }
    // Making field explicitely readonly (but cannot use autoproperties)
    // BTW: If you want to use autoproperties, given that it is a struct,
    // you need to add :this() to the constructor
    private readonly DateTime start;
    private readonly DateTime end;
    private readonly bool hasValue;
    private bool IsOutside(DateSpan other) {
        return other.start > end || other.end < start;
    }
    // Changing the internal machinery so that hasValue default is false
    // This way the automatically generated empty constructor returns the right thing
    private static DateSpan noValueDateSpan = new DateSpan();
    #region Boilerplate Equals, ToString Implementation
    public override string ToString() {
        return string.Format("Start:{0} End:{1}", start, end);
    }
    public static Boolean operator ==(DateSpan v1, DateSpan v2) {
        return (v1.Equals(v2));
    }
    public static Boolean operator !=(DateSpan v1, DateSpan v2) {
        return !(v1 == v2);
    }
    //public override bool Equals(object obj) {
    //    if (this.GetType() != obj.GetType()) return false;
    //    DateSpan other = (DateSpan) obj;
    //    return other.end == end && other.start == start;
    //}
    //public override int GetHashCode() {
    //    return start.GetHashCode() | end.GetHashCode();
    //}
    #endregion
}
```

[TimeLineAsStruct.zip](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/06/85/58/26/TimeLineAsStruct.zip)
