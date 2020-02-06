---
id: 87
title: Writing functional code in C++ III – Performance of different allocation schemes
date: 2012-04-16T13:32:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=87
permalink: /2012/04/16/writing-functional-code-in-c-iii-performance-of-different-allocation-schemes/
categories:
  - C
tags:
  - C++
  - Functional Programming
---
Now we know how to represent records and we know how to operate on them using a nice F# like syntax. But how do we store our record in a data structure in the first place?

Code for this post is [here](https://github.com/lucabol/TestPointersCPP). Thanks to Andy Sawyer and Steve Bower for reviewing this.

As it is often the case, C++ gives you many options that are not available in standard functional languages. A mixed blessing of some sort.

  1. You can store them by value or by pointer 
  2. If you store them by pointer, you can use normal pointers or smart pointers 
  3. If you store them by smart pointer, you can use different ones 

Well, storing them by value is the simplest option, but it has two shortcomings:

  1. You pay the price of a full record copy whenever the object need to be copied (i.e. when you add/remove records to/from a vector and whenever the vector needs to resize itself) 
  2. If you store a record in two containers, you get two different copies of it. If you modify one, the other won’t be modified 

The second issue is not a problem in our scenario as records, by definition, are immutable and structurally equivalent (aka equality for them doesn’t mean pointer equality). The first issue is more tricky. Our records get a copy constructor by default which does a ‘memcpy’ of the object. That should be fast. But fast enough?

To answer this question (and more), I embarked in a little performance test that encompasses most ways to store a pod type in an vector like data structure. For all my test I used this struct:

<pre class="code"><span style="background:white;color:blue;">struct </span><span style="background:white;color:#2b91af;">Record </span><span style="background:white;color:black;">{
    </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">Id;
    </span><span style="background:white;color:blue;">char </span><span style="background:white;color:black;">k1[2];
    </span><span style="background:white;color:blue;">char </span><span style="background:white;color:black;">k2[2];
    </span><span style="background:white;color:blue;">char </span><span style="background:white;color:black;">k3[2];
    </span><span style="background:white;color:blue;">char </span><span style="background:white;color:black;">k4[2];
    </span><span style="background:white;color:blue;">char </span><span style="background:white;color:black;">k5[2];
    </span><span style="background:white;color:blue;">char </span><span style="background:white;color:black;">k6[2];
    </span><span style="background:white;color:blue;">char </span><span style="background:white;color:black;">mem[bigBlock];
    </span><span style="background:white;color:blue;">void </span><span style="background:white;color:black;">Lock() {}
    </span><span style="background:white;color:blue;">void </span><span style="background:white;color:black;">Unlock() {}
};</span></pre>

<span style="background:white;color:black;">By recompiling with different values for ‘bigBlock’ I can test what happens when the record size grows. In all tests a record is initialized with this function:</span>

<pre class="code"><span style="background:white;color:blue;">void </span><span style="background:white;color:black;">record_init(</span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">i</span><span style="background:white;color:black;">) {
    </span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">.Id = </span><span style="background:white;color:gray;">i</span><span style="background:white;color:black;">;
    strcpy(</span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">.k1, </span><span style="background:white;color:maroon;">"0"</span><span style="background:white;color:black;">);
    strcpy(</span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">.k2, </span><span style="background:white;color:maroon;">"0"</span><span style="background:white;color:black;">);
    strcpy(</span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">.k3, </span><span style="background:white;color:maroon;">"0"</span><span style="background:white;color:black;">);
    strcpy(</span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">.k4, </span><span style="background:white;color:maroon;">"0"</span><span style="background:white;color:black;">);
    strcpy(</span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">.k5, </span><span style="background:white;color:maroon;">"0"</span><span style="background:white;color:black;">);
    strcpy(</span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">.k6, </span><span style="background:white;color:maroon;">"0"</span><span style="background:white;color:black;">);
    memset(</span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">.mem, </span><span style="background:white;color:maroon;">'-'</span><span style="background:white;color:black;">, bigBlock);
}</span></pre>

<span style="background:white;color:black;">The tests are specific to the scenario I care about: performing functional-like operations on a Range:</span>

<pre class="code"><span style="background:white;color:blue;">struct </span><span style="background:white;color:#2b91af;">to_int </span><span style="background:white;color:black;">{
    </span><span style="background:white;color:blue;">typedef int </span><span style="background:white;color:#2b91af;">result_type</span><span style="background:white;color:black;">;
    </span><span style="background:white;color:blue;">int operator</span><span style="background:white;color:black;">() (</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">) </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{
        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">.Id;
    };
};
</span><span style="background:white;color:#2b91af;">function</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:blue;">bool </span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">&)&gt; filter_f = [](</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">) {</span><span style="background:white;color:blue;">return </span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">.Id &lt; filterNo;};
</span><span style="background:white;color:blue;">template </span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:blue;">class </span><span style="background:white;color:#2b91af;">Range</span><span style="background:white;color:black;">&gt;
</span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">accumulate_filter(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">Range</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">r</span><span style="background:white;color:black;">) {
    </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">boost::accumulate(
        </span><span style="background:white;color:gray;">r </span><span style="background:white;color:black;">| filtered(filter_f) | transformed(</span><span style="background:white;color:#2b91af;">to_int</span><span style="background:white;color:black;">()),
        0,
        </span><span style="background:white;color:#2b91af;">plus</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:blue;">int</span><span style="background:white;color:black;">&gt;());
}</span></pre>

<span style="background:white;color:black;">The usage of a function and&#160; a functor is a bit odd. I don’t recall why I did it that way, but it doesn’t matter as it is the same for each test. What the test does is just filtering a bunch of record, transforming them (map) to ints and sum these ints.</span>

<span style="background:white;color:black;">How many repetitions of each test are used, how big is the record, how many records the Range contains is specified in these constants:</span>

<pre class="code"><span style="background:white;color:blue;">const int </span><span style="background:white;color:black;">repetitions = 1000;
</span><span style="background:white;color:blue;">const int </span><span style="background:white;color:black;">bigBlock = 1000;
</span><span style="background:white;color:blue;">const int </span><span style="background:white;color:black;">howMany = 1000;</span></pre>

<span style="background:white;color:black;">Time is kept using this clock that wraps boost::chrono:</span>

<pre class="code"><span style="background:white;color:blue;">typedef </span><span style="background:white;color:black;">boost::chrono::</span><span style="background:white;color:#2b91af;">process_cpu_clock the_clock</span><span style="background:white;color:black;">;
</span><span style="background:white;color:blue;">struct </span><span style="background:white;color:#2b91af;">timer </span><span style="background:white;color:black;">{
    timer(): clock_(</span><span style="background:white;color:#2b91af;">the_clock</span><span style="background:white;color:black;">::now()) {}
    </span><span style="background:white;color:#2b91af;">the_clock</span><span style="background:white;color:black;">::</span><span style="background:white;color:#2b91af;">times </span><span style="background:white;color:black;">elapsed() {
        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">(</span><span style="background:white;color:#2b91af;">the_clock</span><span style="background:white;color:black;">::now() - clock_).count();
    }
    </span><span style="background:white;color:#2b91af;">the_clock</span><span style="background:white;color:black;">::</span><span style="background:white;color:#2b91af;">time_point </span><span style="background:white;color:black;">clock_;
};</span></pre>

<span style="background:white;color:black;">I have tested the following configurations. Adding records by value:</span>

<pre class="code"><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">normal() {
    </span><span style="background:white;color:#2b91af;">vector</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">&gt; v;
    </span><span style="background:white;color:blue;">for </span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">i = 0; i &lt; howMany; ++i) {
        </span><span style="background:white;color:#2b91af;">Record </span><span style="background:white;color:black;">r;
        record_init(r, i);
        v.push_back(r);
    }
    </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">accumulate_filter(v);
}</span></pre>

<span style="background:white;color:black;">I then tested adding records using a pod_vector. This is a data structure described <a href="http://www.stlsoft.org/doc-1.9/classstlsoft_1_1pod__vector.html">here</a> and in “<a href="http://www.google.co.uk/url?sa=t&rct=j&q=imperfect%20c%2B%2B%20amazon&source=web&cd=1&ved=0CCoQFjAA&url=http%3A%2F%2Fwww.amazon.co.uk%2FImperfect-Practical-Solutions-Real-Life-Programming%2Fdp%2F0321228774&ei=JfN6T8PsFNS3hAesgbk8&usg=AFQjCNH4jd3EOoC933wZ5n2hzTSfObxLdw">Imperfect C++”.</a> It is a vector that uses as an <a href="http://www.stlsoft.org/doc-1.9/classstlsoft_1_1auto__buffer.html">auto_buffer</a> as the underlying storage. An auto_buffer is a class that uses stack memory if it needs more than a certain number of bytes specified at compile time, otherwise it uses heap memory. It works well if you know at compile time that most allocations for something take at most N bytes, but some might need more. This situation is surprisingly frequent. Unfortunately, your objects need to be <a href="http://stackoverflow.com/questions/146452/what-are-pod-types-in-c">POD</a> to use the pod_vector.</span>

<span style="background:white;color:black;">I tested it in the case where the stack space is big enough (podVector<howMany*2>) and when it is not (podVector<howMany/10>).</span>

<pre class="code"><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">podVector() {
    </span><span style="background:white;color:#2b91af;">pod_vector</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">,</span><span style="background:white;color:black;"> size&gt; v;
    </span><span style="background:white;color:blue;">for </span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">i = 0; i &lt; howMany; ++i) {
        </span><span style="background:white;color:#2b91af;">Record </span><span style="background:white;color:black;">r;
        record_init(r, i);
        v.push_back(r);
    }
    </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">accumulate_filter(v);
}</span></pre>

<span style="background:white;color:black;">I then tested just allocating the memory, without freeing it and using <a href="http://www.boost.org/doc/libs/1_49_0/libs/pool/doc/html/index.html">boost::pool</a> in it’s ‘local’ form, which means that memory is freed when it goes out of scope (stack-like). The main drawback of the latter is that you cannot return the container/range.</span>

<pre class="code"><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">boostallocator(</span><span style="background:white;color:#2b91af;">WhichOne </span><span style="background:white;color:gray;">which</span><span style="background:white;color:black;">) {
    boost::</span><span style="background:white;color:#2b91af;">pool</span><span style="background:white;color:black;">&lt;&gt; p(</span><span style="background:white;color:blue;">sizeof</span><span style="background:white;color:black;">(</span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">));
    </span><span style="background:white;color:#2b91af;">vector</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">*&gt; v;
    </span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">* r;
    </span><span style="background:white;color:blue;">for </span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">i = 0; i &lt; howMany; ++i) {
        </span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">(</span><span style="background:white;color:gray;">which </span><span style="background:white;color:black;">== </span><span style="background:white;color:#2f4f4f;">Boost</span><span style="background:white;color:black;">)
            r = (</span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">*)p.malloc(); </span><span style="background:white;color:green;">// memory freed at function exit
        </span><span style="background:white;color:blue;">else
            </span><span style="background:white;color:black;">r = </span><span style="background:white;color:blue;">new </span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">; </span><span style="background:white;color:green;">// oops, memory leak
        </span><span style="background:white;color:black;">record_init(*r, i);
        v.push_back(r);
    }
    </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">accumulate_filter(v | indirected);
}</span></pre>

Indirected is needed because we are not talking about pointers. I also tested various variations of shared pointers. First a normal shared\_ptr, then a shared\_ptr initialized with the boost::singleton\_pool and finally a pointer initialized with make\_shared.

<pre class="code"><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">pointers(</span><span style="background:white;color:#2b91af;">WhichOne </span><span style="background:white;color:gray;">which</span><span style="background:white;color:black;">) {
    </span><span style="background:white;color:#2b91af;">vector</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:#2b91af;">shared_ptr</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">&gt;&gt; v;
    </span><span style="background:white;color:blue;">for </span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">i = 0; i &lt; howMany; ++i) {
        </span><span style="background:white;color:#2b91af;">shared_ptr</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">&gt; r;
        </span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">(</span><span style="background:white;color:gray;">which </span><span style="background:white;color:black;">== </span><span style="background:white;color:#2f4f4f;">Normal</span><span style="background:white;color:black;">)
            r = </span><span style="background:white;color:#2b91af;">shared_ptr</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">&gt;(</span><span style="background:white;color:blue;">new </span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">);
        </span><span style="background:white;color:blue;">else if</span><span style="background:white;color:black;">(</span><span style="background:white;color:gray;">which </span><span style="background:white;color:black;">== </span><span style="background:white;color:#2f4f4f;">Boost</span><span style="background:white;color:black;">)
            r = </span><span style="background:white;color:#2b91af;">shared_ptr</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">&gt;((</span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">*)</span><span style="background:white;color:#2b91af;">record_pool</span><span style="background:white;color:black;">::malloc(), [](</span><span style="background:white;color:blue;">void</span><span style="background:white;color:black;">* </span><span style="background:white;color:gray;">p</span><span style="background:white;color:black;">) {</span><span style="background:white;color:#2b91af;">record_pool</span><span style="background:white;color:black;">::free(</span><span style="background:white;color:gray;">p</span><span style="background:white;color:black;">);});
        </span><span style="background:white;color:blue;">else if</span><span style="background:white;color:black;">(</span><span style="background:white;color:gray;">which </span><span style="background:white;color:black;">== </span><span style="background:white;color:#2f4f4f;">Make</span><span style="background:white;color:black;">)
            r = make_shared&lt;</span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">&gt;();
        </span><span style="background:white;color:blue;">else throw </span><span style="background:white;color:maroon;">"This kind of pointer doesn't exist"</span><span style="background:white;color:black;">;
        record_init(*r, i);
        v.push_back(r);
    }
    </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">accumulate_filter(v | indirected);
}</span></pre>

