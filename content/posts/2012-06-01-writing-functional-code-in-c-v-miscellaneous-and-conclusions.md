---
id: 96
title: Writing functional code in C++ V – Miscellaneous and conclusions
date: 2012-06-01T06:45:26+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=96
permalink: /2012/06/01/writing-functional-code-in-c-v-miscellaneous-and-conclusions/
categories:
  - C
tags:
  - C++
  - Functional Programming
---
Just a couple of trivialities and my parting thoughts.

# Nested functions

If your language has lambdas, you don’t need nested functions support because you can implement them using it.

I am a heavy user of nested functions, but I’m of two minds about it. On one side, I like that they sit close to where they are used, avoiding going outside the main function body to understand them. I also like that you don’t need to pass a lot of parameters to them, as they capture the function locals. On the other side, they end up creating the impression that your functions are very long and so, in my eyes, they occasionally reduce readability. The IDE helps you out there (at least VS 11) by allowing you to collapse the lambdas.

An example of trivial case is below:

<pre class="code"><span style="background:white;color:#6f008a;">BOOST_AUTO_TEST_CASE</span><span style="background:white;color:black;">(</span><span style="background:white;color:#2b91af;">NestedFunctions</span><span style="background:white;color:black;">)
{
    </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">x = 3;
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">sumX = [&] (</span><span style="background:white;color:blue;">int </span><span style="background:white;color:gray;">y</span><span style="background:white;color:black;">) { </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">x + </span><span style="background:white;color:gray;">y</span><span style="background:white;color:black;">;};
    </span><span style="background:white;color:#6f008a;">BOOST_CHECK_EQUAL</span><span style="background:white;color:black;">(sumX(2), 3+2);
}</span></pre>

<span style="background:white;color:black;">And here is a more realistic one (not written in a functional style), where readability is reduced by the three nested functions (among many other things):</span>

