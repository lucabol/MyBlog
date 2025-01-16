---
id: 92
title: Writing functional code in C++ IV – Algebraic datatypes
date: 2012-04-27T09:29:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=92
description: "Move over Boost.Variant, there's a new discriminated union in town! Watch as we craft F#-style algebraic datatypes in C++ using the dark arts of macros. Sure, we lose some compile-time safety, but look at that sweet pattern matching syntax"
categories:
  - C
tags:
  - C++
  - functional
---
And here comes the guilt bit. I have the strong suspicion (but not certainty) that what I am doing here can be done with templates, but didn't take the time to do it. With that out of the way, let's go.

Code for this post is [here](https://github.com/lucabol/FunctionalCpp/blob/master/discriminated_union.cpp). Thanks to Steve Bower and Andy Sawyer for reviewing it.

[Algebraic datatypes](http://www.google.co.uk/url?sa=t&rct=j&q=algebraic%20datatypes&source=web&cd=1&ved=0CDIQFjAA&url=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FAlgebraic_data_type&ei=UmZ9T8fGOoK2hQeRk6i-DA&usg=AFQjCNGG2oS5s9Ir1NvaX-RRcarkvVAoig) (discriminated unions in F#) are a powerful concept in functional programming. They are the main way to represent type variation in your program. Very roughly, where object orientation uses derivation, functional programming uses algebraic datatypes. An entire book could be written on the theory of this, but the goal of this post is to see how we can map them to C++ without loosing C++ness.

When talking about this with C++ programmers, they always point me to boost variant. That doesn't do it for me for several reasons.

First of all, boost variants represent one of a fixed collection of types. Algebraic datatypes represent one of a fixed collection of <u>named</u> types. That means that a simple thing like the code below cannot be represented as variant:

```fsharp
type LivingEntity =
| Person of string  // name
| Dog of string     // name
```

Ok, ok maybe you could represent it by 'typifing' things using [boost strong typedef](http://www.boost.org/doc/libs/1_37_0/boost/strong_typedef.hpp), but things get ugly syntactically. Moreover, a lot of time the name is all you care about …

```fsharp
type Switch = On | Off
```

Are we going to strong typedef for such a simple thing? Oh boy. Even accepting the syntactic weight of all this, there are other issues in play. Discriminated unions are used extensively in functional programs. So you want a nice syntax to work with them Something like the below F# syntax:

```fsharp
let print living =
    match living with
    | Person(name) -> printfn "I'm a per named %s" name
    | Dog(name)    -> printfn "I'm a dog named %s" name
```

Which could be made even sweeter by using the 'function' keyword as below:

```fsharp
let print = function
    | Person(name) -> printfn "I'm a per named %s" name
    | Dog(name)    -> printfn "I'm a dog named %s" name
```

In boost variant, you either use the get<type> functions or you write a visitor function. In the first case you are probably going to write a chain of 'if' statements or a 'switch' statement. Both are confusing and come with plenty of syntactic weight. I don't really want to write a visitor like the one below for each 'match' in my code. The magic is gone.

```cpp
class times_two_visitor
    : public boost::static_visitor<>
{
public:
    void operator()(int & i) const
    {
        i *= 2;
    }
    void operator()(std::string & str) const
    {
        str += str;
    }
};
```

Ok, so boost variant doesn't really work for this. Remember that our overarching goal was to stay close to C++. The language itself has something that comes pretty close to what we want in the form of a union, or better a [tagged union](http://en.wikipedia.org/wiki/Tagged_union). Again, the types are not named, but maybe we can work that in.

It turns out that Jared [here](http://blogs.msdn.com/b/jaredpar/archive/2010/11/18/discriminated-unions-in-c.aspx) did all the hard work. The general idea is to use macros to hide the construction of a tagged union with methods to test the type and return the contained value. 

For example this code:

```cpp
DU_DECLARE(LivingEntity)
    DU_VALUE(Person,    string)
    DU_VALUE(Dog,       string)
DU_END
```

Becomes something like:

```cpp
struct LivingEntity {
    private:
        LivingEntity() {}
        unsigned int m_kind;
    public:
        static LivingEntity Person(const string& value) {
            LivingEntity unionValue;
            unionValue.m_kind = 19;
            unionValue.m_Person = value;
            return unionValue; }
        bool IsPerson() const {
            return m_kind == 19;
        }
        const string& GetPerson() const {
            (void)( (!!(m_kind == 19)) || (_wassert(L"m_kind == __LINE__", L"c:discriminated_union.cpp", 19), 0) );
            return m_Person; }
        string GetPerson() {
            (void)( (!!(m_kind == 19)) || (_wassert(L"m_kind == __LINE__", L"c:discriminated_union.cpp", 19), 0) );
            return m_Person; }
   private:
        string m_Person;

   …
```

You can see the outline of a tagged union (i.e. m_kind) with a constructor for each type (i.e. Person) and methods to test for at type and return its value. You can also see the storage for the value (i.e. m_Person).

The only thing in DU_DECLARE that is different from Jared's solution is the typedef below that allows not repeating the LivingEntity name in each DU_VALUE.

```cpp
#define DU_DECLARE(name)                        \
    struct name {                               \
    private:                                    \
        typedef name unionName;                 \
        name() {}                               \
        unsigned int m_kind;                    \
    public:
```

```cpp
#define DU_VALUE(entryName, entryType)                                                                      \
        static unionName entryName(const entryType& value) {                                                \
            unionName unionValue;                                                                           \
            unionValue.m_kind = __LINE__;                                                                   \
            unionValue.m_##entryName = value;                                                               \
            return unionValue;  }                                                                           \
        bool Is##entryName() const { return m_kind == __LINE__;}                                            \
        const entryType& Get##entryName() const { assert(m_kind == __LINE__); return m_##entryName; }       \
        entryType Get##entryName() { assert(m_kind == __LINE__); return m_##entryName; }                    \
    private:                                                                                                \
        entryType m_##entryName;                                                                            \
    public:
```

With all of that at your disposal it becomes easy to write:

```cpp
auto entity = LivingEntity::Dog("Bob");
DU_MATCH(entity)
    DU_CASE(Dog,   BOOST_CHECK_EQUAL(value, "Bob");)
    DU_CASE(Person,BOOST_CHECK(false);)
DU_MATCH_END
```

There are some beautiful things about this. First of all, the construction of any of such types is super simple. You even get intellisense!

Moreover the 'value' variable contains whatever was passed in the constructor for the object. So this is semantically equivalent, if not syntactically, to the match statement in F#.

Obviously the code part is not limited to a single instruction:

```cpp
DU_MATCH(entity)
    DU_CASE(Dog,
        cout << "I should be here";
        BOOST_CHECK_EQUAL(value, "Bob");
    )
    DU_CASE(Person,
        BOOST_CHECK(false);
    )
DU_MATCH_END
```

And for those of you addicted to braces, I venture:

```cpp
DU_MATCH(entity)
    DU_CASE(Dog,
    {
        cout << "I should be here";
        BOOST_CHECK_EQUAL(value, "Bob");
    })
    DU_CASE(Person,
    {
        BOOST_CHECK(false);
    })
DU_MATCH_END
```

They all work with the same macro definition. They expand to something along the line of:

```cpp
if(false) {}
    else if(entity.IsDog()) {
        auto value = entity.GetDog();
        BOOST_CHECK_EQUAL(value, "Bob");
    }
    else if(entity.IsPerson()) {
        auto value = entity.GetPerson();
        BOOST_CHECK(false);
    }
    else {
        throw match_exception();
    }
```

I've not reached the pinnacle of macro naming mastering with this one. Making them lowercase and risking a bit more on the conflict side would make the syntax much more palatable. I call it, as it is, not too bad.

The last 'else' clause assures you then if you add a new type to the discriminated union and forget to update one of the 'MATCH' clauses at least you get a run time error. That is not good. Functional languages would give you a compile time error, which is much better. Maybe with judicious use of templates you can bring the error at compile time.

The macros are trivial:

```cpp
class match_exception: std::exception {};
#define DU_MATCH(unionName) { auto du_match_var = unionName; if(false) {}
#define DU_CASE_TAG(entry, ...)                        \
    else if(du_match_var.Is##entry()) {                \
        __VA_ARGS__                                    \
    }
#define DU_CASE(entry, ...)                            \
    else if(du_match_var.Is##entry()) {                \
        auto value = du_match_var.Get##entry();        \
        __VA_ARGS__                                    \
    }
#define DU_DEFAULT(...)                                \
    else if(true) { __VA_ARGS__}
#define DU_MATCH_END else {throw new match_exception();} }
```

Let's now go back to our initial goal and see how far off we are. We were trying to do the following:

```fsharp
type LivingEntity =
| Person of string
| Dog of string
let print = function
    | Person(name) -> printfn "I'm a per named %s" name
    | Dog(name)    -> printfn "I'm a dog named %s" name
```

And here is what we ended up with:

```cpp
DU_DECLARE(LivingEntity)
    DU_VALUE(Person,    string)
    DU_VALUE(Dog,        string)
DU_END
auto print(LivingEntity en) -> void {
    DU_MATCH(entity)
        DU_CASE(Dog,    cout << "I'm a dog named " << value;)
        DU_CASE(Person, cout << "I'm a per named " << value;)
    DU_MATCH_END
}
```

In our Switch case:

```fsharp
type Switch = On | Off
```

You get the good looking:

```cpp
DU_DECLARE(Switch)
    DU_FLAG(On)
    DU_FLAG(Off)
DU_END
```

And along the way we lost compile time type safety in the very common case of adding new types to the discriminated union. That's bad.

Also some of you would strongly dislike the (ab)use of macros. As for me, it looks workable.
