---
id: 473
title: 'A C# library to write functional code - Part III - Records'
date: 2008-04-21T13:34:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/04/21/a-c-library-to-write-functional-code-part-iii-records/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/04/21/a-c-library-to-write-functional-code-part-iii-records.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "8415052"
orig_parent_id:
  - "8415052"
orig_thread_id:
  - "578137"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/04/21/a-c-library-to-write-functional-code-part-iii-records.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="A C# library to write functional code  - Part III  - Records" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/04/21/a-c-library-to-write-functional-code-part-iii-records/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator Now that we know what Tuples are, we can start talking about Record, as they use a derivative of Tuples under the cover. But first, what is..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="A C# library to write functional code  - Part III  - Records" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/04/21/a-c-library-to-write-functional-code-part-iii-records/" />
    <meta name="twitter:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator Now that we know what Tuples are, we can start talking about Record, as they use a derivative of Tuples under the cover. But first, what is..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - csharp
---
Other posts in the series:

  * [Part I  - Background](http://blogs.msdn.com/lucabol/archive/2008/04/01/a-c-library-to-write-functional-code-part-i-background.aspx)
  * [Part II  - Tuples](http://blogs.msdn.com/lucabol/archive/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples.aspx)
  * [Part III  - Records](http://blogs.msdn.com/lucabol/archive/2008/04/21/a-c-library-to-write-functional-code-part-iii-records.aspx)
  * [Part IV  - Type Unions](http://blogs.msdn.com/lucabol/archive/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions.aspx)
  * [Part V  - The Match operator](http://blogs.msdn.com/lucabol/archive/2008/07/15/a-c-library-to-write-functional-code-part-v-the-match-operator.aspx)

Now that we know what Tuples are, we can start talking about Record, as they use a derivative of Tuples under the cover. But first, what is a record?

Well, in C# parlance a Record is a sort of immutable value object. I talked at length about these fellows in [this series of blog posts](http://blogs.msdn.com/lucabol/archive/2007/12/03/creating-an-immutable-value-object-in-c-part-i-using-a-class.aspx). In functional parlance, a Record is a Tuple that lets you access its items by name.

You code Records like this:

```csharp
public class Order: Record<string, int> {
    public Order(string item, int qty): base(item,qty) {}
    public string Item { get { return state.Item1;}}
    public int Quantity { get { return state.Item2; } }
}
public class Customer: Record<string, IEnumerable<Order>> {
    public Customer(string name, IEnumerable<Order> orders) : base(name, orders) { }
    public string Name { get { return state.Item1; } }
    public IEnumerable<Order> Orders { get { return state.Item2; } }
}
```

You need to do three things:

1. Inherit from a generic Record class specifying the types of the properties as parameters
2. Add a constructor that calls back to the Record constructor
3. Add getters to retrieve the values of the properties (no setters as it is immutable)

This may seem like plenty of work, but in return you get structural equality. Coding that by hand every time you use a record would be a royal pain. You lose control of the base class, but that is often not a problem as in functional-land you more often use type unions than inheritance.

How is it implemented?

First of all it is an abstract class with as many generic parameters as properties that you need in your Record. Let's use two as an example.

```csharp
public abstract class Record<T1, T2> {
```

This abstract class has a field of type STuple:

```csharp
protected readonly STuple<T1, T2> state;
```

What is a STuple? Well it is exactly the same as the Tuple described in Part II, but coded as a struct instead of a class. The reason to use a struct is to not allocate an additional object on the stack. This allows this solution to be as 'performant' as simply having coded the fields on the class itself. Or at least I think so

The Record class also has a constructor that simply initialize the STuple:

```csharp
public Record(T1 t1, T2 t2) { state = F.STuple(t1, t2); }
```

where

```csharp
internal static STuple<T1, T2> STuple<T1, T2>(T1 t1, T2 t2) {
    return new STuple<T1, T2>(t1, t2);
}
```

The Equals method is very much the same as the Tuple's one, just delegating to the same DSEqual function that checks equality for Tuples.

```csharp
public override bool Equals(object right) {
    Utils.CheckNull(right);
    if (object.ReferenceEquals(this, right))
        return true;
    if (this.GetType() != right.GetType())
        return false;
    var rightT = right as Record<T1, T2>;
    return F.DSEquals(this.state, rightT.state);
}
```

That's it. Not too difficult as most of the implementation is based on the Tuple's code. Next post will hopefully be more interesting. It is about Type Unions.
