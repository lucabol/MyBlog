---
id: 92
title: Writing functional code in C++ IV – Algebraic datatypes
date: 2012-04-27T09:29:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=92
categories:
  - C
tags:
  - C++
  - functional
---
And here comes the guilt bit. I have the strong suspicion (but not certainty) that what I am doing here can be done with templates, but didn’t take the time to do it. With that out of the way, let’s go.

Code for this post is [here](https://github.com/lucabol/FunctionalCpp/blob/master/discriminated_union.cpp). Thanks to Steve Bower and Andy Sawyer for reviewing it.

[Algebraic datatypes](http://www.google.co.uk/url?sa=t&rct=j&q=algebraic%20datatypes&source=web&cd=1&ved=0CDIQFjAA&url=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FAlgebraic_data_type&ei=UmZ9T8fGOoK2hQeRk6i-DA&usg=AFQjCNGG2oS5s9Ir1NvaX-RRcarkvVAoig) (discriminated unions in F#) are a powerful concept in functional programming. They are the main way to represent type variation in your program. Very roughly, where object orientation uses derivation, functional programming uses algebraic datatypes. An entire book could be written on the theory of this, but the goal of this post is to see how we can map them to C++ without loosing C++ness.

When talking about this with C++ programmers, they always point me to boost variant. That doesn’t do it for me for several reasons.

First of all, boost variants represent one of a fixed collection of types. Algebraic datatypes represent one of a fixed collection of <u>named</u> types. That means that a simple thing like the code below cannot be represented as variant:

<pre class="code"><span style="background:white;color:blue;">type </span><span style="background:white;color:black;">LivingEntity =
| Person </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">string  </span><span style="background:white;color:green;">// name
</span><span style="background:white;color:black;">| Dog </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">string     </span><span style="background:white;color:green;">// name</span></pre>

<span style="background:white;color:green;"><font color="#000000">Ok, ok maybe you could represent it by ‘typifing’ things using <a href="http://www.boost.org/doc/libs/1_37_0/boost/strong_typedef.hpp">boost strong typedef</a>, but things get ugly syntactically. Moreover, a lot of time the name is all you care about …</font></span>

<pre class="code"><span style="background:white;color:blue;">type </span><span style="background:white;color:black;">Switch = On | Off</span></pre>

<span style="background:white;color:black;">Are we going to strong typedef for such a simple thing? Oh boy. Even accepting the syntactic weight of all this, there are other issues in play. Discriminated unions are used extensively in functional programs. So you want a nice syntax to work with them Something like the below F# syntax:</span>

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">print living =
    </span><span style="background:white;color:blue;">match </span><span style="background:white;color:black;">living </span><span style="background:white;color:blue;">with
    </span><span style="background:white;color:black;">| Person(name) </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">printfn </span><span style="background:white;color:maroon;">"I'm a per named %s" </span><span style="background:white;color:black;">name
    | Dog(name)    </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">printfn </span><span style="background:white;color:maroon;">"I'm a dog named %s" </span><span style="background:white;color:black;">name</span></pre>

<span style="background:white;color:black;">Which could be made even sweeter by using the ‘function’ keyword as below:</span>

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">print = </span><span style="background:white;color:blue;">function
    </span><span style="background:white;color:black;">| Person(name) </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">printfn </span><span style="background:white;color:maroon;">"I'm a per named %s" </span><span style="background:white;color:black;">name
    | Dog(name)    </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">printfn </span><span style="background:white;color:maroon;">"I'm a dog named %s" </span><span style="background:white;color:black;">name</span></pre>

<span style="background:white;color:black;">In boost variant, you either use the get<type> functions or you write a visitor function. In the first case you are probably going to write a chain of ‘if’ statements or a ‘switch’ statement. Both are confusing and come with plenty of syntactic weight. I don’t really want to write a visitor like the one below for each ‘match’ in my code. The magic is gone.</span>

<pre>class times_two_visitor
    : public <code>&lt;a href="http://www.boost.org/doc/libs/1_49_0/doc/html/boost/static_visitor.html">boost::static_visitor&lt;/a></code>&lt;&gt;
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
};</pre>

Ok, so boost variant doesn’t really work for this. Remember that our overarching goal was to stay close to C++. The language itself has something that comes pretty close to what we want in the form of a union, or better a [tagged union](http://en.wikipedia.org/wiki/Tagged_union). Again, the types are not named, but maybe we can work that in.

It turns out that Jared [here](http://blogs.msdn.com/b/jaredpar/archive/2010/11/18/discriminated-unions-in-c.aspx) did all the hard work. The general idea is to use macros to hide the construction of a tagged union with methods to test the type and return the contained value. 

For example this code:

<pre class="code"><span style="background:white;color:#6f008a;">DU_DECLARE</span><span style="background:white;color:black;">(</span><span style="background:white;color:#2b91af;">LivingEntity</span><span style="background:white;color:black;">)
    </span><span style="background:white;color:#6f008a;">DU_VALUE</span><span style="background:white;color:black;">(Person,    </span><span style="background:white;color:#2b91af;">string</span><span style="background:white;color:black;">)
    </span><span style="background:white;color:#6f008a;">DU_VALUE</span><span style="background:white;color:black;">(Dog,       </span><span style="background:white;color:#2b91af;">string</span><span style="background:white;color:black;">)
</span><span style="background:white;color:#6f008a;">DU_END
</span></pre>

<span style="background:white;color:#6f008a;"><font color="#000000">Becomes something like:</font></span>

<pre class="code"><span style="background:white;color:blue;">struct </span><span style="background:white;color:#2b91af;">LivingEntity </span><span style="background:white;color:black;">{
    </span><span style="background:white;color:blue;">private</span><span style="background:white;color:black;">:
        LivingEntity() {}
        </span><span style="background:white;color:blue;">unsigned int </span><span style="background:white;color:black;">m_kind;
    </span><span style="background:white;color:blue;">public</span><span style="background:white;color:black;">:
        </span><span style="background:white;color:blue;">static </span><span style="background:white;color:#2b91af;">LivingEntity </span><span style="background:white;color:black;">Person(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">string</span><span style="background:white;color:black;">& </span><span style="background:white;color:gray;">value</span><span style="background:white;color:black;">) {
            </span><span style="background:white;color:#2b91af;">LivingEntity </span><span style="background:white;color:black;">unionValue;
            unionValue.m_kind = 19;
            unionValue.m_Person = </span><span style="background:white;color:gray;">value</span><span style="background:white;color:black;">;
            </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">unionValue; }
        </span><span style="background:white;color:blue;">bool </span><span style="background:white;color:black;">IsPerson() </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{
            </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">m_kind == 19;
        }
        </span><span style="background:white;color:blue;">const </span><span style="background:white;color:#2b91af;">string</span><span style="background:white;color:black;">& GetPerson() </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{
            (</span><span style="background:white;color:blue;">void</span><span style="background:white;color:black;">)( (!!(m_kind == 19)) || (_wassert(L</span><span style="background:white;color:maroon;">"m_kind == __LINE__"</span><span style="background:white;color:black;">, L</span><span style="background:white;color:maroon;">"c:discriminated_union.cpp"</span><span style="background:white;color:black;">, 19), 0) );
            </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">m_Person; }
        </span><span style="background:white;color:#2b91af;">string </span><span style="background:white;color:black;">GetPerson() {
            (</span><span style="background:white;color:blue;">void</span><span style="background:white;color:black;">)( (!!(m_kind == 19)) || (_wassert(L</span><span style="background:white;color:maroon;">"m_kind == __LINE__"</span><span style="background:white;color:black;">, L</span><span style="background:white;color:maroon;">"c:discriminated_union.cpp"</span><span style="background:white;color:black;">, 19), 0) );
            </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">m_Person; }
   </span><span style="background:white;color:blue;">private</span><span style="background:white;color:black;">:<br /></span><span style="background:white;color:#2b91af;">        string </span><span style="background:white;color:black;">m_Person;<br /><br />   …</span></pre>

<span style="background:white;color:black;">You can see the outline of a tagged union (i.e. m_kind) with a constructor for each type (i.e. Person) and methods to test for at type and return its value. You can also see the storage for the value (i.e. m_Person).</span>

<span style="background:white;color:black;">The only thing in DU_DECLARE that is different from Jared’s solution is the typedef below that allows not repeating the LivingEntity name in each DU_VALUE.</span>

<pre class="code"><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">DU_DECLARE</span><span style="background:white;color:black;">(name)                        \
    </span><span style="background:white;color:blue;">struct </span><span style="background:white;color:black;">name {                               \
    </span><span style="background:white;color:blue;">private</span><span style="background:white;color:black;">:                                    \
        </span><span style="background:white;color:blue;">typedef </span><span style="background:white;color:black;">name unionName;                 \
        name() {}                               \
        </span><span style="background:white;color:blue;">unsigned int </span><span style="background:white;color:black;">m_kind;                    \
    </span><span style="background:white;color:blue;">public</span><span style="background:white;color:black;">:
</span></pre>

<pre class="code"><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">DU_VALUE</span><span style="background:white;color:black;">(entryName, entryType)                                                                      \
        </span><span style="background:white;color:blue;">static </span><span style="background:white;color:black;">unionName entryName(</span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">entryType& value) {                                                \
            unionName unionValue;                                                                           \
            unionValue.m_kind = </span><span style="background:white;color:#6f008a;">__LINE__</span><span style="background:white;color:black;">;                                                                   \
            unionValue.m_##entryName = value;                                                               \
            </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">unionValue;  }                                                                           \
        </span><span style="background:white;color:blue;">bool </span><span style="background:white;color:black;">Is##entryName() </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{ </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">m_kind == </span><span style="background:white;color:#6f008a;">__LINE__</span><span style="background:white;color:black;">;}                                            \
        </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">entryType& Get##entryName() </span><span style="background:white;color:blue;">const </span><span style="background:white;color:black;">{ </span><span style="background:white;color:#6f008a;">assert</span><span style="background:white;color:black;">(m_kind == </span><span style="background:white;color:#6f008a;">__LINE__</span><span style="background:white;color:black;">); </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">m_##entryName; }       \
        entryType Get##entryName() { </span><span style="background:white;color:#6f008a;">assert</span><span style="background:white;color:black;">(m_kind == </span><span style="background:white;color:#6f008a;">__LINE__</span><span style="background:white;color:black;">); </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">m_##entryName; }                    \
    </span><span style="background:white;color:blue;">private</span><span style="background:white;color:black;">:                                                                                                \
        entryType m_##entryName;                                                                            \
    </span><span style="background:white;color:blue;">public</span><span style="background:white;color:black;">:
</span></pre>

<span style="background:white;color:black;">With all of that at your disposal it becomes easy to write:</span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">entity = </span><span style="background:white;color:#2b91af;">LivingEntity</span><span style="background:white;color:black;">::Dog(</span><span style="background:white;color:maroon;">"Bob"</span><span style="background:white;color:black;">);
    </span><span style="background:white;color:#6f008a;">DU_MATCH</span><span style="background:white;color:black;">(entity)
        </span><span style="background:white;color:#6f008a;">DU_CASE</span><span style="background:white;color:black;">(Dog,   </span><span style="background:white;color:#6f008a;">BOOST_CHECK_EQUAL</span><span style="background:white;color:black;">(value, </span><span style="background:white;color:maroon;">"Bob"</span><span style="background:white;color:black;">);)
        </span><span style="background:white;color:#6f008a;">DU_CASE</span><span style="background:white;color:black;">(Person,</span><span style="background:white;color:#6f008a;">BOOST_CHECK</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">false</span><span style="background:white;color:black;">);)
    </span><span style="background:white;color:#6f008a;">DU_MATCH_END
</span></pre>

<span style="background:white;color:#6f008a;"><font color="#000000">There are some beautiful things about this. First of all, the construction of any of such types is super simple. You even get intellisense!<br /> <br /></font></span><span style="background:white;color:#6f008a;"><font color="#000000">Moreover the ‘value’ variable contains whatever was passed in the constructor for the object. So this is semantically equivalent, if not syntactically, to the match statement in F#.</font></span>

<span style="background:white;color:#6f008a;"><font color="#000000">Obviously the code part is not limited to a single instruction:</font></span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:#6f008a;">DU_MATCH</span><span style="background:white;color:black;">(entity)
        </span><span style="background:white;color:#6f008a;">DU_CASE</span><span style="background:white;color:black;">(Dog,
            cout &lt;&lt; </span><span style="background:white;color:maroon;">"I should be here"</span><span style="background:white;color:black;">;
            </span><span style="background:white;color:#6f008a;">BOOST_CHECK_EQUAL</span><span style="background:white;color:black;">(value, </span><span style="background:white;color:maroon;">"Bob"</span><span style="background:white;color:black;">);
        )
        </span><span style="background:white;color:#6f008a;">DU_CASE</span><span style="background:white;color:black;">(Person,
            </span><span style="background:white;color:#6f008a;">BOOST_CHECK</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">false</span><span style="background:white;color:black;">);
        )
    </span><span style="background:white;color:#6f008a;">DU_MATCH_END</span></pre>

<span style="background:white;color:#6f008a;"><font color="#000000">And for those of you addicted to braces, I venture:</font></span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:#6f008a;">DU_MATCH</span><span style="background:white;color:black;">(entity)
        </span><span style="background:white;color:#6f008a;">DU_CASE</span><span style="background:white;color:black;">(Dog,
        {
            cout &lt;&lt; </span><span style="background:white;color:maroon;">"I should be here"</span><span style="background:white;color:black;">;
            </span><span style="background:white;color:#6f008a;">BOOST_CHECK_EQUAL</span><span style="background:white;color:black;">(value, </span><span style="background:white;color:maroon;">"Bob"</span><span style="background:white;color:black;">);
        })
        </span><span style="background:white;color:#6f008a;">DU_CASE</span><span style="background:white;color:black;">(Person,
        {
            </span><span style="background:white;color:#6f008a;">BOOST_CHECK</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">false</span><span style="background:white;color:black;">);
        })
    </span><span style="background:white;color:#6f008a;">DU_MATCH_END</span></pre>

<span style="background:white;color:#6f008a;"><font color="#000000">They all work with the same macro definition. They expand to something along the line of:</font></span>

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">false</span><span style="background:white;color:black;">) {}
        </span><span style="background:white;color:blue;">else if</span><span style="background:white;color:black;">(entity.IsDog()) {
            </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">value = entity.GetDog();
            </span><span style="background:white;color:#6f008a;">BOOST_CHECK_EQUAL</span><span style="background:white;color:black;">(value, </span><span style="background:white;color:maroon;">"Bob"</span><span style="background:white;color:black;">);
        }
        </span><span style="background:white;color:blue;">else if</span><span style="background:white;color:black;">(entity.IsPerson()) {
            </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">value = entity.GetPerson();
            </span><span style="background:white;color:#6f008a;">BOOST_CHECK</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">false</span><span style="background:white;color:black;">);
        }
        </span><span style="background:white;color:blue;">else </span><span style="background:white;color:black;">{
            </span><span style="background:white;color:blue;">throw </span><span style="background:white;color:#2b91af;">match_exception</span><span style="background:white;color:black;">();
        }</span></pre>

<span style="background:white;color:black;">I’ve not reached the pinnacle of macro naming mastering with this one. Making them lowercase and risking a bit more on the conflict side would make the syntax much more palatable. I call it, as it is, not too bad.</span>

<span style="background:white;color:black;">The last ‘else’ clause assures you then if you add a new type to the discriminated union and forget to update one of the ‘MATCH’ clauses at least you get a run time error. That is not good. Functional languages would give you a compile time error, which is much better. Maybe with judicious use of templates you can bring the error at compile time.</span>

<span style="background:white;color:black;">The macros are trivial:</span>

<pre class="code"><span style="background:white;color:blue;">class </span><span style="background:white;color:#2b91af;">match_exception</span><span style="background:white;color:black;">: std::</span><span style="background:white;color:#2b91af;">exception </span><span style="background:white;color:black;">{};
</span><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">DU_MATCH</span><span style="background:white;color:black;">(unionName) { </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">du_match_var = unionName; </span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">false</span><span style="background:white;color:black;">) {}
</span><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">DU_CASE_TAG</span><span style="background:white;color:black;">(entry, ...)                        \
    </span><span style="background:white;color:blue;">else if</span><span style="background:white;color:black;">(du_match_var.Is##entry()) {                \
        __VA_ARGS__                                    \
    }
</span><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">DU_CASE</span><span style="background:white;color:black;">(entry, ...)                            \
    </span><span style="background:white;color:blue;">else if</span><span style="background:white;color:black;">(du_match_var.Is##entry()) {                \
        </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">value = du_match_var.Get##entry();        \
        __VA_ARGS__                                    \
    }
</span><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">DU_DEFAULT</span><span style="background:white;color:black;">(...)                                \
    </span><span style="background:white;color:blue;">else if</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">true</span><span style="background:white;color:black;">) { __VA_ARGS__}
</span><span style="background:white;color:blue;">#define </span><span style="background:white;color:#6f008a;">DU_MATCH_END </span><span style="background:white;color:blue;">else </span><span style="background:white;color:black;">{</span><span style="background:white;color:blue;">throw new </span><span style="background:white;color:#2b91af;">match_exception</span><span style="background:white;color:black;">();} }
</span></pre>

<span style="background:white;color:black;">Let’s now go back to our initial goal and see how far off we are. We were trying to do the following:</span>

<pre class="code"><span style="background:white;color:blue;">type </span><span style="background:white;color:black;">LivingEntity =
| Person </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">string
| Dog </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">string
</span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">print = </span><span style="background:white;color:blue;">function
    </span><span style="background:white;color:black;">| Person(name) </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">printfn </span><span style="background:white;color:maroon;">"I'm a per named %s" </span><span style="background:white;color:black;">name
    | Dog(name)    </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">printfn </span><span style="background:white;color:maroon;">"I'm a dog named %s" </span><span style="background:white;color:black;">name</span></pre>

<span style="background:white;color:black;">And here is what we ended up with:</span>

<pre class="code"><span style="background:white;color:#6f008a;">DU_DECLARE</span><span style="background:white;color:black;">(</span><span style="background:white;color:#2b91af;">LivingEntity</span><span style="background:white;color:black;">)
    </span><span style="background:white;color:#6f008a;">DU_VALUE</span><span style="background:white;color:black;">(</span><span style="background:white;color:black;">Person,    </span><span style="background:white;color:#2b91af;">string</span><span style="background:white;color:black;">)
    </span><span style="background:white;color:#6f008a;">DU_VALUE</span><span style="background:white;color:black;">(</span><span style="background:white;color:black;">Dog,        </span><span style="background:white;color:#2b91af;">string</span><span style="background:white;color:black;">)
</span><span style="background:white;color:#6f008a;">DU_END
</span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">print(</span><span style="background:white;color:#2b91af;">LivingEntity </span><span style="background:white;color:gray;">en</span><span style="background:white;color:black;">) -&gt; </span><span style="background:white;color:blue;">void </span><span style="background:white;color:black;">{
    </span><span style="background:white;color:#6f008a;">DU_MATCH</span><span style="background:white;color:black;">(entity)
        </span><span style="background:white;color:#6f008a;">DU_CASE</span><span style="background:white;color:black;">(Dog,    cout &lt;&lt; </span><span style="background:white;color:maroon;">"I'm a dog named " </span><span style="background:white;color:black;">&lt;&lt; value;)
        </span><span style="background:white;color:#6f008a;">DU_CASE</span><span style="background:white;color:black;">(Person, cout &lt;&lt; </span><span style="background:white;color:maroon;">"I'm a per named " </span><span style="background:white;color:black;">&lt;&lt; value;)
    </span><span style="background:white;color:#6f008a;">DU_MATCH_END
</span><span style="background:white;color:black;">}</span></pre>

<span style="background:white;color:black;">In our Switch case:</span>

<span style="background:white;color:blue;">type </span><span style="background:white;color:black;">Switch = On | Off</span>

<span style="background:white;color:black;">You get the good looking :</span>

<span style="background:white;color:black;"></p> 

<pre class="code"><span style="background:white;color:#6f008a;">DU_DECLARE</span><span style="background:white;color:black;">(</span><span style="background:white;color:#2b91af;">Switch</span><span style="background:white;color:black;">)
    </span><span style="background:white;color:#6f008a;">DU_FLAG</span><span style="background:white;color:black;">(</span><span style="background:white;color:black;">On)
    </span><span style="background:white;color:#6f008a;">DU_FLAG</span><span style="background:white;color:black;">(</span><span style="background:white;color:black;">Off)
</span><span style="background:white;color:#6f008a;">DU_END
</span></pre>

<p>
  And along the way we lost compile time type safety in the very common case of adding new types to the discriminated union. That’s bad.
</p>

<p>
  Also some of you would strongly dislike the (ab)use of macros. As for me, it looks workable.
</p>

<p>
  </span>
</p>
