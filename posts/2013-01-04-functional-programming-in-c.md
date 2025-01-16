---
id: 1119
title: Functional programming in C
date: 2013-01-04T14:45:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=134
description: "What if we took C, sprinkled it with GCC extensions, and made it dance like a functional language? Join us on this wild ride where discriminated unions meet macros, and nested functions pretend to be lambdas. Warning: Microsoft compiler users need not apply"
categories:
  - C
  - Functional
tags:
  - C
  - functional
---
This post/program (as I’m writing it in literate style) is a continuation of my previous posts about functional programming in C++. I promise I’m not going to post about doing it in assembly language (I think) ….

I came to like the simplicity of C very much and got interested in how you could write functional code in it.

There is one irritating thing about C as a viable programming language. Microsoft’s compiler support is not good. It just supports ANSI C, not C99 or C11. So, if you want to use more modern idyoms, you got to use gcc or clang. In this post I assume you use gcc. I will point out the gcc specific extensions.

Also, the C standard library is pretty limited, so I decided to use GLib to complement it. I also created some macros to simplify the syntax. I never understood why people like templates and think macros are evil. It takes me all of 5 minutes to do a -E on GCC to debug the result of a macro expansion. With templates, well, that’s different.

So, in summary, this post is about how you can write functional code in C, perhaps with some gcc extensions and certainly with some macro tricks. Let’s call it funkyC (thanks Ian ). I’m going to show how to use it first. Next post I’m going to show how it’s implemented.

## Discriminated unions in C
With a bit of macro magic, you can get a decent looking discriminated union syntax. First we need to include the correct headers. lutils.h is where all the macros are defined.
~~~c
#include <glib.h>
#include <stdio.h>
#include <assert.h>
#include <stdbool.h>
#include <signal.h>
#include <string.h>

#include "lutils.h"
~~~
Then you can declare a discriminated union with the syntax below. It suffers from two problems: repeting the list of possible types in union_decl and repeating the name of the discriminated union in union_end. Perhaps there is a way to avoid that, but I haven’t found it.

The syntax for the union_type call is the same as you would use inside a struct declaration. We’ll see how this works when we look at lutils.h.
~~~c
union_decl  (Car, Volvo, Fiat, Ferrari)
union_type      (Volvo,     int x; double y;)
union_type      (Fiat,      char* brand, *model;)
union_type      (Ferrari,   char* brand, *model;)
union_end   (Car)
~~~
We can create a Car either on the stack, as below, or on the heap and we can set its value with union_set.

Notice the usage of the new struct construction syntax to simulate optional named parameters in C. I would prefer not to have a dot at the start of the name, but overall it is beautiful (if I can say that myself).
~~~c
static void printCar(Car*);

static void testUnion() {
    Car c;

    union_set   (&c, Volvo, .x = 3, .y = 4);
    printCar    (&c);
    union_set   (&c, Ferrari, .brand = "Ferrari");
    printCar    (&c);
    union_set   (&c, Fiat, .brand = "Fiat", .model = "234");
    printCar    (&c);
}
~~~
You can then access values inside your discriminated union with normal if statements.
~~~c
static void testCar(Car*, char const *);

