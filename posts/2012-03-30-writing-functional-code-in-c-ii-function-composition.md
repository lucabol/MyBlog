---
id: 83
title: Writing functional code in C++ II – Function composition
date: 2012-03-30T10:11:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=83
description: "Beyond the 'big fat for loop': discover how Boost.Range and clever operator overloading can bring F#-style function composition to C++. With performance benchmarks to prove it won't kill your program. Because even C++ deserves some functional elegance"
categories:
  - C
tags:
  - C++
  - functional
---
Function composition is at the core of functional programming. You start by being very confident that certain very small functions are correct, you compose them in well known ways and you end up being very confident that your final program is correct.

You are very confident that the initial functions are correct because they are very small and side effect free. You are very confident that your program is correct because the means of composition are well known and generate functions that are themselves side effect free.

Such 'almost primitive' functions operate on data structures. Each functional language has its own set of data structures and 'almost primitive' functions. Probably the most famous ones are contained in the [haskell prelude](http://www.haskell.org/onlinereport/standard-prelude.html), but F# has similar ones. LINQ in C# is just such a set.

In this article I use the term functional composition in a broad sense as 'putting functions together', not in the more technical sense of f(g(x)): dot operator in Haskell or '>>' operator in F#.

Code for this post is [here](https://github.com/lucabol/FunctionalCpp). Thanks to Steve Bower and Andy Sawyer for review and comments.

Here is an example. The F# code below filters in the odd numbers from an array and doubles them. You have two logical operations, filtering and doubling.

```fsharp
let v = [|1;2;3;4;5;6;7;8;9;0|]
let transformed =
    v
    |> Seq.filter(fun i -> i % 2 = 0)
    |> Seq.map ((*) 2)
```

How would the code look in C++? There are many ways. One is the 'big fat for loop', or in C++ 11, for each:

```cpp
const int tmp[] = {1,2,3,4,5,6,7,8,9,0};
const vector<int> v(&tmp[0], &tmp[10]);
vector<int> filtered;
for(auto i: v)
{
    if(i % 2 == 0)
        filtered.push_back(i * 2);
}
```

This looks simple enough, apart from the initialization syntax that gets better with C++ 11. But it's simplicity is misleading. We have now lost the information that our computation is composed by a filter and a map. It's all intermingled. Obviously, the info is still there in some sense, but you need to read each line in your head and figure out the structure on your own. It is not readily apparent to the reader.

Obviously, things get much worse in a large program composed of several loops where each one does not trivial stuff. As for me, every time I indulge into the 'big fat for loop pattern', I end up regretting it either immediately or after some time when I have to make changes to the code. So I try to avoid it.

Wait a minute, you might say, what about STL algorithms? Aren't you supposed to use those?

The syntax to call them is not very compositional. You cannot take the result of an algorithm and pass it to another easily. It is difficult to chain them that way. Everything takes two iterators, even if 99% of the times you are just using begin and end. Moreover, you have to create all sort of temporary data structures for the sake of not modifying your original one. Once you have done all of that, the syntactic weight of your code overwhelm the simplicity of what you are trying to do.

For example, here is the same code using 'transform' for the 'map' part of the algorithm:

```cpp
vector<int> filtered;
copy_if(begin(v), end(v), back_inserter(filtered), [](int x) { return x % 2 == 0;});
vector<int> transformed;
transform(begin(filtered), end(filtered), back_inserter(transformed), [](int x) { return x * 2;});
```

I'm not arguing that STL is a bad library, I think it is a great one. It's just that its syntax is not very compositional. And that breaks the magic.

Luckily, help is on the way in the form of the [Range](http://www.boost.org/doc/libs/1_49_0/libs/range/doc/html/index.html) library and [OvenToBoost](https://github.com/faithandbrave/OvenToBoost). These libraries 'pack' the two iterators in a single structure and override the '|' operator to come up with something as below:

```cpp
auto result =
    v
    | filtered(   [] (int i) { return i % 2 == 0;})
    | transformed([] (int i) { return i * 2;});
```

If you use Boost lambdas (not sure I'd do that), the syntax gets even better:

```cpp
auto result =
    v
    | filtered(_1 % 2 == 0)
    | transformed(_1 * 2);
```

Ok, so we regained compositionality and clarity, but what price are we paying? Apart from the dependency from Boost::Range and OvenToBoost, you might think that this code would be slower than a normal for loop. And you would be right. But maybe not by as much as you would think.

The code for my test is [here](https://github.com/lucabol/FunctionalCpp/blob/master/range_performance.cpp). I'm testing the perf difference between the following code engineered to put in a bad light the most pleasing syntax. A for loop:

```cpp
int sum = 0;
for(vector<int>::const_iterator it = v.begin(); it != v.end(); ++it)
    if(*it < 50)
        sum += *it * 2;
return sum;
```

A Range based code using language lambdas (transformedF is a variation of [this](http://smellegantcode.wordpress.com/2011/10/31/linq-to-c-or-something-much-better/)):

```cpp
auto lessThan50 = v | filtered(    [](int i) { return i < 50;})
                    | transformedF([] (int i) { return i * 2;});
return boost::accumulate (lessThan50, 0);
```

A Range based code using two functors:

```cpp
auto lessThan50 = v | filtered(Filterer())
                    | transformed(Doubler());
return boost::accumulate (lessThan50, 0);
```

Where:

```cpp
struct Doubler {
    typedef int result_type;
    int operator() (int i) const { return i * 2;}
};
struct Filterer {
    typedef int result_type;
    bool operator() (int i) const { return i < 50;}
};
```

a Range based code using Boost lambdas:

```cpp
auto lessThan50 = v | filtered(_1 < 50)
                    | transformed(_1 * 2);
return boost::accumulate (lessThan50, 0);
```

And finally, some code using the STL for_each function:

```cpp
int sum = 0;
std::for_each( v.cbegin(), v.cend(),
    [&](int i){
        if( i < 50 ) sum += i*2;
    });
return sum;
```

Notice that I need to run the test an humongous number of times (10000000) on a 100 integers array to start seeing some consistency in results.  
And the differences that I see (in nanosecs below) are not huge:

```text
1>                         Language lambda: {1775645516;1778411400;0}
1>                          Functor lambda: {1433377701;1435209200;0}
1>                            Boost lambda: {1327829199;1326008500;0}
1>                                For loop: {1338268336;1341608600;0}
1>                             STL foreach: {1338268336;1341608600;0}
```

True to be told, by changing the code a bit these numbers vary and, in some configurations, the Range code takes twice as long.
 
But given how many repetitions of the test I need to run to notice the difference, I'd say that in most scenarios you should be ok.

The '|>' operator over collections is the kind of functional composition, broadly defined, that I use the most, but you certainly can use it over other things as well. You'd like to write something like the below:

```cpp
BOOST_CHECK_EQUAL(pipe("bobby", strlen, boost::lexical_cast<string, int>), "5");
```

And you can, once you define the following:

```cpp
template< class A, class F1, class F2 >
inline auto pipe(const A & a, const F1 & f1, const F2 & f2)
    -> decltype(REMOVE_REF_BUG(f2(f1(a)))) {
    return f2(f1(a));
}
```

Where REMOVE_REF_BUG is a workaround for a bug in the decltype implementation under msvc (it should be fixed in VS 11):

```cpp
#ifdef _MSC_VER
    #define REMOVE_REF_BUG(...) remove_reference<decltype(__VA_ARGS__)>::type()
#else
    #define REMOVE_REF_BUG(...) __VA_ARGS__
#endif
```

I didn't do the work of creating '>>' , '<<' and '<|' F# operators or wrapping the whole lot with better syntax (i.e. operator overloading?), but it certainly can be done.

Now that we have a good syntax for records and a good syntax for operating over collections, the next instalment will put them together and try to answer the question: how should I create collections of records and operate over them?
