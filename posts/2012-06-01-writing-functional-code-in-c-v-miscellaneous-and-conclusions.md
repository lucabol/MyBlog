---
id: 96
title: Writing functional code in C++ V – Miscellaneous and conclusions
date: 2012-06-01T06:45:26+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=96
categories:
  - C
tags:
  - C++
  - functional
---
Just a couple of trivialities and my parting thoughts.

## Nested functions

If your language has lambdas, you don't need nested functions support because you can implement them using it.

I am a heavy user of nested functions, but I'm of two minds about it. On one side, I like that they sit close to where they are used, avoiding going outside the main function body to understand them. I also like that you don't need to pass a lot of parameters to them, as they capture the function locals. On the other side, they end up creating the impression that your functions are very long and so, in my eyes, they occasionally reduce readability. The IDE helps you out there (at least VS 11) by allowing you to collapse the lambdas.

An example of trivial case is below:

```cpp
BOOST_AUTO_TEST_CASE(NestedFunctions)
{
    int x = 3;
    auto sumX = [&] (int y) { return x + y;};
    BOOST_CHECK_EQUAL(sumX(2), 3+2);
}
```

And here is a more realistic one (not written in a functional style), where readability is reduced by the three nested functions (among many other things):

```cpp
bool condor(
            boost::gregorian::date now,  // date to evaluate
            double spot,                 // spot price underlying
            double v,                    // ATM volatility
            double r,                    // risk free rate
            double step,                 // % of spot price to keep as distance between wings
            int minCallShortDist,        // min distance from the short call strike in steps
            int minPutShortDist,         // min distance from the short put strike in steps
            int minDays,                 // min number of days to expiry
            int maxDays,                 // max number of days to expiry
            double maxDelta,             // max acceptable delta value for shorts in steps
            double minPremium,           // min accepted premium as % of step
            Condor& ret                  // return value
            )
{
    // convert params to dollar signs
    auto stepPr            = round(step * spot);
    auto toUSD             = [stepPr] (double x) { return round(stepPr * x);};
    auto minCpr            = toUSD( minCallShortDist );
    auto minPpr            = toUSD( minPutShortDist );
    auto premiumPr         = toUSD( minPremium );
    // calc strike values for short legs
    auto atm               = round(spot / stepPr) * (long) stepPr;
    auto callShort         = atm + minCpr;
    auto putShort          = atm - minPpr;
    auto addDays           = [](boost::gregorian::date d, int dys) -> boost::gregorian::date {
        using namespace boost::gregorian;
        auto toAdd         = days(dys);
        auto dTarget       = d + toAdd;
        return  dTarget;
    };
    // calc min & max allowed expiry dates
    auto minDate           = addDays(now, minDays);
    auto maxDate           = addDays(now, maxDays);
    auto expiry            = calcExpiry(now, 0);
    // find first good expiry
    while(expiry < minDate)
        expiry          = calcExpiry(expiry, +1);
    Greeks g;
    auto scholes           = [=, &g] (double strike, int days, bool CorP) {
        return blackScholesEuro(spot, strike, days, CorP, v, r, g, true);
    };
    // find a condor that works at this expiry
    auto findCondor        = [=, &g, &ret] (int days) -> bool {
        ret.shortCallStrike                = callShort;
        ret.shortPutStrike                 = putShort;
        auto shCallPremium                 = 0.0;
        auto shPutPremium                  = 0.0;
        // find short call strike price < maxDelta
        while(true) {
            shCallPremium                  = scholes(ret.shortCallStrike, days, true);
            if(g.delta <= maxDelta)
                break;
            else
                ret.shortCallStrike        += stepPr;
        }
        // find short put strike price < maxDelta
        while(true) {
            shPutPremium                   = scholes(ret.shortPutStrike, days, false);
            if( (- g.delta) <= maxDelta)
                break;
            else
                ret.shortPutStrike         -= stepPr;
        }
        // check premium is adeguate
        ret.longCallStrike                = ret.shortCallStrike + stepPr;
        ret.longPutStrike                 = ret.shortPutStrike  - stepPr;
        auto lgCall                       = scholes(ret.longCallStrike, days, true);
        auto lgPut                        = scholes(ret.longPutStrike,  days, false);
        ret.netPremium                    = shCallPremium + shPutPremium - lgCall - lgPut;
        return ret.netPremium > premiumPr;
    };
    // increases the expiry until it finds a condor or the expiry is too far out
    while (expiry < maxDate) {
        auto days        = (expiry - now).days();
        if(findCondor(days)) {
            ret.year     = expiry.year();
            ret.month    = expiry.month();
            ret.day      = expiry.day();
            return true;
        }
        expiry           = calcExpiry(expiry, +1);
    }
    return false;
}
```