<pre class="code"><span style="background:white;color:blue;">bool </span><span style="background:white;color:black;">condor(
            boost::gregorian::date now,  </span><span style="background:white;color:green;">// date to evaluate
            </span><span style="background:white;color:blue;">double </span><span style="background:white;color:black;">spot,                 </span><span style="background:white;color:green;">// spot price underlying
            </span><span style="background:white;color:blue;">double </span><span style="background:white;color:black;">v,                    </span><span style="background:white;color:green;">// ATM volatility
            </span><span style="background:white;color:blue;">double </span><span style="background:white;color:black;">r,                    </span><span style="background:white;color:green;">// risk free rate
            </span><span style="background:white;color:blue;">double </span><span style="background:white;color:black;">step,                 </span><span style="background:white;color:green;">// % of spot price to keep as distance between wings
            </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">minCallShortDist,        </span><span style="background:white;color:green;">// min distance from the short call strike in steps
            </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">minPutShortDist,         </span><span style="background:white;color:green;">// min distance from the short put strike in steps
            </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">minDays,                 </span><span style="background:white;color:green;">// min number of days to expiry
            </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">maxDays,                 </span><span style="background:white;color:green;">// max number of days to expiry
            </span><span style="background:white;color:blue;">double </span><span style="background:white;color:black;">maxDelta,             </span><span style="background:white;color:green;">// max acceptable delta value for shorts in steps
            </span><span style="background:white;color:blue;">double </span><span style="background:white;color:black;">minPremium,           </span><span style="background:white;color:green;">// min accepted premium as % of step
            </span><span style="background:white;color:black;">Condor& ret                  </span><span style="background:white;color:green;">// return value
            </span><span style="background:white;color:black;">)
{
    </span><span style="background:white;color:green;">// convert params to dollar signs
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">stepPr            = round(step * spot);
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">toUSD             = [stepPr] (</span><span style="background:white;color:blue;">double </span><span style="background:white;color:black;">x) { </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">round(stepPr * x);};
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">minCpr            = toUSD( minCallShortDist );
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">minPpr            = toUSD( minPutShortDist );
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">premiumPr         = toUSD( minPremium );
    </span><span style="background:white;color:green;">// calc strike values for short legs
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">atm               = round(spot / stepPr) * (</span><span style="background:white;color:blue;">long</span><span style="background:white;color:black;">) stepPr;
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">callShort         = atm + minCpr;
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">putShort          = atm - minPpr;
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">addDays           = [](boost::gregorian::date d, </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">dys) -&gt; boost::gregorian::date {
        </span><span style="background:white;color:blue;">using namespace </span><span style="background:white;color:black;">boost::gregorian;
        </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">toAdd         = days(dys);
        </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">dTarget       = d + toAdd;
        </span><span style="background:white;color:blue;">return  </span><span style="background:white;color:black;">dTarget;
    };
    </span><span style="background:white;color:green;">// calc min & max allowed expiry dates
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">minDate           = addDays(now, minDays);
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">maxDate           = addDays(now, maxDays);
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">expiry            = calcExpiry(now, 0);
    </span><span style="background:white;color:green;">// find first good expiry
    </span><span style="background:white;color:blue;">while</span><span style="background:white;color:black;">(expiry &lt; minDate)
        expiry          = calcExpiry(expiry, +1);
    Greeks g;
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">scholes           = [=, &g] (</span><span style="background:white;color:blue;">double </span><span style="background:white;color:black;">strike, </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">days, </span><span style="background:white;color:blue;">bool </span><span style="background:white;color:black;">CorP) {
        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">blackScholesEuro(spot, strike, days, CorP, v, r, g, </span><span style="background:white;color:blue;">true</span><span style="background:white;color:black;">);
    };
    </span><span style="background:white;color:green;">// find a condor that works at this expiry
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">findCondor        = [=, &g, &ret] (</span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">days) -&gt; </span><span style="background:white;color:blue;">bool </span><span style="background:white;color:black;">{
        ret.shortCallStrike                = callShort;
        ret.shortPutStrike                 = putShort;
        </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">shCallPremium                 = 0.0;
        </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">shPutPremium                  = 0.0;
        </span><span style="background:white;color:green;">// find short call strike price &lt; maxDelta
        </span><span style="background:white;color:blue;">while</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">true</span><span style="background:white;color:black;">) {
            shCallPremium                  = scholes(ret.shortCallStrike, days, </span><span style="background:white;color:blue;">true</span><span style="background:white;color:black;">);
            </span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">(g.delta &lt;= maxDelta)
                </span><span style="background:white;color:blue;">break</span><span style="background:white;color:black;">;
            </span><span style="background:white;color:blue;">else
                </span><span style="background:white;color:black;">ret.shortCallStrike        += stepPr;
        }
        </span><span style="background:white;color:green;">// find short put strike price &lt; maxDelta
        </span><span style="background:white;color:blue;">while</span><span style="background:white;color:black;">(</span><span style="background:white;color:blue;">true</span><span style="background:white;color:black;">) {
            shPutPremium                   = scholes(ret.shortPutStrike, days, </span><span style="background:white;color:blue;">false</span><span style="background:white;color:black;">);
            </span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">( (- g.delta) &lt;= maxDelta)
                </span><span style="background:white;color:blue;">break</span><span style="background:white;color:black;">;
            </span><span style="background:white;color:blue;">else
                </span><span style="background:white;color:black;">ret.shortPutStrike         -= stepPr;
        }
        </span><span style="background:white;color:green;">// check premium is adeguate
        </span><span style="background:white;color:black;">ret.longCallStrike                = ret.shortCallStrike + stepPr;
        ret.longPutStrike                 = ret.shortPutStrike  - stepPr;
        </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">lgCall                       = scholes(ret.longCallStrike, days, </span><span style="background:white;color:blue;">true</span><span style="background:white;color:black;">);
        </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">lgPut                        = scholes(ret.longPutStrike,  days, </span><span style="background:white;color:blue;">false</span><span style="background:white;color:black;">);
        ret.netPremium                    = shCallPremium + shPutPremium - lgCall - lgPut;
        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">ret.netPremium &gt; premiumPr;
    };
    </span><span style="background:white;color:green;">// increases the expiry until it finds a condor or the expiry is too far out
    </span><span style="background:white;color:blue;">while </span><span style="background:white;color:black;">(expiry &lt; maxDate) {
        </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">days        = (expiry - now).days();
        </span><span style="background:white;color:blue;">if</span><span style="background:white;color:black;">(findCondor(days)) {
            ret.year     = expiry.year();
            ret.month    = expiry.month();
            ret.day      = expiry.day();
            </span><span style="background:white;color:blue;">return true</span><span style="background:white;color:black;">;
        }
        expiry           = calcExpiry(expiry, +1);
    }
    </span><span style="background:white;color:blue;">return false</span><span style="background:white;color:black;">;
}</span></pre>

<span style="background:white;color:black;"></span>

That is quite a mouthful, isn’t it? But really the function is not that long. It is all these nested functions that makes it seems so.

# Tuples

Tuples are another feature toward which I have mixed feelings. They are really useful to return multiple results from a function and for rapid prototyping of concepts. But they are easy to abuse. Creating Records is almost always a better, safer way to craft your code, albeit more verbose.

The standard C++ has an excellent tuple library that makes working with them almost as easy as in mainstream functional languages. The below function shows creating them, getting their value, passing them to functions and deconstructing them:

