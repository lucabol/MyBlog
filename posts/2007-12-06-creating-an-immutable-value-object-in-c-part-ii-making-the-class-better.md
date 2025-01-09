---
id: 593
title: 'Creating an immutable value object in C#  - Part II  - Making the class better'
date: 2007-12-06T12:34:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/12/06/creating-an-immutable-value-object-in-c-part-ii-making-the-class-better/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/12/06/creating-an-immutable-value-object-in-c-part-ii-making-the-class-better.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "6682357"
orig_parent_id:
  - "6682357"
orig_thread_id:
  - "551175"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/12/06/creating-an-immutable-value-object-in-c-part-ii-making-the-class-better.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Creating an immutable value object in C#  - Part II  - Making the class better" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/12/06/creating-an-immutable-value-object-in-c-part-ii-making-the-class-better/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts: Part I  - Using a class Part III  - Using a struct Part IV  - A class with a special value In the previous post I showed how to trivially implement a value object. The code works but it has several issues. Some are very simple, others are more interesting. Let's take a..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Creating an immutable value object in C#  - Part II  - Making the class better" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/12/06/creating-an-immutable-value-object-in-c-part-ii-making-the-class-better/" />
    <meta name="twitter:description" content="Other posts: Part I  - Using a class Part III  - Using a struct Part IV  - A class with a special value In the previous post I showed how to trivially implement a value object. The code works but it has several issues. Some are very simple, others are more interesting. Let's take a..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - csharp
---
Other posts:

  * [Part I  - Using a class](http://blogs.msdn.com/lucabol/archive/2007/12/03/creating-an-immutable-value-object-in-c-part-i-using-a-class.aspx)
  * [Part III  - Using a struct](http://blogs.msdn.com/lucabol/archive/2007/12/24/creating-an-immutable-value-object-in-c-part-iii-using-a-struct.aspx)
  * [Part IV  - A class with a special value](http://blogs.msdn.com/lucabol/)

In the previous post I showed how to trivially implement a value object. The code works but it has several issues. Some are very simple, others are more interesting.

Let's take a look at them:

  * State not explicitly read-only
  * Asymmetry in the usage of Union and Intersection
  * Small perf issue in the Union method

The first problem is that my use of automatic properties doesn't assure that the status of the object is immutable; I can still modify it from inside the class. The simple solution is to make the fields _readonly_ and write the getters as in:

```csharp
private readonly DateTime start;
    private readonly DateTime end;
    public DateTime Start { get { return start; } }
    public DateTime End { get { return end; } }
```

The second issue is more subtle. Consider this code

```csharp
DateSpan d1 = new DateSpan(new DateTime(1, 1, 2000), new DateTime(1, 1, 2002));
        DateSpan d2 = null;
        DateSpan r1 = d1.Intersect(d2);
        DateSpan r2 = d2.Intersect(d1);
```

I would like things in my little 'algebra' to be symmetric. In this case I'd like: _r1 == r2 == null_. But this code throws in the last line as I'm trying to invoke a method on a null object.

The traditional solution to this problem is to make Union and Intersect to be static methods, but then you loose the magic of calling them as instance methods (i.e. it becomes hard to chain them together as in _d1.Intersect(d2).Union(d3).Intersect(d4)_).

Extension methods come to the rescue here as they allow you to create static methods, but to call them as if the were instance methods. The new code for _Intersect_ looks like the following:

```csharp
public static DateSpan Intersect(this DateSpan one, DateSpan other) {
        if (one == null)
            return null;
        if (other == null)
            return null;
        if (one.IsOutside(other))
            return null;
        DateTime start = other.Start > one.Start ? other.Start : one.Start;
        DateTime end = other.End < one.End ? other.End : one.End;
        return new DateSpan(start, end);
    }
```

This workaround would not work if the extension method needs to access private state of the class. In that case you would need to create a static method on the _DataSpan_ class and invoke it from the extension method. Slightly more convoluted, but still doable.

At a more philosophical level, the asymmetry issue happens here because I'm using something outside my domain of interest (the _null_ value) to represent a special value inside my domain of interest. More on this as we talk about structs in upcoming posts.

The last point is a very small one. In the _Union_ method I am creating a new object unnecessarily in the following line:

```csharp
if (other == null)
            return new DateSpan(Start, End);
```

I can obviously avoid it by just returning _this_.

This post hints to several possible issues. Is it a good idea to use null to represent special values in my domain? What if I have more than one of them (i.e. positive/negative infinite)? Would using structs solve these problems?

We'll take a look at these options in upcoming posts. Attached is the modified code.