That is quite a mouthful, isn't it? But really the function is not that long. It is all these nested functions that makes it seems so.

## Tuples

Tuples are another feature toward which I have mixed feelings. They are really useful to return multiple results from a function and for rapid prototyping of concepts. But they are easy to abuse. Creating Records is almost always a better, safer way to craft your code, albeit more verbose.

The standard C++ has an excellent tuple library that makes working with them almost as easy as in mainstream functional languages. The below function shows creating them, getting their value, passing them to functions and deconstructing them:

```cpp
BOOST_AUTO_TEST_CASE(Tuples)
{
    auto t = make_tuple("bob", "john", 3, 2.3);
    BOOST_CHECK_EQUAL(get<0>(t), "bob");
    BOOST_CHECK_EQUAL(get<2>(t), 3);
    // yep, compiler error
    //auto k = get<10>(t);
    auto t2(t);
    BOOST_CHECK(t2 == t);
    // passing as argument, returning it
    auto f = [] (tuple<string, string, int, double> t) { return t;};
    auto t1 = f(t);
    BOOST_CHECK(t == t1);
    // automatic deconstruction
    string s1; string s2; int i; double d;
    std::tie(s1, s2, i, d) = f(t);
    BOOST_CHECK_EQUAL(s1, "bob");
    // partial reconstruction
    string s11;
    std::tie(s11, ignore, ignore, ignore) = f(t);
    BOOST_CHECK_EQUAL(s11, "bob");
}
```

## Conclusion

I'm sure there are some fundamental functional features that I haven't touched on (i.e. currying, more powerful function composition, etc…).  Despite that, I think we have enough material here to start drawing some conclusions. To start with, where is C++ deficient compared to mainstream functional languages _<u>for the sake of writing functional code</u>_ ?

  * <u>Compiler errors</u>: if you make a well natured error, you often get back from the compiler a long page of rubbish if you are using templates (and you are). You put your goggles on and start swimming through it to find the nugget of gold that is the root cause of your problem.   
    I can hear you C++ gurus screaming: come on, come on, it's not that bad. After a while you get used to it. You become proficient in rubbish swimming. That makes me think of the story of that guy who lived in a strange neighbourhood where, as soon as you open the door of you house, someone kicks you in the nuts. His wife suggested that they moved to a better part of town, but the man replied: "no worries, I got used to it". 
  * <u>Syntax oddity:</u> we did our best to make the gods of syntax happy in this series of articles, but we are still far removed from Haskell, F#, etc beauty… 
  * <u>Advanced features</u>: if you go beyond the basics of functional languages, there is a plethora of interesting features that just make your life so much easier and bring your code to an higher level of abstraction. Things like monads (i.e. f# async workflow), type providers, Haskell's lazy execution, Haskell's super strong type system, Closure's transactional memory etc… Boost is trying to bring many of these things to C++, but there is still a big gap to be filled. 
  * <u>Temptation to cheat</u>: you can cheat in many functional programming languages (i.e. having mutable variables), but nowhere the temptation is as strong as in C++. You need an iron discipline not to do it. The fact that sometimes cheating is the right thing to do makes it even worse. 

Overall, am I going to use C++ now as my main programming language? Not really. I don't have one of those. My general view is to always use the best language for the job at hand (yes, I even use Javascript for web pages).

C++ has some unique characteristics (i.e. speed, cross compilation & simple C interfacing). I'm going to use it whenever I need these characteristics, but now I'll be a happier user knowing that I can write decent functional code in it.
