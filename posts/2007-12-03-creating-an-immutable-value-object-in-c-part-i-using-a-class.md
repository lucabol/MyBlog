---
id: 603
title: 'Creating an immutable value object in C#  - Part I  - Using a class'
date: 2007-12-03T13:22:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/12/03/creating-an-immutable-value-object-in-c-part-i-using-a-class/
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

  * [Part II  - Making the class better](http://blogs.msdn.com/lucabol/archive/2007/12/06/creating-an-immutable-value-object-in-c-part-ii-making-the-class-better.aspx)
  * [Part III  - Using a struct](http://blogs.msdn.com/lucabol/archive/2007/12/24/creating-an-immutable-value-object-in-c-part-iii-using-a-struct.aspx)
  * [Part IV  - A class with a special value](http://blogs.msdn.com/lucabol/)

Value objects are objects for which the identity is based on their state instead of their pointer in memory. For example, a numeric Complex class is, most of the time, a value object because you can treat two instances as the same if their state (real and img fields in this case) is the same. An immutable value object is a value object that cannot be changed. You cannot modify its state, you have to create new ones.

I'm using these guys more and more in my code for a number of reasons, both practical and philosophical. The practical ones revolve around the greater robustness of programming without side effects and the greater simplicity of parallelizing your code. The philosophical ones are more interesting (and subjective). When in my design process I spend the time to aggressively looking for these kinds of objects, the resulting design ends up cleaner. I especially like when I can define some sort of close algebra for these guys (i.e. a set of functions that operate over them and produces new ones, not unlike '+' and '-' for numbers).

This series describes how to create immutable value objects in C# and the design decisions involved. This is a summary of an email thread I had with [Mads](http://blogs.msdn.com/madst/default.aspx) and [Luke](http://blogs.msdn.com/lukeh/default.aspx).

The concept I will use for this series is a **DateSpan**. As I define it, a DateSpan has a **Start** and an **End** date. You can ask for the DateSpan that represents the **Union** and **Intersection** of two DateSpans. The tests in the attached code better define the behavior of these operations.

Given that I never use structs in my code (I'm a minimalist language user), I'll start by using a class to represent it. We'll make this class better in part II and use a struct in part III. A first stab at it is as follows:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
public class DateSpan {
    public DateSpan(DateTime start, DateTime end) {
        if (end < start)
            throw new ArgumentException(start.ToString() + " doesn't come before " + end.ToString());
        Start = start;
        End = end;
    }
    public DateSpan Union(DateSpan other) {
        if (other == null)
            return new DateSpan(Start, End);
        if (IsOutside(other))
            return null;
        DateTime start = other.Start < Start ? other.Start : Start;
        DateTime end = other.End > End ? other.End : End;
        return new DateSpan(start, end);
    }
    public DateSpan Intersect(DateSpan other) {
        if (other == null)
            return null;
        if (IsOutside(other))
            return null;
        DateTime start = other.Start > Start ? other.Start : Start;
        DateTime end = other.End < End ? other.End : End;
        return new DateSpan(start, end);
    }
    private bool IsOutside(DateSpan other) {
        return other.Start > End || other.End < Start;
    }
    public DateTime Start { get; private set; }
    public DateTime End { get; private set; }
    #region Boilerplate Equals, ToString Implementation
    public override string ToString() {
        return string.Format("Start:{0} End:{1}", Start, End);
    }
    public override bool Equals(object obj) {
        if (obj == null) return false;
        if (this.GetType() != obj.GetType()) return false;
        DateSpan other = obj as DateSpan;
        return other.End == End && other.Start == Start;
    }
    public override int GetHashCode() {
        return Start.GetHashCode() | End.GetHashCode();
    }
    public static Boolean operator ==(DateSpan v1, DateSpan v2) {
        if ((object)v1 == null)
            if ((object)v2 == null)
                return true;
            else
                return false;
        return (v1.Equals(v2));
    }
    public static Boolean operator !=(DateSpan v1, DateSpan v2) {
        return !(v1 == v2);
    }
    #endregion
}
```

```csharp
public static class TimeLineExtensions {
    public static bool IsSuperSet(this DateSpan span, DateSpan other) {
        if (span.Intersect(other) == other)
            return true;
        return false;
    }
}
```

Some things to notice in this code:

1. Defining a value object with a C# class involves overriding Equals, Hashcode, == and !=. It is tricky, but usually boilerplate stuff, well described in [Wagner (2004)](http://www.amazon.com/Effective-Specific-Improve-Software-Development/dp/0321245660). I don't have Bill's book in my office, so I kind of made it up on the fly. It could be very wrong (the '==' one looks very suspicious). Don't copy it, read Bill's book instead
2. Defining an immutable object with a C# class involves discipline in not changing the private state (we'll see in Part II that we can do better than 'discipline')
3. Notice the extension method IsSuperSet. This is something I picked up from an old Coplien book, [probably this one](http://www.amazon.com/Multi-Paradigm-Design-James-O-Coplien/dp/0201824671). The concept is to keep methods that don't use internal state of an object external to the object itself for the sake of future maintainability. The syntax for doing that was awkward before, but extension methods make it easier

This works (it passes all the tests), but it has a number of problems. We'll talk about these in Part II.

[TimeLineAsClass  - 1.zip](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/06/64/68/07/TimeLineAsClass%20-%201.zip)
