---
id: 81
title: Writing functional code in C++ – Records
date: 2012-03-23T08:11:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=81
categories:
  - C
tags:
  - C++
  - functional programming
---
This is the first of a series of posts about writing functional code in C++.&#160; My goal is different from [FC++](http://www.cc.gatech.edu/~yannis/fc++/), which is a full fledged ‘environment’ to write functional code. Instead, I want to experiment with some of the new C++ 11 language features and see if one can build reasonably looking functional code and stay pretty close to the language. The idea is to judiciously use macros and external libraries to build a thin layer on top of the language that doesn’t change the performance characteristics of it (aka it doesn’t slow it down) and integrates fine with existing C++ code.

Think of it as an attempt to answer the question: is there a way to write C++ code in a functional style without loosing its ‘C++sness’? We won’t attempt to be as type safe or syntactically pleasing as Haskell or F# , but we’ll attempt to stay as fast and flexible as C++ and make it functional enough to be interesting.

Thanks to Steve Bower and Ganesh Sittampalam for reviewing and to Andy Sawyer for giving me so much feedback that this post can be considered a co-authorship. Code for this post is [here](https://github.com/lucabol/BlogCppFunctional).

Let’s first talk about the data types that you typically find in a functional language. Let’s start with Records. They are not part of the functional model per se. You can do without them and just use algebraic data types and tuples. But they are damn convenient, and&#160; most functional languages (i.e. Haskell, Clojure, etc…) have them now. We start from them because they map naturally to C++. Records are just like structs, but immutable and having structural equality.

In F# your vanilla record looks like this:

<pre class="code"><span style="background:white;color:blue;">type </span><span style="background:white;color:black;">Person = {
    Name: string
    Id: int
}</span></pre>

<span style="background:white;color:black;">Nice and simple. With C++, you become more verbose. A first attempt would be:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">struct </span><span style="background:white;color:#2b91af;">Person </span><span style="background:white;color:black;">{
        </span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">string </span><span style="background:white;color:black;">Name;
        </span><span style="background:white;color:blue;">const int </span><span style="background:white;color:black;">Salary;
</span><span style="background:white;color:black;">    };</span></pre>

<span style="background:white;color:black;">Which looks nice and easy, but doesn’t quite work because more often than not you need to be able to compare two records for structural equality (which means the value of their fields, not the pointer in memory, defines equality). Records in functional languages automatically support that. But the syntax gets on the ugly side:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">struct </span><span style="background:white;color:#2b91af;">Person </span><span style="background:white;color:black;">{
        </span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">string </span><span style="background:white;color:black;">Name;
        </span><span style="background:white;color:blue;">const int </span><span style="background:white;color:black;">Salary;
        </span><span style="background:white;color:blue;">bool operator</span><span style="background:white;color:black;">==(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">Person</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">) </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{ </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">Salary == </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">.Salary && Name == </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">.Name;}
        </span><span style="background:white;color:blue;">bool operator</span><span style="background:white;color:black;">!=(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">Person</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">) </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{ </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">!(*</span><span style="background:white;color:blue;">this </span><span style="background:white;color:black;">== </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">);}
    };</span></pre>

<span style="background:white;color:black;">We’ll see how to simplify the syntax later. The syntax on the creation side is not too bad:</span>

<span style="background:white;color:#2b91af;">Person </span><span style="background:white;color:black;">p = {</span><span style="background:white;color:maroon;">"Bobby"<font color="#000000">, 2</font></span><span style="background:white;color:black;">};</span>

<span style="background:white;color:black;">Let’s call the above representation, the obvious one. Let’s consider two variations on this scheme. The first one is useful if you want to make your records interoperable with C or with other C++ compilers. </span>

<span style="background:white;color:black;">A full discussion of how to achieve these goals would be very long. It will go about discussing what <a href="http://stackoverflow.com/questions/146452/what-are-pod-types-in-c">POD</a> types are and how their definition <a href="http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2007/n2342.htm">got more precise</a> in C++ 11.</span>