Finally, I used a [Loki smart pointer](http://www.google.co.uk/url?sa=t&rct=j&q=loki%20c%2B%2B%20smart%20pointer&source=web&cd=3&ved=0CDUQFjAC&url=http%3A%2F%2Floki-lib.sourceforge.net%2Fhtml%2Fa00528.html&ei=-_d6T7awDo2whAeO7qVY&usg=AFQjCNGwub9irghuNNlMzQCmgHLrbkG66Q). This is a very elegantly designed smart pointers from&#160; “[Modern C++ design](http://www.amazon.co.uk/s/ref=nb_sb_noss/278-0149531-8020334?url=search-alias%3Daps&field-keywords=alexandrescu+c%2B%2B+modern)”. You pass as template parameters the policies you want your smart pointer to have (aka how it should behave). I tested it like so:

<pre class="code"><span style="background:white;color:blue;">typedef </span><span style="background:white;color:black;">Loki::</span><span style="background:white;color:#2b91af;">SmartPtr</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">,
                 Loki::</span><span style="background:white;color:#2b91af;">RefCounted</span><span style="background:white;color:black;">,
                 Loki::</span><span style="background:white;color:#2b91af;">DisallowConversion</span><span style="background:white;color:black;">,
                 Loki::</span><span style="background:white;color:#2b91af;">AssertCheck</span><span style="background:white;color:black;">,
                 Loki::</span><span style="background:white;color:#2b91af;">DefaultSPStorage</span><span style="background:white;color:black;">,
                 </span><span style="background:white;color:#6f008a;">LOKI_DEFAULT_CONSTNESS</span><span style="background:white;color:black;">&gt; </span><span style="background:white;color:#2b91af;">RecordPtr</span><span style="background:white;color:black;">;</span></pre>

<span style="background:white;color:black;">And using the following, slightly more convoluted code:</span>

<pre class="code"><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">lokipointers(</span><span style="background:white;color:#2b91af;">WhichOne</span><span style="background:white;color:black;">) {
    </span><span style="background:white;color:#2b91af;">vector</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:#2b91af;">RecordPtr</span><span style="background:white;color:black;">&gt; v;
    </span><span style="background:white;color:blue;">for </span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">i = 0; i &lt; howMany; ++i) {
        </span><span style="background:white;color:#2b91af;">RecordPtr </span><span style="background:white;color:black;">r = </span><span style="background:white;color:#2b91af;">RecordPtr</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">new </span><span style="background:white;color:#2b91af;">Record</span><span style="background:white;color:black;">());
        record_init(*r, i);
        v.push_back(r);
    }
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">ret = accumulate_filter(v | transformed(</span><span style="background:white;color:#2b91af;">RecordPtr</span><span style="background:white;color:black;">::GetPointer) | indirected);
    </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">ret;
}</span></pre>

