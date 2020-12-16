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
  - functional programming
---
Recently I got interested in C++ again. The new lambda functions in C++ 11 open up a world of opportunities for C++ programmers. I’ll talk more about how you can write functional code in C++ 11 in upcoming posts. For now let’s look at design by contract.

[Design by contract](http://en.wikipedia.org/wiki/Design_by_contract) is a development style promoted by&#160; [Bertrand Meyer](http://en.wikipedia.org/wiki/Bertrand_Meyer) and it is implemented in his own [Eiffel programming language](http://en.wikipedia.org/wiki/Eiffel_%28programming_language%29). At core, it advocates using preconditions, postconditions and invariants.

An invariant is an assertion that always holds true for a class after the class has been fully constructed and if the code is not executing inside a method. As a user of the class, you always observe the invariant to be true. As an implementer of the class, you can be assured that the invariant is true before a method is entered and you need to make the invariant true again by the time your method exits.

A preconditions is an assertion that needs to hold true at the start of a function, for the postcondition to be true at the end of it. Taken together, invariant, precondition and postcondition define the contract between the implementer and the user of a class.

Code for this post is [here](https://github.com/lucabol/FunctionalCpp/blob/master/dbc.hpp) and [here](https://github.com/lucabol/FunctionalCpp/blob/master/dbc.cpp). Thanks to Andy Sawyer, Steve Bower and Ganesh Sittampalam for reviewing my code and suggesting improvements.

Preconditions are simple and everyone uses them. They are those little _if_ statements that you put at the start of your functions to make sure that the caller has given you the right parameters.

<pre class="code"><span style="background:white;color:blue;">double </span><span style="background:white;color:black;">divide(</span><span style="background:white;color:blue;">double </span><span style="background:white;color:gray;">x</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">double </span><span style="background:white;color:gray;">y</span><span style="background:white;color:black;">) {
    </span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">(</span><span style="background:white;color:gray;">y </span><span style="background:white;color:black;">== 0) </span><span style="background:white;color:blue;">throw new </span><span style="background:white;color:#2b91af;">exception</span><span style="background:white;color:black;">(“y cannot be 0”</span><span style="background:white;color:black;">);<br />    …
</span><span style="background:white;color:black;">}</span></pre>

<span style="background:white;color:black;">These little ‘if’ statements don’t really make the precondition stand out. They can be confused with other, unrelated, ‘if’ statements that do completely different semantic things. A more readable alternative is:</span>

<pre class="code"><span style="background:white;color:blue;">double </span><span style="background:white;color:black;">divide(</span><span style="background:white;color:blue;">double </span><span style="background:white;color:gray;">x</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">double </span><span style="background:white;color:gray;">y</span><span style="background:white;color:black;">) {
</span><span style="background:white;color:black;">    </span><span style="background:white;color:#6f008a;">requires</span><span style="background:white;color:black;">(</span><span style="background:white;color:gray;">y </span><span style="background:white;color:black;">!= 0);
    </span><span style="background:white;color:#6f008a;">…<br /></span><span style="background:white;color:black;">}</span></pre>

<span style="background:white;color:black;">Not an impressive difference, for sure, but kind of nice. The evil macro looks like this:</span>

<pre class="code"><span style="background:white;color:blue;">#ifndef </span><span style="background:white;color:black;">___PRECOND
</span><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">requires</span><span style="background:white;color:black;">(F) {</span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">((!(F))) </span><span style="background:white;color:blue;">throw </span><span style="background:white;color:#2b91af;">preexception</span><span style="background:white;color:black;">(</span><span style="background:white;color:#6f008a;">__FILE__</span><span style="background:white;color:black;">, </span><span style="background:white;color:#6f008a;">__LINE__</span><span style="background:white;color:black;">,</span><span style="background:white;color:maroon;">"Pre-condition failure: " </span><span style="background:white;color:black;">#F);};
</span><span style="background:white;color:blue;">#else
#define </span><span style="background:white;color:black;">requires(F)
</span><span style="background:white;color:blue;">#endif</span></pre>

<span style="background:white;color:blue;"><font color="#000000">Note that the exception maintains information not just about the file and line number of the failure, but also a textual representation of the failed condition. Such things you can do with macro magick.</font></span>

<span style="background:white;color:blue;"><font color="#000000">Postconditions are trickier. In the case of a side-effect free (pure) function, a postcondition asserts something of interest about the return value. In the case of a class, it asserts something of interest about the state of the class before and after the execution of the method.</font></span>

<span style="background:white;color:blue;"><font color="#000000">Let’s start with a pure function. I like to have all my assertion at the start of the function to allow reasoning about it without looking at implementation details. But that poses the problem that the result is available just at the end of the function.&#160; My solution is to enforce this idiom:</font></span>

<pre class="code"><span style="background:white;color:blue;">double </span><span style="background:white;color:black;">divide(</span><span style="background:white;color:blue;">double </span><span style="background:white;color:gray;">x</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">double </span><span style="background:white;color:gray;">y</span><span style="background:white;color:black;">) {
    </span><span style="background:white;color:blue;">double </span><span style="background:white;color:black;">result;
    </span><span style="background:white;color:#6f008a;">requires</span><span style="background:white;color:black;">(</span><span style="background:white;color:gray;">y </span><span style="background:white;color:black;">!= 0);
 </span><span style="background:white;color:black;">   </span><span style="background:white;color:#6f008a;">ensures</span><span style="background:white;color:black;">(result &lt; </span><span style="background:white;color:gray;">x</span><span style="background:white;color:black;">); // Silly, just to falsify it in tests<br />    …
    </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">result;
}</span></pre>

<span style="background:white;color:black;">So you need to declare your result upfront. That is the biggest limitation of the overall solution in my opinion.&#160; If that is acceptable to you, the trick now is how to execute the postcondition test before the method exits. We can do that by storing a lambda and executing it in the destructor:</span>

<pre class="code"><span style="background:white;color:blue;">typedef </span><span style="background:white;color:black;">std::</span><span style="background:white;color:#2b91af;">function</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:blue;">bool </span><span style="background:white;color:black;">()&gt; </span><span style="background:white;color:#2b91af;">___dbcLambda</span><span style="background:white;color:black;">;
</span><span style="background:white;color:blue;">class </span><span style="background:white;color:#2b91af;">___post </span><span style="background:white;color:black;">{
</span><span style="background:white;color:blue;">public</span><span style="background:white;color:black;">:
    ___post(</span><span style="background:white;color:blue;">const char </span><span style="background:white;color:black;">*</span><span style="background:white;color:gray;">file</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">long </span><span style="background:white;color:gray;">line</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">const char </span><span style="background:white;color:black;">*</span><span style="background:white;color:gray;">expr</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">___dbcLambda</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">postF</span><span style="background:white;color:black;">)
        : _f(</span><span style="background:white;color:gray;">postF</span><span style="background:white;color:black;">),
          _file(</span><span style="background:white;color:gray;">file</span><span style="background:white;color:black;">),
          _line(</span><span style="background:white;color:gray;">line</span><span style="background:white;color:black;">),
          _expr(</span><span style="background:white;color:gray;">expr</span><span style="background:white;color:black;">)
    {}
    ~___post()
    {
        </span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">( !std::uncaught_exception() && !_f() )
        {
            </span><span style="background:white;color:blue;">throw </span><span style="background:white;color:#2b91af;">postexception</span><span style="background:white;color:black;">(_file,_line,_expr);
        }
    }
</span><span style="background:white;color:blue;">private</span><span style="background:white;color:black;">:
    </span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">___dbcLambda </span><span style="background:white;color:black;">_f;
    </span><span style="background:white;color:blue;">const char </span><span style="background:white;color:black;">* </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">_file;
    </span><span style="background:white;color:blue;">const long </span><span style="background:white;color:black;">_line;
    </span><span style="background:white;color:blue;">const char </span><span style="background:white;color:black;">* </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">_expr;
};</span></pre>

<span style="background:white;color:black;">You might think that you shouldn’t throw exceptions in a destructor. That is something I never understood about the <a href="http://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization">RAII</a> pattern in C++. If I choose to use exceptions as my error notification method, how am I supposed to get notified if there is a problem releasing a resource in RAII, other than by throwing an exception in the destructor?</span>

<span style="background:white;color:black;">Maybe because of this, the standard has an uncaught_exception() function that allows you to check if an exception has been thrown, so that you don’t throw another one during stack unwinding. If you really don’t like throwing in the destructor, feel free to assert.</span>

<span style="background:white;color:black;">You might be worried about performance, but you really shouldn’t as you can disable all these macros in Release.</span>

<span style="background:white;color:black;">The macro then creates a ___post class on the stack.</span>

<pre class="code"><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">ensures</span><span style="background:white;color:black;">(F) \
    </span><span style="background:white;color:blue;">int </span><span style="background:white;color:#6f008a;">___UNIQUE_LINE </span><span style="background:white;color:black;">= </span><span style="background:white;color:#6f008a;">__LINE__</span><span style="background:white;color:black;">;  \
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:#6f008a;">___UNIQUE_POST </span><span style="background:white;color:black;">= ___post( </span><span style="background:white;color:#6f008a;">__FILE__</span><span style="background:white;color:black;">, </span><span style="background:white;color:#6f008a;">__LINE__</span><span style="background:white;color:black;">, </span><span style="background:white;color:maroon;">"Post-condition failure:" </span><span style="background:white;color:black;">#F, [&](){</span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">(F);});</span></pre>

The UNIQUE stuff is messy business. Part of it is by design and it is used to make sure that each __post variable has a unique name to have multiple ‘ensures’ in a function. The other part is a workaround for [this](http://social.msdn.microsoft.com/Forums/en/vcgeneral/thread/2c4698e1-8159-44fc-a64c-d15220acedb8) msvc bug. Let me know if you want more details. I suspect there is a better way to do it.

Here is the full enchilada …

<pre class="code"><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">___MERGE</span><span style="background:white;color:black;">(a, b) a##b
</span><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">___POST</span><span style="background:white;color:black;">(a) </span><span style="background:white;color:#6f008a;">___MERGE</span><span style="background:white;color:black;">(___postcond,a)
</span><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">___UNIQUE_POST ___POST</span><span style="background:white;color:black;">(</span><span style="background:white;color:#6f008a;">__LINE__</span><span style="background:white;color:black;">)
</span><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">___LINE</span><span style="background:white;color:black;">(a) </span><span style="background:white;color:#6f008a;">___MERGE</span><span style="background:white;color:black;">(___line, a)
</span><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">___UNIQUE_LINE ___LINE</span><span style="background:white;color:black;">(</span><span style="background:white;color:#6f008a;">__LINE__</span><span style="background:white;color:black;">)</span></pre>

<span style="background:white;color:black;">The case in which a postcondition is used inside a method of a class is even trickier because the postcondition must be able to compare the state of the class at the entrance of the method to the state of the class at its exit. Assuming a Counter object with an Add method and assuming ‘___pre’ captures the state of the counter at the start of the method, you’d like to write something like:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">void </span><span style="background:white;color:black;">Add(</span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">x</span><span style="background:white;color:black;">) {
</span><span style="background:white;color:black;">        </span><span style="background:white;color:#6f008a;">ensuresClass</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">this</span><span style="background:white;color:black;">-&gt;c_ == ___pre.c_ + x);<br />        …
</span><span style="background:white;color:black;">    }</span></pre>

<span style="background:white;color:black;">Now, this is tricky. The only way to capture the ‘old’ state in ‘___pre’ is by making a copy of it and store it there. This is what the code below does:</span>

<pre class="code"><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">ensuresClass</span><span style="background:white;color:black;">(F) \
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">___pre(*</span><span style="background:white;color:blue;">this</span><span style="background:white;color:black;">); \
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:#6f008a;">___UNIQUE_POST </span><span style="background:white;color:black;">= </span><span style="background:white;color:#2b91af;">___post</span><span style="background:white;color:black;">( </span><span style="background:white;color:#6f008a;">__FILE__</span><span style="background:white;color:black;">, </span><span style="background:white;color:#6f008a;">__LINE__</span><span style="background:white;color:black;">, </span><span style="background:white;color:maroon;">"Post-condition failure: " </span><span style="background:white;color:black;">#F, [&](){</span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">(F);});</span></pre>

<span style="background:white;color:black;">More troubling is the possibility that the class doesn’t have a copy constructor. In that case you explicitly need to associate a value with ‘___pre2’ by passing it as the first parameter to the appropriate macro as in the code below:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">void </span><span style="background:white;color:black;">Add(</span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">x</span><span style="background:white;color:black;">) {
</span><span style="background:white;color:black;">        </span><span style="background:white;color:#6f008a;">ensuresClass2</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">this</span><span style="background:white;color:black;">-&gt;c_, c_ == ___pre2 + x);
</span><span style="background:white;color:black;">    }</span></pre>

<span style="background:white;color:black;">Which is implemented as follows:</span>

<pre class="code"><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">ensuresClass2</span><span style="background:white;color:black;">(ASS,F) \
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">___pre2(ASS); \
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:#6f008a;">___UNIQUE_POST </span><span style="background:white;color:black;">= </span><span style="background:white;color:#2b91af;">___post</span><span style="background:white;color:black;">( </span><span style="background:white;color:#6f008a;">__FILE__</span><span style="background:white;color:black;">, </span><span style="background:white;color:#6f008a;">__LINE__</span><span style="background:white;color:black;">, </span><span style="background:white;color:maroon;">"Post-condition failure: " </span><span style="background:white;color:black;">#ASS </span><span style="background:white;color:maroon;">" is ___pre2 in " </span><span style="background:white;color:black;">#F, [&](){</span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">(F);});</span></pre>

<span style="background:white;color:black;">And I know about the giant ass …</span>

<span style="background:white;color:black;">Now for invariants. The user should implement an isValid() method on his class as below:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">bool </span><span style="background:white;color:black;">isValid() { </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">c_ &gt;= 0;}</span></pre>

<span style="background:white;color:black;">Then he should add an ‘invariant()’ call at the start of each method, at the end of each constructor and at the start of each destructor:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">void </span><span style="background:white;color:black;">Add(</span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">x</span><span style="background:white;color:black;">) {
        </span><span style="background:white;color:#6f008a;">invariant</span><span style="background:white;color:black;">();
        </span><span style="background:white;color:#6f008a;">requires</span><span style="background:white;color:black;">(x &lt; 10);
</span><span style="background:white;color:black;">        </span><span style="background:white;color:#6f008a;">ensures</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">this</span><span style="background:white;color:black;">-&gt;c_ == ___pre.c_ + x);<br />        …
</span><span style="background:white;color:black;">    }</span></pre>

