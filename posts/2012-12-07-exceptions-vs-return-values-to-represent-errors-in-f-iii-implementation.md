---
id: 109
title: 'Exceptions vs. Return Values to represent errors (in F#) – IV – Implementation'
date: 2012-12-07T09:44:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=109
categories:
  - fsharp
tags:
  - fsharp
---
The Critical monad is defined as follows. First there is the type that propagates through the monad: 

<pre class="code"><span style="background:white;color:blue;">type </span><span style="background:white;color:black;">Result&lt;'a, 'b&gt; =
| Success </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">'a
| Failure </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">'b</span></pre>

  
Then we define the usual computation expression methods.
    


<pre class="code"><span style="background:white;color:blue;">type </span><span style="background:white;color:black;">Critical() =
       </span><span style="background:white;color:green;">// a -&gt; m a
        </span><span style="background:white;color:blue;">member </span><span style="background:white;color:black;">o.Return x       = Success x
        </span><span style="background:white;color:green;">// m a -&gt; (a -&gt; m b) -&gt; m b
        </span><span style="background:white;color:blue;">member </span><span style="background:white;color:black;">o.Bind (m, f)    = </span><span style="background:white;color:blue;">match </span><span style="background:white;color:black;">m </span><span style="background:white;color:blue;">with
                                    </span><span style="background:white;color:black;">| Failure e </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">Failure e
                                    | Success x </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">f x
        </span><span style="background:white;color:green;">// m a -&gt; m a
        </span><span style="background:white;color:blue;">member </span><span style="background:white;color:black;">o.ReturnFrom m   = m</span></pre>

Explaining how computational expressions work in F# is a blog onto itself. And several chapters in many books. Sufficient to say that conceptually this propagates the success value and returns the failure value.

We then define an instance of this type, so that we can use the nice ‘critical { … }’ syntax.

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">critical = Critical()
</span></pre>

  
We then go and define the functions that the user needs to use to annotate their function calls. The simplest one is the one to propagate any exception coming from the function ‘f’.
    


<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">fault f = f
</span></pre>

  
Then it comes the one to manage contingencies. This will trap any exception for which ‘stopF ex’ is ‘true’, call ‘errF ex’ to construct the error return value and wrap it in a ‘Failure’. Otherwise it will rethrow the exception.
    


<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">contingentGen stopF errF f =
    </span><span style="background:white;color:blue;">try
        </span><span style="background:white;color:black;">Success(f ())
    </span><span style="background:white;color:blue;">with
        </span><span style="background:white;color:black;">| ex </span><span style="background:white;color:blue;">when </span><span style="background:white;color:black;">stopF ex </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">Failure(errF ex)
        | _                </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">reraise ()
</span></pre>

Albeit very simple, the above is the core of the system. Everything else is just details. Let’s look at them.

First we want a function that takes as parameter a list of (Exception, ReturnValue) and gives back the correct stopF errF to plug into ‘contingentGen’.

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">exceptionMapToFuncs exMap =
    </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">tryFind ex = exMap |&gt; List.tryFind (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">(k, _) </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">k.GetType() = ex.GetType())
    (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">ex </span><span style="background:white;color:blue;">-&gt;
        let </span><span style="background:white;color:black;">found = tryFind ex
        </span><span style="background:white;color:blue;">match </span><span style="background:white;color:black;">found </span><span style="background:white;color:blue;">with </span><span style="background:white;color:black;">Some(_) </span><span style="background:white;color:blue;">-&gt; true </span><span style="background:white;color:black;">| None </span><span style="background:white;color:blue;">-&gt; false</span><span style="background:white;color:black;">),
    (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">ex </span><span style="background:white;color:blue;">-&gt;
        let </span><span style="background:white;color:black;">found = tryFind ex
        </span><span style="background:white;color:blue;">match </span><span style="background:white;color:black;">found </span><span style="background:white;color:blue;">with
        </span><span style="background:white;color:black;">| Some(k, v)    </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">v ex
        | None          </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">raise ex)
</span></pre>

Then ugliness comes. For the sake of getting a decent syntax (not great) on the calling site, we need to fake overloading of functions by the old trick of adding a number at the end. Thanks to [Tobias](http://gotocon.com/amsterdam-2012/speaker/Tobias+Gedell) to point out this (my api was even worse earlier).

I often wondered about the trade-off between currying and overloading for functions. I seem to always paint myself in a situation where I need overloading. In any case, here it goes:

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">contingent1 exMap f x =
    </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">stopF, errF = exceptionMapToFuncs exMap
    contingentGen stopF errF (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">_ </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">f x)
</span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">contingent2 exMap f x y =
    </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">stopF, errF = exceptionMapToFuncs exMap
    contingentGen stopF errF (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">_ </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">f x y)
</span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">contingent3 exMap f x y z =
    </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">stopF, errF = exceptionMapToFuncs exMap
    contingentGen stopF errF (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">_ </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">f x y z)
</span></pre>

  
Sometimes you want to trap all exceptions from a function and return your own error value:
    


<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">neverThrow1 exc f x     = contingentGen (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">_ </span><span style="background:white;color:blue;">-&gt; true</span><span style="background:white;color:black;">) (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">ex </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">exc ex) (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">_ </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">f x)
</span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">neverThrow2 exc f x y   = contingentGen (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">_ </span><span style="background:white;color:blue;">-&gt; true</span><span style="background:white;color:black;">) (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">ex </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">exc ex) (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">_ </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">f x y)
</span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">neverThrow3 exc f x y z = contingentGen (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">_ </span><span style="background:white;color:blue;">-&gt; true</span><span style="background:white;color:black;">) (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">ex </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">exc ex) (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">_ </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">f x y z)
</span></pre>

  
Other times you need to go from a function that returns return values to one that throws exceptions. You need translating from contingencies to faults:
    


<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">alwaysThrow exc f x =
    </span><span style="background:white;color:blue;">match </span><span style="background:white;color:black;">f x </span><span style="background:white;color:blue;">with
    </span><span style="background:white;color:black;">| Success(ret)              </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">ret
    | Failure(e)                </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">raise (exc e)
</span></pre>

And that’s it. Hopefully we have bridged the gap between exceptions and return values without making the code too ugly (just a little bit). Or perhaps not.

I need to add that I haven’t used this library myself (yet). I’m sure when I do I’ll discover many things to change.