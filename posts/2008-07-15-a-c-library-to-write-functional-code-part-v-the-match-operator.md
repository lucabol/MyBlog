---
id: 453
title: 'A C# library to write functional code - Part V - The Match operator'
date: 2008-07-15T05:46:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/07/15/a-c-library-to-write-functional-code-part-v-the-match-operator/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/07/15/a-c-library-to-write-functional-code-part-v-the-match-operator.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "8732828"
orig_parent_id:
  - "8732828"
orig_thread_id:
  - "594875"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/07/15/a-c-library-to-write-functional-code-part-v-the-match-operator.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="A C# library to write functional code  - Part V  - The Match operator" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/07/15/a-c-library-to-write-functional-code-part-v-the-match-operator/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator This is my last post of this series. It is about the match operator. To the untrained eyes this operator might look like a case statement. But..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="A C# library to write functional code  - Part V  - The Match operator" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/07/15/a-c-library-to-write-functional-code-part-v-the-match-operator/" />
    <meta name="twitter:description" content="Other posts in the series: Part I  - Background Part II  - Tuples Part III  - Records Part IV  - Type Unions Part V  - The Match operator This is my last post of this series. It is about the match operator. To the untrained eyes this operator might look like a case statement. But..." />
    
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

This is my last post of this series. It is about the _match_ operator. To the untrained eyes this operator might look like a case statement. But they are different.

The _match_ operator combines control flow and decomposition in a single construct. As it often happens, even if these two things are well known concepts, putting them together gives you a different perspective on your code.

I have to admit that the similarity with a case statement triggered all sorts of bad reactions in my OO trained mind. Phrases from wise gurus on the tone of never use an 'if' statement was echoing in my mind. After a while I got over it and enjoyed the power that this operator gives.

In this library we won't get close to the beauty of the _match_ operator in functional languages (i.e. F#), especially the decomposition piece. There might be a way to do better than this in C#, but this was enough for my purpose of learning about functional programming, so I didn't investigate further. Learning was my real goal.

**How to use it**

There are two versions of this operator. Let's start from the more eye pleasing one.

Let's assume a discriminated union like the following:

```csharp
public class Node : TypeUnion<int, string> {
    public Node(int i) : base(i) { }
    public Node(string s) : base(s) { }
    public int IntNode { get { return Type1; } }
    public string StringNode { get { return Type2; } }
}
```

I can then match against this union with the following code:

```csharp
var no = new Node(35);
r = F.Match(no,
                (int i)    => (i + 3).ToString(),
                (string s) => s
            );
Assert.AreEqual("38", r);
```

Note that the _match_ operator behaves a bit like a case statement, but it also gives you the 'right' type on the right of the '=>' for you to write code against.

I have to admit I'm rather happy of this syntax, but it has one severe limitation. You need to specify all the types of the type union and they have to be in the same order. For example, in the previous code I cannot match against _string_ first and _int_ second. I consider this to be a big deal.

A different implementation of match that doesn't have that limitation is as follows:

```csharp
no = new Node("35");
r = F.Match(no,
    n => n.Is<int>(),   n => (n.As<int>() + 3).ToString(),
    n => n.Is<string>(),n => n.As<string>());
Assert.AreEqual("35", r);
```

Rather less pleasing to the eyes, but more robust to use.

By using this more generic version, you can obviously match against all the constructs we described in this series. I.E. against _Tuples_:

```csharp
var t = F.Tuple("msft", 10, "Nasdaq");
var r = F.Match(t,
    i => i.Item2 < 5 && i.Item3 == "OTC",          i => i.Item1 + " is low price OTC stock",
    i => i.Item3 == "OTC",                         i => i.Item1 + "is a normal OTC stock",
    i => i.Item3 == "Nasdaq",                      i => i.Item1 + " is a Nasdaq stock");
Assert.AreEqual("msft is a Nasdaq stock", r);
```

Or against sequences:

```csharp
var i1 = new int[] { 1, 2, 3, 4, 5, 6, 7 };
var r1 = F.Match(i1,
                s => s.SequenceEqual(new int[] { 1, 2}),    s => s.Where(i => i < 4),
                s => s.First() == 2,                        s => s.Where(i => i == 1),
                s => s.Last() == 6,                         s => s.Select(i => i * i),
                s => true,                                  s => s.Where(i => i < 7));
Assert.IsTrue(i1.Take(6).SequenceEqual(r1));
```

The match operator, as I defined it, is very flexible (probably too flexible as it doesn't use the type system to enforce much).

**How it is implemented**

Let's start from the special _match_ against union types: the one that is beautiful but flawed. Its implementation looks just like this (I just show the two parameters version):

```csharp
public static R Match<T1, T2, R>(
                           this TypeUnion<T1, T2> u,
                           Func<T1, R> f1, Func<T2, R> f2) {
    if (u.Is<T1>()) return f1(u.As<T1>());
    if (u.Is<T2>()) return f2(u.As<T2>());
    throw new Exception("No Match for this Union Type");
}
```

It is easy to see the reason for the limitations of this function. The same thing that gives you type inference (nice to look at) also gives you the problem with the ordering of lambdas. Also note the I originally intended to have these as extension methods. In practice I ended up liking more the F.Match syntax. De gustibus I assume

The more general version looks like this:

```csharp
public static R Match<T, R>(this T t,
    Func<T, bool> match1, Func<T, R> func1,
    Func<T, bool> match2, Func<T, R> func2) {
    if (match1(t))
        return func1(t);
    if (match2(t))
        return func2(t);
    throw new Exception("Nothing matches");
}
```

Again, it is easy to see in the implementation that this is an extremely general thing: a glorified case statement really. This is the beauty of it (you can match against anything) and the ugliness of it (you can write anything as _match1_ of _func1_, even code that doesn't reference _t_ at all).

**How to use this series to learn functional programming**

Here is how I did it (it worked for me). Take this library and force yourself to write a medium size program using <u>just</u> these constructs.

I mean it. No objects, just records. No inheritance, just discriminated unions. Tuples to return values. Match operators everywhere. No iteration statements (for, while, etc), just recursion. Extensive use of sequence operators. After a while I noticed that all my functions had the same pattern: they just match against the input and produce an output, usually by calling other functions or recursively calling themselves.

Obviously, this is overcompensating. After a while you will realize the different trade offs that come with a functional vs OO style of programming. At that point you'll be able to get the best of the two. Or maybe you'll be royally confused

At that point I picked up F# and I'm now enjoying the fact that all these constructs are directly embedded in the language (and yes, you can use while statements too).