<span style="background:white;color:black;">This calls the ‘isValid’ function at the start of the method and at the end of it using the same destructor trick:</span>

<pre class="code"><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">invariant</span><span style="background:white;color:black;">() \
    </span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">(!(</span><span style="background:white;color:blue;">this</span><span style="background:white;color:black;">-&gt;isValid())) </span><span style="background:white;color:blue;">throw </span><span style="background:white;color:#2b91af;">preexception</span><span style="background:white;color:black;">(</span><span style="background:white;color:#6f008a;">__FILE__</span><span style="background:white;color:black;">, </span><span style="background:white;color:#6f008a;">__LINE__</span><span style="background:white;color:black;">,</span><span style="background:white;color:maroon;">"Invariant failure"</span><span style="background:white;color:black;">); \
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:#6f008a;">___UNIQUE_INV </span><span style="background:white;color:black;">= </span><span style="background:white;color:#2b91af;">___post</span><span style="background:white;color:black;">( </span><span style="background:white;color:#6f008a;">__FILE__</span><span style="background:white;color:black;">, </span><span style="background:white;color:#6f008a;">__LINE__</span><span style="background:white;color:black;">, </span><span style="background:white;color:maroon;">"Invariant failure"</span><span style="background:white;color:black;">, [&](){</span><span style="background:white;color:blue;">return this</span><span style="background:white;color:black;">-&gt;isValid();});</span></pre>

<span style="background:white;color:black;">All the above machinery is not at all equivalent to having such constructs in the language, but it is simple enough and with a decent enough syntax to be interesting.</span>

<span style="background:white;color:black;">Now a caveat: I have no idea if any of this works. It does work in my examples and its behaviour seems reasonably safe to me, but I haven’t tried it out on any big codebase and haven’t stressed it enough for me to be confident recommending its usage. So, use it at your own risk, let me know how it goes.</span>