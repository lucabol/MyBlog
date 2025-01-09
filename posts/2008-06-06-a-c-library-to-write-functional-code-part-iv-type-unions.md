---
id: 463
title: 'A C# library to write functional code - Part IV - Type Unions'
date: 2008-06-06T04:45:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "8577265"
orig_parent_id:
  - "8577265"
orig_thread_id:
  - "587316"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="A C# library to write functional code  - Part IV  - Type Unions" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator I'm sorry for my prolonged absence in the middle of this series of posts. I'm on a long paternity leave in Italy (playing beach volley every day)...." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="A C# library to write functional code  - Part IV  - Type Unions" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/06/06/a-c-library-to-write-functional-code-part-iv-type-unions/" />
    <meta name="twitter:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator I'm sorry for my prolonged absence in the middle of this series of posts. I'm on a long paternity leave in Italy (playing beach volley every day)...." />
    
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

I'm sorry for my prolonged absence in the middle of this series of posts. I'm on a long paternity leave in Italy (playing beach volley every day). It's hard to have the discipline

A bunch of you wrote telling me to finish this. So here I go: let's talk about type unions. First of all: they are not called like that. The correct name is discriminated unions. I have no idea why I call them differently, but I want to be consistent with my previous mistake.

For those of you with a C++ background (like myself) they are like unions, just better (or worse depending on your convictions). They let you define a type that can represent one of several different types. You can then use the 'match' operator (discussed in the next post) to pattern match against it.

I won't elaborate on the pros and cons of this style of programming versus using polymorphism. I just want to show you how I implemented this construct in C#. As always, my usual caveat: this is just 'educational code', use it at your own risk, no extensive or perf related test has been done on it. You can download the zip file and check my unit tests for yourself.

**How type unions are used**

In my world, you declare a type union like this:

```csharp
public class Person { }
public class Dog { }
public class Friend : TypeUnion<Person, Dog> {
    public Friend(Person p) : base(p) { }
    public Friend(Dog d) : base(d) { }
}
```

You inherit a type union from the TypeUnion class and use generic parameters that correspond to the types that the union can represent.

You can then create a type union as:

```csharp
var fr = new Friend(new Dog());
```

Test its type by:

```csharp
Assert.IsTrue(fr.Is<Dog>());
Assert.IsFalse(fr.Is<Person>());
```

Cast it to one of the types they represent:

```csharp
var d = fr.As<Dog>();
```

Or use it with the 'match' operator (fully explained in an upcoming post):

```csharp
var r = F.Match(fr,
    f => f.Is<Dog>(), f => f.As<Dog>().ToString(),
    f => f.Is<Person>(), f => f.As<Person>().ToString());
Assert.AreEqual(r, new Dog().ToString());
```

Or the slightly more pleasing:

```csharp
r = F.Match(fr,
        (Person p) => p.ToString(),
        (Dog d) => d.ToString());
Assert.AreEqual(r, new Dog().ToString());
```

You get the idea.

**How they are implemented**

Nothing really sophisticated going on here. Let's take as an example a type union that can represent two types. I have versions that go to 5 types in the zip file.

First of all a TypeUnion is a Record:

```csharp
public class TypeUnion<T1, T2> : Record<T1, T2> {
```

It has overloaded constructors to create a type union of a particular type:

```csharp
public TypeUnion(T1 t1)
    : base(t1, default(T2)) {
    UnionType = t1.GetType();
}
public TypeUnion(T2 t2)
    : base(default(T1), t2) {
    UnionType = t2.GetType();
}
```

UnionType is used to 'remember' which type it is:

```csharp
protected Type UnionType;
```

It also has properties to return the objects of all the types that can be stored:

```csharp
protected T1 Type1 { get { return state.Item1; } }
protected T2 Type2 { get { return state.Item2; } }
```

The 'Is' operator is simply implemented as:

```csharp
public bool Is<K>() {
    return typeof(K).IsAssignableFrom(UnionType);
}
```

And the 'As' operator looks like so:

```csharp
public K As<K>() {
    if (!Is<K>())
        throw new Exception(string.Format(
          "In a TypeUnion cannot cast from {0} to {1}",
          UnionType.Name, typeof(K).Name));
    if (typeof(T1) == UnionType)
        return (K)(object) Type1;
    if (typeof(T2) == UnionType)
        return (K)(object) Type2;
    throw new Exception("Shouldn't get here");
}
```

I leave as an exercise to the reader to understand what happens if T1 and T2 are the same type or inherit from the same type. I could have written code to handle this case in a more explicit manner, but didn't.

Also, by reviewing my code I found an obvious bug in my Is<K>/As<K> code. I fixed it and re-posted the zip file in the second post of this series.

Now back to the beach. Next post is on the 'match' operator.
