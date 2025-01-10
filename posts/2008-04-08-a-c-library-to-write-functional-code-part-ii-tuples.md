---
id: 493
title: 'A C# library to write functional code - Part II - Tuples'
date: 2008-04-08T16:51:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "8369978"
orig_parent_id:
  - "8369978"
orig_thread_id:
  - "575453"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="A C# library to write functional code  - Part II  - Tuples" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator Tuples are a way for you not to name things. In Object Oriented languages&nbsp;you got to name everything. If you need to represent a bunch of data,..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="A C# library to write functional code  - Part II  - Tuples" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/04/08/a-c-library-to-write-functional-code-part-ii-tuples/" />
    <meta name="twitter:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator Tuples are a way for you not to name things. In Object Oriented languages&nbsp;you got to name everything. If you need to represent a bunch of data,..." />
    
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

[Tuples](http://en.wikipedia.org/wiki/Tuple) are a way for you not to name things. In Object Oriented languages you got to name everything. If you need to represent a bunch of data, you create a class for it.

There is a strange asymmetry in mainstream OO languages in that you can pass multiple parameters to a function, but you can return just one value. Granted, there are ways around it: you can use 'ref' in C# or return some sort of collection where things are stored. But by and large the model is: you pass many, you get one; if you need to return more than one, create a class to represent this 'bunch of data'. Tuples are a way for you not to create such a class.

Tuples are also much more than that. Once you have the language concept of 'a bunch of data without a name', you can create arrays of them, you can pass them as parameters, use them as local variables. Wherever you'd use a type, you can use a Tuple instead.

This is particularly appealing to me as I like to use classes almost exclusively to represent things that have a counterpart in the domain I'm modeling (i.e. Customer, Account). I don't like to create classes/structs just for the sake of temporarily put some data together.

You can create your own Tuple class in C#, but the syntax gets ugly. Syntax matter. Syntax helps you to think differently about your program. We have syntax for anonymous types, but given that they cannot escape the scope of a method, they cannot be used as full replacement for Tuples.

In any case, to my implementation. Here is how you create a Tuple:

```csharp
var t1 = F.Tuple(34, "bo", 2.3);
```

not too bad. In F# it is better: (34, bo, 2.3). And you often don't need the parenthesis. But still, my C# version is ok.

You then need to access its elements:

```csharp
var n = t1.Item1;
var s = t1.Item2;
```

In F# you usually access them by doing pattern matching, which gives a more intuitive syntax. But again, my C# syntax is not terrible.

Tuples need to have structural equality, which means that the following has to work:

```csharp
ArrayList mad1 = new ArrayList { new List<IEnumerable<string>> { new string[] { "bo" }, new string[] { "bo" } },
                               32, "bo", new int[] { 4, 5, 6 } };
ArrayList mad2 = new ArrayList { new List<IEnumerable<string>> { new string[] { "bo" }, new string[] { "bo" } },
                               32, "bo", new int[] { 4, 5, 6 } };
ArrayList mad3 = new ArrayList { new List<IEnumerable<string>> { new string[] { "bo" }, new string[] { "bo" } },
                               32, "bo", new int[] { 4, 5, 5 } };

Assert.AreEqual(F.Tuple(mad1, mad2, mad1), F.Tuple(mad2, mad1, mad2));
Assert.AreNotEqual(F.Tuple(mad1, mad2, mad1), F.Tuple(mad1, mad3, mad1));
```

You can use Tuples as return values, parameters, locals etc. Unfortunately, the syntax is ugly when Tuples are part of the signature of a function:

```csharp
public Tuple<string, IEnumerable<Tuple<string, ObservationHistory>>> Execute() {
}
```

With the above information, you can be a user of Tuples. From this point on, I'll talk about some details of the implementation (I also attach the full code to this post as a zip file).

```csharp
public class Tuple<T1> {
    public Tuple(T1 t1) {
        Item1 = t1;
    }
    public readonly T1 Item1;
    #region Equals, GetHashCode, ==, !=
}
public class Tuple<T1, T2> : Tuple<T1> {
    public Tuple(T1 t1, T2 t2) : base(t1) { Item2 = t2; }
    public readonly T2 Item2;
    #region Equals, GetHashCode, ==, !=
}
```

So, Tuples are classes, not structs. The reason for it is fully described in [this series of posts](http://blogs.msdn.com/lucabol/archive/2008/01/11/creating-an-immutable-value-object-in-c-part-v-using-a-library.aspx). They also inherit from one another. There are pros and cons to that. The main pros are that I had to write less code and that you can pass a Tuple<int, string> when a function expects a Tuple<int, string, int>. The main drawback is that you can pass a Tuple<int, string> when a function expects a Tuple<int, string, int>. Also notice the use of public fields. These is a problem with frameworks that insist on properties (i.e. Data Binding). Also, I just got to 5 as arity goes. The day I need 6 items, I'll add another one. It is boilerplate code (that I'd still like not to write).

The Equals method is a bit convoluted:

```csharp
internal static class Utils {
    public static void CheckNull<T>(T t) {
        if (t == null)
            throw new ArgumentNullException();
    }
}
```

```csharp
public override bool Equals(object right) {
    Utils.CheckNull(right);
    if (object.ReferenceEquals(this, right))
        return true;
    if (this.GetType() != right.GetType())
        return false;
    var rightT = right as Tuple<T1, T2, T3>;
    return base.Equals(rightT) && F.DSEquals(this.Item3, rightT.Item3);
}
```

I always get complaints when I show Equals methods that throw if null is passed in, but I stand by my logic, that the presence of null for these categories of 'structurally equal' classes is symptom of an error and I want to be notified. Returning false doesn't do that.

```csharp
internal static bool DSEquals<T>(T left, T right) {
    if (left == null && right == null)
        return true;
    if (left == null && right != null)
        return false;
    var len = left as IEnumerable;
    var ren = right as IEnumerable;
    if (len == null && ren == null)
        return left.Equals(right);
    if (len == null && ren != null)
        return false;
    if (len != null && ren == null)
        return false;
    return SequenceEqual(len, ren);
}
```

DSEquals check the content of the Tuple and forward to SequenceEqual in case one slot of the Tuple contains an IEnumerable.

```csharp
internal static bool SequenceEqual(IEnumerable en1, IEnumerable en2) {
    var enumerator = en2.GetEnumerator();
    foreach (var o in en1) {
        if (!enumerator.MoveNext())
            return false;
        if (!DSEquals(o, enumerator.Current))
            return false;
    }
}
```

SequenceEqual checks that the number of items in the enumerator is the same and recursively calls DSEqual to check structural equality for items at the same index in the two enumerators.

GetHashCode is trivial (and maybe trivially wrong, one of these days I'll learn everything about GetHashCode() ).

```csharp
public override int GetHashCode() {
    return base.GetHashCode() | Item3.GetHashCode();
}
```

The equality operators are equally simple.

```csharp
public static bool operator ==(Tuple<T1, T2, T3> t1, Tuple<T1, T2, T3> t2) {
    Utils.CheckNull(t1);
    Utils.CheckNull(t2);
    return t1.Equals(t2);
}
public static bool operator !=(Tuple<T1, T2, T3> t1, Tuple<T1, T2, T3> t2) {
    return !(t1 == t2);
}
```

And ToString() prints my favorite Tuple format.

```csharp
public override string ToString() {
    return string.Format("{0},{1}", base.ToString(), Item3.ToString());
}
```

I'm sure you can find plenty of issues in this code. As always, it is not 'production ready', it is more 'Luca having fun doing it'. In any case, there are some testcases in the solution to check the extent of my testing.

In the next post we'll look at Records.

[Functional.zip](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/08/36/99/78/Functional.zip)