<span style="background:white;color:black;">You can look at my experimentations on pod, standard layout and trivially constructible types <a href="https://github.com/lucabol/FunctionalCpp/blob/master/records.cpp">here</a>. My summary is pretty simple, if you want to achieve all the goals above, you got to use C structs that contain C-compatible types. No const, strings or STL libraries allowed.</span>

<span style="background:white;color:black;">The above class would then become:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">struct </span><span style="background:white;color:#2b91af;">Person </span><span style="background:white;color:black;">{
        </span><span style="background:white;color:blue;">char </span><span style="background:white;color:black;">Name[20];
        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">Salary;
        </span><span style="background:white;color:blue;">bool operator</span><span style="background:white;color:black;">==(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">Person</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">) </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{ </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">Salary == </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">.Salary && !strcmp(Name,</span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">.Name);}
        </span><span style="background:white;color:blue;">bool operator</span><span style="background:white;color:black;">!=(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">Person</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">) </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{ </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">!(*</span><span style="background:white;color:blue;">this </span><span style="background:white;color:black;">== </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">);}
    };</span></pre>

<span style="background:white;color:black;">Obviously, not being able to use strings or STL collections in your record is a big limitation, but in certain cases you might be able to live with it.&#160; Let’s call this representation, the pod one.</span>

<span style="background:white;color:black;">You would think you can make the syntax better by doing something like the below:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">struct </span><span style="background:white;color:#2b91af;">_Person </span><span style="background:white;color:black;">{
        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">id;
        </span><span style="background:white;color:blue;">char </span><span style="background:white;color:black;">name[20];
        </span><span style="background:white;color:#6f008a;">pod_equality</span><span style="background:white;color:black;">(</span><span style="background:white;color:#2b91af;">_Person</span><span style="background:white;color:black;">);
    };    </span></pre>

<span style="background:white;color:black;">Where pod_equality is defined as below:</span>