<span style="background:white;color:black;">The result of my tests are in this table and at <a href="https://github.com/lucabol/TestPointersCPP/blob/master/Results.xlsx">this link</a>. I used VS10 and gcc 4.6.2 on a Windows 7 box. The first number in the (S, N) pair at the top of each column represents&#160; the size of the record, the second one represents the number of objects in the vector. To obtain reasonable numbers, the tests have been run with a different number of iteration for each pair, which means that you can compare the results vertically, but not horizontally.</span>

<span style="background:white;color:black;"><a href="/wp-content/uploads/2012/04/results.jpg"><img style="background-image:none;padding-left:0;padding-right:0;display:inline;padding-top:0;border-width:0;" title="Results" border="0" alt="Results" src="/wp-content/uploads/2012/04/results_thumb.jpg" width="637" height="911" /></a></span>

There are a lot of interesting things in this table. Here are my takeaways. They are obviously specific to this single scenario. You might have different scenarios or different takeaways:

  * Stack allocation is not too bad for small objects, especially for gcc 
  * Pod_vector is a good overall performer (even if you don’t get the size right), it is unfortunate that just works with POD types 
  * GCC seems to be lagging on the shared\_ptr front. Also msvc implementation of the make\_shared optimization gives a visible advantage 
  * There is not much advantage in using the shared pointer with the boost pooled allocator 
  * If you can use the boost local pool allocator, you should. It is faster than stack allocation (in this scenario). Remember that the memory is reclaimed when you exit the function … 

