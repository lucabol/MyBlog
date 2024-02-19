---
id: 83
title: Writing functional code in C++ II – Function composition
date: 2012-03-30T10:11:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=83
categories:
  - C
tags:
  - C++
  - functional
---
Function composition is at the core of functional programming. You start by being very confident that certain very small functions are correct, you compose them in well known ways and you end up being very confident that your final program is correct.

You are very confident that the initial functions are correct because they are very small and side effect free. You are very confident that your program is correct because the means of composition are well known and generate functions that are themselves side effect free.

Such ‘almost primitive’ functions operate on data structures. Each functional language has its own set of data structures and ‘almost primitive’ functions. Probably the most famous ones are contained in the [haskell prelude](http://www.haskell.org/onlinereport/standard-prelude.html), but F# has similar ones. LINQ in C# is just such a set.

In this article I use the term functional composition in a broad sense as ‘putting functions together’, not in the more technical sense of f(g(x)): dot operator in Haskell or ‘>>’ operator in F#.

Code for this post is [here](https://github.com/lucabol/FunctionalCpp). Thanks to Steve Bower and Andy Sawyer for review and comments.

Here is an example. The F# code below filters in the odd numbers from an array and doubles them. You have two logical operations, filtering and doubling.

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">v = [|1;2;3;4;5;6;7;8;9;0|]
</span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">transformed =
    v
    |&gt; Seq.filter(</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">i </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">i % 2 = 0)
    |&gt; Seq.map ((*) 2)
</span></pre>

How would the code look in C++? There are many ways. One is the ‘big fat for loop’, or in C++ 11, for each:

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">const int </span><span style="background:white;color:black;">tmp[] = {1,2,3,4,5,6,7,8,9,0};
    </span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">vector</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:blue;">int</span><span style="background:white;color:black;">&gt; v(&tmp[0], &tmp[10]);
    </span><span style="background:white;color:#2b91af;">vector</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:blue;">int</span><span style="background:white;color:black;">&gt; filtered;
    </span><span style="background:white;color:blue;">for</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">i:</span><span style="background:white;color:blue;"> </span><span style="background:white;color:black;">v)
    {
        </span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">(i % 2 == 0)
            filtered.push_back(i * 2);
    }</span></pre>

<span style="background:white;color:black;">This looks simple enough, apart from the initialization syntax that gets better with C++ 11. But it’s simplicity is misleading. We have now lost the information that our computation is composed by a filter and a map. It’s all intermingled. Obviously, the info is still there in some sense, but you need to read each line in your head and figure out the structure on your own. It is not readily apparent to the reader.</span>

<span style="background:white;color:black;">Obviously, things get much worse in a large program composed of several loops where each one does not trivial stuff. As for me, every time I indulge into the ‘big fat for loop pattern’, I end up regretting it either immediately or after some time when I have to make changes to the code. So I try to avoid it.</span>

<span style="background:white;color:black;">Wait a minute, you might say, what about STL algorithms? Aren’t you supposed to use those?</span>

<span style="background:white;color:black;">The syntax to call them is not very compositional. You cannot take the result of an algorithm and pass it to another easily. It is difficult to chain them that way. Everything takes two iterators, even if 99% of the times you are just using begin and end. Moreover, you have to create all sort of temporary data structures for the sake of not modifying your original one. Once you have done all of that, the syntactic weight of your code overwhelm the simplicity of what you are trying to do.</span>

<span style="background:white;color:black;">For example, here is the same code using ‘transform’ for the ‘map’ part of the algorithm:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:#2b91af;">vector</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:blue;">int</span><span style="background:white;color:black;">&gt; filtered;
    copy_if(begin(v), end(v), back_inserter(filtered), [](</span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">x</span><span style="background:white;color:black;">) { </span><span style="background:white;color:blue;">return </span><span style="background:white;color:gray;">x </span><span style="background:white;color:black;">% 2 == 0;});
    </span><span style="background:white;color:#2b91af;">vector</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:blue;">int</span><span style="background:white;color:black;">&gt; transformed;
    transform(begin(filtered), end(filtered), back_inserter(transformed), [](</span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">x</span><span style="background:white;color:black;">) { </span><span style="background:white;color:blue;">return </span><span style="background:white;color:gray;">x </span><span style="background:white;color:black;">* 2;});
</span></pre>

<span style="background:white;color:black;">I’m not arguing that STL is a bad library, I think it is a great one. It’s just that its syntax is not very compositional. And that breaks the magic.</span>

<span style="background:white;color:black;">Luckily, help is on the way in the form of the <a href="http://www.boost.org/doc/libs/1_49_0/libs/range/doc/html/index.html">Range</a> library and <a href="https://github.com/faithandbrave/OvenToBoost">OvenToBoost</a>. These libraries ‘pack’ the two iterators in a single structure and override the ‘|’ operator to come up with something as below:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">result =
        v
        | filtered(   [] (</span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">i</span><span style="background:white;color:black;">) { </span><span style="background:white;color:blue;">return </span><span style="background:white;color:gray;">i </span><span style="background:white;color:black;">% 2 == 0;})
        | transformed([] (</span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">i</span><span style="background:white;color:black;">) { </span><span style="background:white;color:blue;">return </span><span style="background:white;color:gray;">i </span><span style="background:white;color:black;">* 2;});</span></pre>

<span style="background:white;color:black;">If you use Boost lambdas (not sure I’d do that), the syntax gets even better:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">result =
        v
        | filtered(   _1 % 2 == 0)
        | transformed(_1 * 2);</span></pre>

<span style="background:white;color:black;">Ok, so we regained compositionality and clarity, but what price are we paying? Apart from the dependency from Boost::Range and OvenToBoost, you might think that this code would be slower than a normal for loop. And you would be right. But maybe not by as much as you would think.</span>

<span style="background:white;color:black;">The code for my test is <a href="https://github.com/lucabol/FunctionalCpp/blob/master/range_performance.cpp">here</a>. I’m testing the perf difference between the following code engineered to put in a bad light the most pleasing syntax. A for loop:</span>

<pre class="code"><span style="background:white;color:black;">        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">sum = 0;
        </span><span style="background:white;color:blue;">for</span><span style="background:white;color:black;">(</span><span style="background:white;color:#2b91af;">vector</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:blue;">int</span><span style="background:white;color:black;">&gt;::</span><span style="background:white;color:#2b91af;">const_iterator </span><span style="background:white;color:black;">it = v.begin(); it != v.end(); ++it)
            </span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">(*it &lt; 50)
                sum += *it * 2;
        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">sum;</span></pre>

<span style="background:white;color:black;">A Range based code using language lambdas (transformedF is a variation of <a href="http://smellegantcode.wordpress.com/2011/10/31/linq-to-c-or-something-much-better/">this</a>):</span>

<pre class="code"><span style="background:white;color:black;">        </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">lessThan50 = v | filtered(    [](</span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">i</span><span style="background:white;color:black;">) { </span><span style="background:white;color:blue;">return </span><span style="background:white;color:gray;">i </span><span style="background:white;color:black;">&lt; 50;})
                            | transformedF([] (</span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">i</span><span style="background:white;color:black;">) { </span><span style="background:white;color:blue;">return </span><span style="background:white;color:gray;">i </span><span style="background:white;color:black;">* 2;});
        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">boost::accumulate (lessThan50, 0);</span></pre>

<span style="background:white;color:black;">A Range based code using two functors:</span>

<pre class="code"><span style="background:white;color:black;">        </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">lessThan50 = v | filtered(</span><span style="background:white;color:#2b91af;">Filterer</span><span style="background:white;color:black;">())
                            | transformed(</span><span style="background:white;color:#2b91af;">Doubler</span><span style="background:white;color:black;">());
        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">boost::accumulate (lessThan50, 0);
</span></pre>

<span style="background:white;color:black;">Where:</span>

<pre class="code"><span style="background:white;color:blue;">struct </span><span style="background:white;color:#2b91af;">Doubler </span><span style="background:white;color:black;">{
    </span><span style="background:white;color:blue;">typedef int </span><span style="background:white;color:#2b91af;">result_type</span><span style="background:white;color:black;">;
    </span><span style="background:white;color:blue;">int operator</span><span style="background:white;color:black;">() (</span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">i</span><span style="background:white;color:black;">) </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{ </span><span style="background:white;color:blue;">return </span><span style="background:white;color:gray;">i </span><span style="background:white;color:black;">* 2;}
};
</span><span style="background:white;color:blue;">struct </span><span style="background:white;color:#2b91af;">Filterer </span><span style="background:white;color:black;">{
    </span><span style="background:white;color:blue;">typedef int </span><span style="background:white;color:#2b91af;">result_type</span><span style="background:white;color:black;">;
    </span><span style="background:white;color:blue;">bool operator</span><span style="background:white;color:black;">() (</span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">i</span><span style="background:white;color:black;">) </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{ </span><span style="background:white;color:blue;">return </span><span style="background:white;color:gray;">i </span><span style="background:white;color:black;">&lt; 50;}
};
</span></pre>

<span style="background:white;color:black;">a Range based code using Boost lambdas:</span>

<pre class="code"><span style="background:white;color:black;">        </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">lessThan50 = v | filtered(_1 &lt; 50)
                            | transformed(_1 * 2);
        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">boost::accumulate (lessThan50, 0);</span></pre>

<span style="background:white;color:black;">And finally, some code using the STL for_each function:</span>

<pre class="code"><span style="background:white;color:black;">        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">sum = 0;
        std::for_each( v.cbegin(), v.cend(),
            [&](</span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">i</span><span style="background:white;color:black;">){
                </span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">( </span><span style="background:white;color:gray;">i </span><span style="background:white;color:black;">&lt; 50 ) sum += </span><span style="background:white;color:gray;">i</span><span style="background:white;color:black;">*2;
            });
        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">sum;
</span></pre>

<span style="background:white;color:black;">Notice that I need to run the test an humongous number of times (10000000) on a 100 integers array to start seeing some consistency in results.&#160; <br />And the differences that I see (in nanosecs below) are not huge:</span>

<pre class="code"><span style="background:white;color:black;">1&gt;                         Language lambda: {1775645516;1778411400;0}
1&gt;                          Functor lambda: {1433377701;1435209200;0}
1&gt;                            Boost lambda: {1327829199;1326008500;0}
1&gt;                                For loop: {1338268336;1341608600;0}
1&gt;                             STL foreach: {1338268336;1341608600;0}
</span></pre>

<span style="background:white;color:black;">True to be told, by changing the code a bit these numbers vary and, in some configurations, the Range code takes twice as long.<br /> <br />But given how many repetitions of the test I need to run to notice the difference, I’d say that in most scenarios you should be ok.</span>

<span style="background:white;color:black;">The ‘|>’ operator over collections is the kind of functional composition, broadly defined, that I use the most, but you certainly can use it over other things as well. You’d like to write something like the below:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:#6f008a;">BOOST_CHECK_EQUAL</span><span style="background:white;color:black;">(pipe(</span><span style="background:white;color:maroon;">"bobby"</span><span style="background:white;color:black;">, strlen, boost::lexical_cast&lt;</span><span style="background:white;color:#2b91af;">string</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">int</span><span style="background:white;color:black;">&gt;), </span><span style="background:white;color:maroon;">"5"</span><span style="background:white;color:black;">);</span></pre>

<span style="background:white;color:black;">And you can, once you define the following:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">template</span><span style="background:white;color:black;">&lt; </span><span style="background:white;color:blue;">class </span><span style="background:white;color:#2b91af;">A</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">class </span><span style="background:white;color:#2b91af;">F1</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">class </span><span style="background:white;color:#2b91af;">F2 </span><span style="background:white;color:black;">&gt;
    </span><span style="background:white;color:blue;">inline auto </span><span style="background:white;color:black;">pipe(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">A </span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">a</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">F1 </span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">f1</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">F2 </span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">f2</span><span style="background:white;color:black;">)
        -&gt; </span><span style="background:white;color:blue;">decltype</span><span style="background:white;color:black;">(</span><span style="background:white;color:#6f008a;">REMOVE_REF_BUG</span><span style="background:white;color:black;">(f2(f1(a)))) {
        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:gray;">f2</span><span style="background:white;color:black;">(</span><span style="background:white;color:gray;">f1</span><span style="background:white;color:black;">(</span><span style="background:white;color:gray;">a</span><span style="background:white;color:black;">));
    }</span></pre>

<span style="background:white;color:black;">Where REMOVE_REF_BUG is a workaround for a bug in the decltype implementation under msvc (it should be fixed in VS 11):</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">#ifdef </span><span style="background:white;color:#6f008a;">_MSC_VER
        </span><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">REMOVE_REF_BUG</span><span style="background:white;color:black;">(...) </span><span style="background:white;color:#2b91af;">remove_reference</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:blue;">decltype</span><span style="background:white;color:black;">(__VA_ARGS__)&gt;::</span><span style="background:white;color:#2b91af;">type</span><span style="background:white;color:black;">()
    </span><span style="background:white;color:blue;">#else
        #define </span><span style="background:white;color:black;">REMOVE_REF_BUG(...) __VA_ARGS__
    </span><span style="background:white;color:blue;">#endif</span></pre>

<span style="background:white;color:blue;"><font color="#000000">I didn’t do the work of creating ‘>>’ , ‘<<’ and ‘<|’ F# operators or wrapping the whole lot with better syntax (i.e. operator overloading?), but it certainly can be done.</font></span>

<span style="background:white;color:blue;"><font color="#000000">Now that we have a good syntax for records and a good syntax for operating over collections, the next instalment will put them together and try to answer the question: how should I create collections of records and operate over them?</font></span>
