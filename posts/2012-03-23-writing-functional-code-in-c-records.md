---
id: 81
title: Writing functional code in C++ – Records
date: 2012-03-23T08:11:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=81
description: "Can we bring F#-style immutable records to C++? Join us as we explore three different approaches, from obvious to clever, complete with structural equality and macro magic. Because even C++ deserves some functional data structures"
categories:
  - C
tags:
  - C++
  - functional
---
This is the first of a series of posts about writing functional code in C++.  My goal is different from [FC++](http://www.cc.gatech.edu/~yannis/fc++/), which is a full fledged 'environment' to write functional code. Instead, I want to experiment with some of the new C++ 11 language features and see if one can build reasonably looking functional code and stay pretty close to the language. The idea is to judiciously use macros and external libraries to build a thin layer on top of the language that doesn't change the performance characteristics of it (aka it doesn't slow it down) and integrates fine with existing C++ code.

Think of it as an attempt to answer the question: is there a way to write C++ code in a functional style without loosing its 'C++sness'? We won't attempt to be as type safe or syntactically pleasing as Haskell or F# , but we'll attempt to stay as fast and flexible as C++ and make it functional enough to be interesting.

Thanks to Steve Bower and Ganesh Sittampalam for reviewing and to Andy Sawyer for giving me so much feedback that this post can be considered a co-authorship. Code for this post is [here](https://github.com/lucabol/BlogCppFunctional).

Let's first talk about the data types that you typically find in a functional language. Let's start with Records. They are not part of the functional model per se. You can do without them and just use algebraic data types and tuples. But they are damn convenient, and  most functional languages (i.e. Haskell, Clojure, etc…) have them now. We start from them because they map naturally to C++. Records are just like structs, but immutable and having structural equality.

In F# your vanilla record looks like this:

```fsharp
type Person = {
    Name: string
    Id: int
}
```

Nice and simple. With C++, you become more verbose. A first attempt would be:

```cpp
struct Person {
    const string Name;
    const int Salary;
};
```

Which looks nice and easy, but doesn't quite work because more often than not you need to be able to compare two records for structural equality (which means the value of their fields, not the pointer in memory, defines equality). Records in functional languages automatically support that. But the syntax gets on the ugly side:

```cpp
struct Person {
    const string Name;
    const int Salary;
    bool operator==(const Person& other) const { return Salary == other.Salary && Name == other.Name;}
    bool operator!=(const Person& other) const { return !(*this == other);}
};
```

We'll see how to simplify the syntax later. The syntax on the creation side is not too bad:

```cpp
Person p = {"Bobby", 2};
```

Let's call the above representation, the obvious one. Let's consider two variations on this scheme. The first one is useful if you want to make your records interoperable with C or with other C++ compilers. 

A full discussion of how to achieve these goals would be very long. It will go about discussing what [POD](http://stackoverflow.com/questions/146452/what-are-pod-types-in-c) types are and how their definition [got more precise](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2007/n2342.htm) in C++ 11.

You can look at my experimentations on pod, standard layout and trivially constructible types [here](https://github.com/lucabol/FunctionalCpp/blob/master/records.cpp). My summary is pretty simple, if you want to achieve all the goals above, you got to use C structs that contain C-compatible types. No const, strings or STL libraries allowed.

The above class would then become:

```cpp
struct Person {
    char Name[20];
    int Salary;
    bool operator==(const Person& other) const { return Salary == other.Salary && !strcmp(Name,other.Name);}
    bool operator!=(const Person& other) const { return !(*this == other);}
};
```

Obviously, not being able to use strings or STL collections in your record is a big limitation, but in certain cases you might be able to live with it.  Let's call this representation, the pod one.

You would think you can make the syntax better by doing something like the below:

```cpp
struct _Person {
    int id;
    char name[20];
    pod_equality(_Person);
};    
```

Where pod_equality is defined as below:

```cpp
#define pod_equality(Record)                                                                 \
       bool operator==(const Record& other) const {                                          \
              static_assert(std::is_trivial<Record>::value, "Not trivially copyable");       \
              return memcmp(this, &other, sizeof(Record)) == 0;}                             \
       bool operator!=(const Record& other) const { return !(*this == other);}
```

But you would be wrong (as I was for a while), as comparing memory values doesn't work in this case because of the padding that the compiler can insert between fields. Such padding can contain random value (whatever was on the stack, for example) which would make the equality return false for structurally equal objects. Also this scheme fails for floating point types (i.e. NaN and signed zeros).

An alternative representation for records, which nicely separates constness from the structure of your record is below. It does have some some advantages that we'll look at, but in its raw form it is yet more syntax:

```cpp
namespace Mutable {
    struct Person {
        string Name;
        int Salary;
        bool operator==(const Person& other) const { return Salary == other.Salary && Name == other.Name;}
        bool operator!=(const Person& other) const { return !(*this == other);}
    };
}
typedef const Mutable::Person Person;
```

Let's call this representation, the immutable one. Let's give these guys some usage and talk about their trade-offs. If you want to write a function that increase someone salary, you would write it like this:

```cpp
template<class T>
T rise_salary1(const T& p) {
    T ret = { p.Name, p.Salary + 1000 };
    return ret;
}
```

This looks nice and clean, unless your record has a lot of fields. Let me tell you, in real application it probably does. For example:

```cpp
namespace Mutable {
    struct foo {
        int value1;
        int value2;
        int value3;
        int value4;
        int value5;
        int value7;
        int value6;
        int value8;
        int value9;
    };
}
typedef const Mutable::foo foo;
foo increment_value7( const foo& f )
{
     foo tmp = { f.value1, f.value2, f.value3, f.value4, f.value5, f.value6, f.value7+1, f.value8 };
     return tmp;
}
```

Thanks to Andy for this example. BTW: did you spot the bug at first sight? What about the other one?

So this syntax is problematic. True to be told, part of the problem is in the sub-optimal initialization syntax in C++. If you could use named parameters, it would be more difficult to introduce bugs, but the syntax would still be ugly. You really need something like the F# syntax:

```fsharp
let r1 = {f = 0.2; k = 3}
let r2 = {r1 with f = 0.1}
```

Can we do something like that? Well, if we are willing to pass the Mutable one around, we can write this:

```cpp
template<class T>
T rise_salary2(const T& p) {
    T ret(p);
    ret.Salary += 1000;
    return ret;
}
```

Or even this:

```cpp
template<class T>
T rise_salary3(T p) {
    p.Salary += 1000;
    return p;
}
```

But that doesn't make us happy, does it? The whole point of making things const is that you want them to be const.  If you pass around mutable ones, who knows what's going to happen inside the method?

There is a middle ground that might be acceptable, which is to write functions so that their interface takes immutable records, but inside the function they operate on mutable ones. This is not a bad pattern in general, as having mutable versions of your immutable records might come useful for optimizing certain algorithms. Luckily the casting rules of C++ favour the bold, so the below works:

```cpp
Person rise_salary_m(const Person& p) {
    Mutable::Person ret(p);
    ret.Salary += 1000;
    return ret;
}
```

And doesn't look too bad either.

Now let's talk syntax. Defining a record is still a lot of typing (and a lot of reading if you are maintaining the code). F# does it like this:

```fsharp
type Person = {
    Name: string
    Id: int
}
```

The best I came up with looks like this:

```cpp
RECORD2(Person,
          string, Name,
          int,    Salary);
```

And you need a lot of those macros depending on how many fields your record has. You can write this macro to expand to either the Obvious or Immutable representation trivially. It is a bit more complex for the Pod one because of the interesting C++ array declaration syntax with the number of elements after the name of the field.

For the Obvious one it looks like this:

```cpp
#define RECORD2(n, t1, f1, t2, f2)                                                            \
    struct n {                                                                                \
        const t1 f1;                                                                          \
        const t2 f2;                                                                          \
                                                                                              \
        bool operator==(const n& other) const { return f1 == other.f1 && f2 == other.f2;}     \
        bool operator!=(const n& other) const { return !(*this == other);}                    \
    };
```

All the usual concerns about macros apply. Moreover all your fields need to have a meaningful == operator.

To summarize, we have found three different representations of records in C++ and tried to alleviate the syntax burden with some macro magick. We'll go wild in macro-land when we talk about discriminated unions.