So here you have it. A small detour on the performance of different schemes for allocating pod types. As it is often the case in C++, it depends … 

BTW: Andy Sawyer told me about his rough algorithm to decide which STL container to use. I reproduce it here:

*BEGIN*

A decision tree for selecting a sequence container:

 - I’m in a rush and don’t want to read the rest: use std::deque

 - Do we know ahead of time _exactly_ how many elements will be needed (and will they all fit on our stack!)  - If so, use std::array.

 - Do we need constant-time random access? (Note that we often ***think*** we do, but actually don't  - YAGNI) If so, then we can eliminate std::list/std::forward_list as candidates.

 - Do we need bidirectional iteration? (Again, we need this less often that we think we do). If so, that eliminates std::forward_list

 - Will there be a large number of in-the-middle insertion/removal?&#160; (and assuming we haven’t already eliminated them) then std::list/std::forward_list (especially when the contained type is expensive to move/copy).&#160; In extreme cases, this may be a strong enough requirement to override other constraints (e.g. the need for random access). On the other hand, it may be viable to reduce the cost of move/copy of large contained types by using containers of (smart) pointers.

 - Do we need the contents as a contiguous array? use std::vector (and call reserve&#160; if we can)  - sometimes, anyway; I’ve seen cases where it's faster to build my collection as a std::deque, then transform to std::vector later on.)

 - Use std::deque.

Or, to put it another way, “use std::deque&#160; unless there’s a good reason not to”.&#160; That’s probably an overly-strong statement, but it’s a reasonable starting point.

Naturally, every case will be different  - and no set of &#8216;rules of thumb' is going to work every time (this is one of the things which distinguish rules of thumb from laws of physics). Commonly, we don't know ahead of time which of those criteria is going to have the most significant impact on what we're doing; when I find myself in that situation, I'll use std::deque; once I have a firmer idea of the criteria, I’ll go back and revisit that choice (which – quite often – is as simple as changing a typedef). And of course  - as with all &#8216;optimisations'  - measure, measure and measure again!

*END*

Next time, we’ll go back to more traditional functional programming topics.