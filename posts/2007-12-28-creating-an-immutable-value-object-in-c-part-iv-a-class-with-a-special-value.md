---
id: 553
title: 'Creating an immutable value object in C# - Part IV - A class with a special value'
date: 2007-12-28T18:45:32+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/12/28/creating-an-immutable-value-object-in-c-part-iv-a-class-with-a-special-value/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/12/28/creating-an-immutable-value-object-in-c-part-iv-a-class-with-a-special-value.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "6889957"
orig_parent_id:
  - "6889957"
orig_thread_id:
  - "555073"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/12/28/creating-an-immutable-value-object-in-c-part-iv-a-class-with-a-special-value.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Creating an immutable value object in C#  - Part IV  - A class with a special value" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/12/28/creating-an-immutable-value-object-in-c-part-iv-a-class-with-a-special-value/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts: Part I  - Using a class Part II  - Making the class better Part III  - Using a struct In the last post we looked at structs as ways to implement immutable value objects and we discovered that they have several issues. A good thing about the struct implementation was the introduction of..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Creating an immutable value object in C#  - Part IV  - A class with a special value" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/12/28/creating-an-immutable-value-object-in-c-part-iv-a-class-with-a-special-value/" />
    <meta name="twitter:description" content="Other posts: Part I  - Using a class Part II  - Making the class better Part III  - Using a struct In the last post we looked at structs as ways to implement immutable value objects and we discovered that they have several issues. A good thing about the struct implementation was the introduction of..." />
    
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

In the last post we looked at structs as ways to implement immutable value objects and we discovered that they have several issues. 

A good thing about the struct implementation was the introduction of an explicit 'special value' instead of 'null'. I personally like doing that because it forces me to think about what are the special values in my domain instead of blindly rely on null and its semantics. Plus, it also works where null breaks down, when there are multiple special values.

Having explicit special values is obviously not related to structs in any way. You can use the same pattern with classes as well, but you have to manage 'null' values that can enter your API. Here is how I did it for the DateSpan class.

First I defined an utility function to manage null values:

```csharp
public static void CheckNull<T>(T t) {
    if (t == null)
        throw new ArgumentNullException();
}
```

Then I had to check my null precondition for each parameter of my API. I.E.

```csharp
public DateSpan Intersect(DateSpan other) {
    Utils.CheckNull(other);
    ...
}
```

Most importantly I now have to check for null in 'Equals' and '==':

```csharp
public override bool Equals(object obj) {
    // Interesting choice, null is not valid in this domain
    Utils.CheckNull(obj);
    if (this.GetType() != obj.GetType()) return false;
    DateSpan other = obj as DateSpan;
    return other.End == End && other.Start == Start;
}
```

```csharp
public static Boolean operator ==(DateSpan v1, DateSpan v2) {
    Utils.CheckNull(v1);
    Utils.CheckNull(v2);
    return (v1.Equals(v2));
}
```

So now we have an immutable value object, represented as a class, with checks for nulls and a special value (not shown above because it is essentially the same as for structs). So, does this work?

It does, but it is cumbersome to write. And if it is too cumbersome, I already know that I'm not going to use it. I might start doing it, but I would soon give up. Are there ways to ease the pain?

One way would be to use snippets to help in writing the code. Snippets in this case have a couple of problems:

  * It is not easy to 'snippify' the logic inside 'Equals', 'GetHashcode' and such
  * It makes easy to write the code, but still it is hard to read it and maintain it

In the next post we'll look at a better solution.