<pre class="code"><span style="background:white;color:black;">        </span><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">pod_equality</span><span style="background:white;color:black;">(Record)                                                                 \
               </span><span style="background:white;color:blue;">bool operator</span><span style="background:white;color:black;">==(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">Record& other) </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{                                          \
                      </span><span style="background:white;color:blue;">static_assert</span><span style="background:white;color:black;">(std::is_trivial&lt;Record&gt;::value, </span><span style="background:white;color:maroon;">"Not trivially copyable"</span><span style="background:white;color:black;">);       \
                      </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">memcmp(</span><span style="background:white;color:blue;">this</span><span style="background:white;color:black;">, &other, </span><span style="background:white;color:blue;">sizeof</span><span style="background:white;color:black;">(Record)) == 0;}                             \
               </span><span style="background:white;color:blue;">bool operator</span><span style="background:white;color:black;">!=(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">Record& other) </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{ </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">!(*</span><span style="background:white;color:blue;">this </span><span style="background:white;color:black;">== other);}</span></pre>

<span style="background:white;color:black;">But you would be wrong (as I was for a while), as comparing memory values doesn’t work in this case because of the padding that the compiler can insert between fields. Such padding can contain random value (whatever was on the stack, for example) which would make the equality return false for structurally equal objects. Also this scheme fails for floating point types (i.e. NaN and signed zeros).</span>

<span style="background:white;color:black;">An alternative representation for records, which nicely separates constness from the structure of your record is below. It does have some some advantages that we’ll look at, but in its raw form it is yet more syntax:</span>

<pre class="code"><span style="background:white;color:blue;">namespace </span><span style="background:white;color:black;">Mutable {
    </span><span style="background:white;color:blue;">struct </span><span style="background:white;color:#2b91af;">Person </span><span style="background:white;color:black;">{
        </span><span style="background:white;color:#2b91af;">string </span><span style="background:white;color:black;">Name;
        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">Salary;
        </span><span style="background:white;color:blue;">bool operator</span><span style="background:white;color:black;">==(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">Person</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">) </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{ </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">Salary == </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">.Salary && Name == </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">.Name;}
        </span><span style="background:white;color:blue;">bool operator</span><span style="background:white;color:black;">!=(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">Person</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">) </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{ </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">!(*</span><span style="background:white;color:blue;">this </span><span style="background:white;color:black;">== </span><span style="background:white;color:gray;">other</span><span style="background:white;color:black;">);}
    };
}
</span><span style="background:white;color:blue;">typedef const </span><span style="background:white;color:black;">Mutable::</span><span style="background:white;color:#2b91af;">Person Person</span><span style="background:white;color:black;">;
</span></pre>

<span style="background:white;color:black;">Let’s call this representation, the immutable one. </span><span style="background:white;color:black;">Let’s give these guys some usage and talk about their trade-offs. If you want to write a function that increase someone salary, you would write it like this:</span>

<pre class="code"><span style="background:white;color:blue;">template</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:blue;">class </span><span style="background:white;color:#2b91af;">T</span><span style="background:white;color:black;">&gt;
</span><span style="background:white;color:#2b91af;">T </span><span style="background:white;color:black;">rise_salary1(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">T</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">p</span><span style="background:white;color:black;">) {
    </span><span style="background:white;color:#2b91af;">T </span><span style="background:white;color:black;">ret = { </span><span style="background:white;color:gray;">p</span><span style="background:white;color:black;">.Name, </span><span style="background:white;color:gray;">p</span><span style="background:white;color:black;">.Salary + 1000 };
    </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">ret;
}</span></pre>

This looks nice and clean, unless your record has a lot of fields. Let me tell you, in real application it probably does. For example:

<pre class="code"><span style="background:white;color:blue;">namespace </span><span style="background:white;color:black;">Mutable {
    </span><span style="background:white;color:blue;">struct </span><span style="background:white;color:#2b91af;">foo </span><span style="background:white;color:black;">{
        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">value1;
        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">value2;
        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">value3;
        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">value4;
        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">value5;
        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">value7;
        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">value6;
        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">value8;
        </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">value9;
    };
}
</span><span style="background:white;color:blue;">typedef const </span><span style="background:white;color:black;">Mutable::</span><span style="background:white;color:#2b91af;">foo foo</span><span style="background:white;color:black;">;
</span><span style="background:white;color:#2b91af;">foo </span><span style="background:white;color:black;">increment_value7( </span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">foo</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">f </span><span style="background:white;color:black;">)
{
     </span><span style="background:white;color:#2b91af;">foo </span><span style="background:white;color:black;">tmp = { </span><span style="background:white;color:gray;">f</span><span style="background:white;color:black;">.value1, </span><span style="background:white;color:gray;">f</span><span style="background:white;color:black;">.value2, </span><span style="background:white;color:gray;">f</span><span style="background:white;color:black;">.value3, </span><span style="background:white;color:gray;">f</span><span style="background:white;color:black;">.value4, </span><span style="background:white;color:gray;">f</span><span style="background:white;color:black;">.value5, </span><span style="background:white;color:gray;">f</span><span style="background:white;color:black;">.value6, </span><span style="background:white;color:gray;">f</span><span style="background:white;color:black;">.value7+1, </span><span style="background:white;color:gray;">f</span><span style="background:white;color:black;">.value8 };
     </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">tmp;
}</span></pre>

Thanks to Andy for this example. BTW: did you spot the bug at first sight? What about the other one?

So this syntax is problematic. True to be told, part of the problem is in the sub-optimal initialization syntax in C++. If you could use named parameters, it would be more difficult to introduce bugs, but the syntax would still be ugly. You really need something like the F# syntax:

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">r1 = {f = 0.2; k = 3}
</span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">r2 = {r1 </span><span style="background:white;color:blue;">with </span><span style="background:white;color:black;">f = 0.1}
</span></pre>

Can we do something like that? Well, if we are willing to pass the Mutable one around, we can write this:

<pre class="code"><span style="background:white;color:blue;">template</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:blue;">class </span><span style="background:white;color:#2b91af;">T</span><span style="background:white;color:black;">&gt;
</span><span style="background:white;color:#2b91af;">T </span><span style="background:white;color:black;">rise_salary2(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">T</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">p</span><span style="background:white;color:black;">) {
    </span><span style="background:white;color:#2b91af;">T </span><span style="background:white;color:black;">ret(</span><span style="background:white;color:gray;">p</span><span style="background:white;color:black;">);
    ret.Salary += 1000;
    </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">ret;
}</span></pre>

<span style="background:white;color:black;">Or even this:</span>

<pre class="code"><span style="background:white;color:blue;">template</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:blue;">class </span><span style="background:white;color:#2b91af;">T</span><span style="background:white;color:black;">&gt;
</span><span style="background:white;color:#2b91af;">T </span><span style="background:white;color:black;">rise_salary3(</span><span style="background:white;color:#2b91af;">T </span><span style="background:white;color:gray;">p</span><span style="background:white;color:black;">) {
    </span><span style="background:white;color:gray;">p</span><span style="background:white;color:black;">.Salary += 1000;
    </span><span style="background:white;color:blue;">return </span><span style="background:white;color:gray;">p</span><span style="background:white;color:black;">;
}</span></pre>

But that doesn’t make us happy, does it? The whole point of making things const is that you want them to be const.  If you pass around mutable ones, who knows what’s going to happen inside the method?

There is a middle ground that might be acceptable, which is to write functions so that their interface takes immutable records, but inside the function they operate on mutable ones. This is not a bad pattern in general, as having mutable versions of your immutable records might come useful for optimizing certain algorithms. Luckily the casting rules of C++ favour the bold, so the below works:

<pre class="code"><span style="background:white;color:#2b91af;">Person </span><span style="background:white;color:black;">rise_salary_m(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">Person</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">p</span><span style="background:white;color:black;">) {
    Mutable::</span><span style="background:white;color:#2b91af;">Person </span><span style="background:white;color:black;">ret(</span><span style="background:white;color:gray;">p</span><span style="background:white;color:black;">);
    ret.Salary += 1000;
    </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">ret;
}</span></pre>

<span style="background:white;color:black;">And doesn’t look too bad either.</span>

<span style="background:white;color:black;">Now let’s talk syntax. Defining a record is still a lot of typing (and a lot of reading if you are maintaining the code). F# does it like this:</span>

<pre class="code"><span style="background:white;color:blue;">type </span><span style="background:white;color:black;">Person = {
    Name: string
    Id: int
}</span></pre>

<span style="background:white;color:black;">The best I came up with looks like this:</span>

<pre class="code"><span style="background:white;color:#6f008a;">RECORD2</span><span style="background:white;color:black;">(</span><span style="background:white;color:#2b91af;">Person</span><span style="background:white;color:black;">,
          </span><span style="background:white;color:#2b91af;">string</span><span style="background:white;color:black;">, Name,
          </span><span style="background:white;color:blue;">int</span><span style="background:white;color:black;">,    Salary);</span></pre>

<span style="background:white;color:black;">And you need a lot of those macros depending on how many fields your record has. You can write this macro to expand to either the Obvious or Immutable representation trivially. It is a bit more complex for the Pod one because of the interesting C++ array declaration syntax with the number of elements after the name of the field.</span>

<span style="background:white;color:black;">For the Obvious one it looks like this:</span>

<pre class="code"><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">RECORD2</span><span style="background:white;color:black;">(n, t1, f1, t2, f2)                                                            \
    </span><span style="background:white;color:blue;">struct </span><span style="background:white;color:black;">n {                                                                                \
        </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">t1 f1;                                                                          \
        </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">t2 f2;                                                                          \
                                                                                              \
        </span><span style="background:white;color:blue;">bool operator</span><span style="background:white;color:black;">==(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">n& other) </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{ </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">f1 == other.f1 && f2 == other.f2;}     \
        </span><span style="background:white;color:blue;">bool operator</span><span style="background:white;color:black;">!=(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">n& other) </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{ </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">!(*</span><span style="background:white;color:blue;">this </span><span style="background:white;color:black;">== other);}                    \
    };</span></pre>

<span style="background:white;color:black;">All the usual concerns about macros apply. Moreover all your fields need to have a meaningful == operator.</span>

<span style="background:white;color:black;">To summarize, we have found three different representations of records in C++ and tried to alleviate the syntax burden with some macro magick. We’ll go wild in macro-land when we talk about discriminated unions.</span>