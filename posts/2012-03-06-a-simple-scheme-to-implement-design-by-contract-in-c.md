---
id: 78
title: A simple scheme to implement Design by Contract in C++
date: 2012-03-06T16:42:58+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=78
categories:
  - C
tags:
  - C++
  - functional
---
Recently I got interested in C++ again. The new lambda functions in C++ 11 open up a world of opportunities for C++ programmers. I'll talk more about how you can write functional code in C++ 11 in upcoming posts. For now let's look at design by contract.

[Design by contract](http://en.wikipedia.org/wiki/Design_by_contract) is a development style promoted by&#160; [Bertrand Meyer](http://en.wikipedia.org/wiki/Bertrand_Meyer) and it is implemented in his own [Eiffel programming language](http://en.wikipedia.org/wiki/Eiffel_%28programming_language%29). At core, it advocates using preconditions, postconditions and invariants.

An invariant is an assertion that always holds true for a class after the class has been fully constructed and if the code is not executing inside a method. As a user of the class, you always observe the invariant to be true. As an implementer of the class, you can be assured that the invariant is true before a method is entered and you need to make the invariant true again by the time your method exits.

A preconditions is an assertion that needs to hold true at the start of a function, for the postcondition to be true at the end of it. Taken together, invariant, precondition and postcondition define the contract between the implementer and the user of a class.

Code for this post is [here](https://github.com/lucabol/FunctionalCpp/blob/master/dbc.hpp) and [here](https://github.com/lucabol/FunctionalCpp/blob/master/dbc.cpp). Thanks to Andy Sawyer, Steve Bower and Ganesh Sittampalam for reviewing my code and suggesting improvements.

Preconditions are simple and everyone uses them. They are those little _if_ statements that you put at the start of your functions to make sure that the caller has given you the right parameters.

```cpp
double divide(double x, double y) {
    if(y == 0) throw new exception("y cannot be 0");
    …
}
```

These little 'if' statements don't really make the precondition stand out. They can be confused with other, unrelated, 'if' statements that do completely different semantic things. A more readable alternative is:

```cpp
double divide(double x, double y) {
    requires(y != 0);
    …
}
```

Not an impressive difference, for sure, but kind of nice. The evil macro looks like this:

```cpp
#ifndef ___PRECOND
#define requires(F) {if((!(F))) throw preexception(__FILE__, __LINE__,"Pre-condition failure: " #F);};
#else
#define requires(F)
#endif
```

Note that the exception maintains information not just about the file and line number of the failure, but also a textual representation of the failed condition. Such things you can do with macro magick.

Postconditions are trickier. In the case of a side-effect free (pure) function, a postcondition asserts something of interest about the return value. In the case of a class, it asserts something of interest about the state of the class before and after the execution of the method.

Let's start with a pure function. I like to have all my assertion at the start of the function to allow reasoning about it without looking at implementation details. But that poses the problem that the result is available just at the end of the function.&#160; My solution is to enforce this idiom:

```cpp
double divide(double x, double y) {
    double result;
    requires(y != 0);
    ensures(result < x); // Silly, just to falsify it in tests
    …
    return result;
}
```

So you need to declare your result upfront. That is the biggest limitation of the overall solution in my opinion.&#160; If that is acceptable to you, the trick now is how to execute the postcondition test before the method exits. We can do that by storing a lambda and executing it in the destructor:

```cpp
typedef std::function<bool ()> ___dbcLambda;
class ___post {
public:
    ___post(const char *file, long line, const char *expr, const ___dbcLambda& postF)
        : _f(postF),
          _file(file),
          _line(line),
          _expr(expr)
    {}
    ~___post()
    {
        if( !std::uncaught_exception() && !_f() )
        {
            throw postexception(_file,_line,_expr);
        }
    }
private:
    const ___dbcLambda _f;
    const char * const _file;
    const long _line;
    const char * const _expr;
};
```

You might think that you shouldn't throw exceptions in a destructor. That is something I never understood about the [RAII](http://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization) pattern in C++. If I choose to use exceptions as my error notification method, how am I supposed to get notified if there is a problem releasing a resource in RAII, other than by throwing an exception in the destructor?

Maybe because of this, the standard has an uncaught_exception() function that allows you to check if an exception has been thrown, so that you don't throw another one during stack unwinding. If you really don't like throwing in the destructor, feel free to assert.

You might be worried about performance, but you really shouldn't as you can disable all these macros in Release.

The macro then creates a ___post class on the stack.

```cpp
#define ensures(F) \
    int ___UNIQUE_LINE = __LINE__;  \
    auto ___UNIQUE_POST = ___post( __FILE__, __LINE__, "Post-condition failure:" #F, [&](){return (F);});
```

The UNIQUE stuff is messy business. Part of it is by design and it is used to make sure that each __post variable has a unique name to have multiple 'ensures' in a function. The other part is a workaround for [this](http://social.msdn.microsoft.com/Forums/en/vcgeneral/thread/2c4698e1-8159-44fc-a64c-d15220acedb8) msvc bug. Let me know if you want more details. I suspect there is a better way to do it.

Here is the full enchilada …

```cpp
#define ___MERGE(a, b) a##b
#define ___POST(a) ___MERGE(___postcond,a)
#define ___UNIQUE_POST ___POST(__LINE__)
#define ___LINE(a) ___MERGE(___line, a)
#define ___UNIQUE_LINE ___LINE(__LINE__)
```

The case in which a postcondition is used inside a method of a class is even trickier because the postcondition must be able to compare the state of the class at the entrance of the method to the state of the class at its exit. Assuming a Counter object with an Add method and assuming '___pre' captures the state of the counter at the start of the method, you'd like to write something like:

```cpp
void Add(int x) {
    ensuresClass(this->c_ == ___pre.c_ + x);
    …
}
```

Now, this is tricky. The only way to capture the 'old' state in '___pre' is by making a copy of it and store it there. This is what the code below does:

```cpp
#define ensuresClass(F) \
    auto ___pre(*this); \
    auto ___UNIQUE_POST = ___post( __FILE__, __LINE__, "Post-condition failure: " #F, [&](){return (F);});
```

More troubling is the possibility that the class doesn't have a copy constructor. In that case you explicitly need to associate a value with '___pre2' by passing it as the first parameter to the appropriate macro as in the code below:

```cpp
void Add(int x) {
    ensuresClass2(this->c_, c_ == ___pre2 + x);
}
```

Which is implemented as follows:

```cpp
#define ensuresClass2(ASS,F) \
    auto ___pre2(ASS); \
    auto ___UNIQUE_POST = ___post( __FILE__, __LINE__, "Post-condition failure: " #ASS " is ___pre2 in " #F, [&](){return (F);});
```

And I know about the giant ass …

Now for invariants. The user should implement an isValid() method on his class as below:

```cpp
bool isValid() { return c_ >= 0;}
```

Then he should add an 'invariant()' call at the start of each method, at the end of each constructor and at the start of each destructor:

```cpp
void Add(int x) {
    invariant();
    requires(x < 10);
    ensures(this->c_ == ___pre.c_ + x);
    …
}
```

This calls the 'isValid' function at the start of the method and at the end of it using the same destructor trick:

```cpp
#define invariant() \
    if(!(this->isValid())) throw preexception(__FILE__, __LINE__,"Invariant failure"); \
    auto ___UNIQUE_INV = ___post( __FILE__, __LINE__, "Invariant failure", [&](){return this->isValid();});
```

All the above machinery is not at all equivalent to having such constructs in the language, but it is simple enough and with a decent enough syntax to be interesting.

Now a caveat: I have no idea if any of this works. It does work in my examples and its behaviour seems reasonably safe to me, but I haven't tried it out on any big codebase and haven't stressed it enough for me to be confident recommending its usage. So, use it at your own risk, let me know how it goes.