<pre class="code"><span style="background:white;color:#6f008a;">BOOST_AUTO_TEST_CASE</span><span style="background:white;color:black;">(</span><span style="background:white;color:#2b91af;">Tuples</span><span style="background:white;color:black;">)
{
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">t = make_tuple(</span><span style="background:white;color:maroon;">"bob"</span><span style="background:white;color:black;">, </span><span style="background:white;color:maroon;">"john"</span><span style="background:white;color:black;">, 3, 2.3);
    </span><span style="background:white;color:#6f008a;">BOOST_CHECK_EQUAL</span><span style="background:white;color:black;">(get&lt;0&gt;(t), </span><span style="background:white;color:maroon;">"bob"</span><span style="background:white;color:black;">);
    </span><span style="background:white;color:#6f008a;">BOOST_CHECK_EQUAL</span><span style="background:white;color:black;">(get&lt;2&gt;(t), 3);
    </span><span style="background:white;color:green;">// yep, compiler error
    //auto k = get&lt;10&gt;(t);
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">t2(t);
    </span><span style="background:white;color:#6f008a;">BOOST_CHECK</span><span style="background:white;color:black;">(t2 == t);
    </span><span style="background:white;color:green;">// passing as argument, returning it
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">f = [] (</span><span style="background:white;color:#2b91af;">tuple</span><span style="background:white;color:black;">&lt;</span><span style="background:white;color:#2b91af;">string</span><span style="background:white;color:black;">, </span><span style="background:white;color:#2b91af;">string</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">int</span><span style="background:white;color:black;">, </span><span style="background:white;color:blue;">double</span><span style="background:white;color:black;">&gt; </span><span style="background:white;color:gray;">t</span><span style="background:white;color:black;">) { </span><span style="background:white;color:blue;">return </span><span style="background:white;color:gray;">t</span><span style="background:white;color:black;">;};
    </span><span style="background:white;color:blue;">auto </span><span style="background:white;color:black;">t1 = f(t);
    </span><span style="background:white;color:#6f008a;">BOOST_CHECK</span><span style="background:white;color:black;">(t == t1);
    </span><span style="background:white;color:green;">// automatic deconstruction
    </span><span style="background:white;color:#2b91af;">string </span><span style="background:white;color:black;">s1; </span><span style="background:white;color:#2b91af;">string </span><span style="background:white;color:black;">s2; </span><span style="background:white;color:blue;">int </span><span style="background:white;color:black;">i; </span><span style="background:white;color:blue;">double </span><span style="background:white;color:black;">d;
    std::tie(s1, s2, i, d) = f(t);
    </span><span style="background:white;color:#6f008a;">BOOST_CHECK_EQUAL</span><span style="background:white;color:black;">(s1, </span><span style="background:white;color:maroon;">"bob"</span><span style="background:white;color:black;">);
    </span><span style="background:white;color:green;">// partial reconstruction
    </span><span style="background:white;color:#2b91af;">string </span><span style="background:white;color:black;">s11;
    std::tie(s11, ignore, ignore, ignore) = f(t);
    </span><span style="background:white;color:#6f008a;">BOOST_CHECK_EQUAL</span><span style="background:white;color:black;">(s11, </span><span style="background:white;color:maroon;">"bob"</span><span style="background:white;color:black;">);
}</span></pre>

# Conclusion

I’m sure there are some fundamental functional features that I haven’t touched on (i.e. currying, more powerful function composition, etc…).&#160; Despite that, I think we have enough material here to start drawing some conclusions. To start with, where is C++ deficient compared to mainstream functional languages _<u>for the sake of writing functional code</u>_ ?

  * <u>Compiler errors</u>: if you make a well natured error, you often get back from the compiler a long page of rubbish if you are using templates (and you are). You put your goggles on and start swimming through it to find the nugget of gold that is the root cause of your problem.&#160;   
    I can hear you C++ gurus screaming: come on, come on, it’s not that bad. After a while you get used to it. You become proficient in rubbish swimming. That makes me think of the story of that guy who lived in a strange neighbourhood where, as soon as you open the door of you house, someone kicks you in the nuts. His wife suggested that they moved to a better part of town, but the man replied: “no worries, I got used to it”. 
  * <u>Syntax oddity:</u> we did our best to make the gods of syntax happy in this series of articles, but we are still far removed from Haskell, F#, etc beauty… 
  * <u>Advanced features</u>: if you go beyond the basics of functional languages, there is a plethora of interesting features that just make your life so much easier and bring your code to an higher level of abstraction. Things like monads (i.e. f# async workflow), type providers, Haskell’s lazy execution, Haskell’s super strong type system, Closure’s transactional memory etc… Boost is trying to bring many of these things to C++, but there is still a big gap to be filled. 
  * <u>Temptation to cheat</u>: you can cheat in many functional programming languages (i.e. having mutable variables), but nowhere the temptation is as strong as in C++. You need an iron discipline not to do it. The fact that sometimes cheating is the right thing to do makes it even worse. 

Overall, am I going to use C++ now as my main programming language? Not really. I don’t have one of those. My general view is to always use the best language for the job at hand (yes, I even use Javascript for web pages).

C++ has some unique characteristics (i.e. speed, cross compilation & simple C interfacing). I’m going to use it whenever I need these characteristics, but now I’ll be a happier user knowing that I can write decent functional code in it.