static void printCar(Car* c) {

    if(c->kind == Volvo) {
        int x = c->Volvo.x;
        g_assert_cmpint(x, ==, 3);
    }
~~~
Or perhaps you want the equivalent of a match statement in F# (aka an expression that returns a value based on the type of the discriminated union). Notice that, as logical, all the expressions need to return the same type. That’s why union_fail takes a value of the expression type.
~~~c
    char temp[40];

    char* value =   c->kind == Volvo    ?   itoa(c->Volvo.x, temp, 10)
                  : c->kind == Ferrari  ?   (void)c->Ferrari.model, c->Ferrari.brand
                  : c->kind == Fiat     ?   c->Fiat.model
                                        :   union_fail("Not a valid car type");
~~~
If you are willing to be gcc specific, then your expression can be comprised of multiple statements, of which the last one returns the value of the expression. This allows a much more flexible syntax for your match clauses.
~~~c
#ifdef __GNUC__

    value       =   c->kind == Volvo    ? ({
                                            struct Volvo* it = &c->Volvo;
                                            itoa(it->x, temp, 10);
                                          })
                  : c->kind == Ferrari  ?   (void)c->Ferrari.model, c->Ferrari.brand
                  : c->kind == Fiat     ?   c->Fiat.model
                                        :   union_fail("Not a valid car type");

    testCar(c, value);

#endif // __GNUC__
}
~~~
We then use the super simple test framework in GLib to make sure that it all works as expected …
~~~c
static void testCar(Car* c, char const * value) {
    if(c->kind == Volvo) g_assert_cmpstr(value, ==, "3");
    else if (c->kind == Fiat) g_assert_cmpstr(value, ==, "234");
    else if (c->kind == Ferrari) g_assert_cmpstr(value, ==, "Ferrari");
    else g_assert_not_reached();

}
~~~
## Nested functions and lambda variables
GCC has many other cool extensions. A very simple one is nested functions. It allows you to nest functions :-) Look at the definition of doA and f2 in the function below. Putting together nested functions and block statement expressions allows you, with some macro magic, to define lambda functions in your code (from here ).

Remember that lambdas (aka nested functions) are allocated on the stack. They are very fast, but you cannot store their pointer into a gloal table (unless such table is used while the stack for this function is alive).

In such cases, you have to create a proper function. But for the other 90% of use cases, they work pretty well. They are lambdas in the spirit of C: very fast, but error prone …
~~~c
#ifdef __GNUC__

static void testLambda() {

    typedef int (*aFunc) (int);

    aFunc doA(aFunc f){

        int k(int i) {
            return f(i) + 3;
        }
        return k;
    }

    int clos = 2;

    int f2 (int i) {return i;}
    aFunc b = doA(lambda (int, (int p) {return p + clos;}));

    g_assert_cmpint(b(3), ==, 8);
}
~~~
## Automatic cleanup of local variables
This is not a functional topic per se, but something that always annoyed me tremendously about C. The fact that you cannot define the equivalent of the using statement in C#, or destructors in C++. Well, now you can. Or not?

Again, if you are willing to be GCC specific, you can use an attribute (more on this in the upcoming implementation post) to associate a cleanup function that gets called when your variable goes out of scope. In this case, I wrapped the free case in a nice looking macro.

But that doesn’t really work. You would certainly want such function to be called on any kind of exit from the enclosing scope (aka via exit(), abort() or longjmp()). Alas, that doesn’t happen.

This reduces the usefulness of this mechanism tremendously. Probably too much in that it lulls you into a false sense of security. You still need to free your resources in the error path of your application.
~~~c
static void testAutomaticCleanup() {
    char* stack_alloc() {
        auto_free char* b = g_malloc(10000);
        memset(b, '#', 10000);
        return b;
    };

    char * c = stack_alloc();
    g_assert(*c != '#');
}

#endif
~~~
## Data structures
GLib comes with a vast library of data structures to use, not too different from the .NET framework or Java. For example, below you have a single linked list …
~~~c
static void testGLib() {
     GSList* list = NULL;

     list = g_slist_append(list, "Three");
     list = g_slist_prepend(list, "first");
     g_assert_cmpint(g_slist_length(list), ==, 2);

     list = g_slist_remove(list, "first");
     g_assert_cmpint(g_slist_length(list), ==, 1);

     g_slist_free(list);
}
~~~
## Wrapping up
There you go, rising the level of abstraction of C, still keeping it very fast (if you are willing to be gcc bound).

There are other features in functional programming languages that are not in this post. Maybe I’ll get around to macro my way into them eventually, maybe not.

In the next post we’ll talk about how all of this is implemented. Below is the code for running the testcases.
~~~c
int runTests(int argc, char* argv[]) {
    g_test_init(&argc, &argv, NULL);

    if(g_test_quick()) {
        g_test_add_func("/utils/automatic_cleanup", testAutomaticCleanup);
        g_test_add_func("/utils/lambda", testLambda);
        g_test_add_func("/utils/Union", testUnion);
        g_test_add_func("/utils/SList", testGLib);
    }

    return g_test_run();
}

int main(int argc, char *argv[]) {
    return runTests(argc, argv);
}
~~~
