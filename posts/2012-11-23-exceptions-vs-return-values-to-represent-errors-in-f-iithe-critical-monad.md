---
id: 104
title: 'Exceptions vs. Return Values to represent errors (in F#) – II– An example problem'
date: 2012-11-23T10:45:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=104
categories:
  - fsharp
tags:
  - fsharp
---
In the previous post, we talked about the difference between Critical and Normal code. In this post we are going to talk about the Critical code part. Ideally, we want:

  * A way to indicate that a particular piece of code (potentially the whole program) is Critical 
  * A way to force/encourage the programmer to make an explicit decision on the call site of a function on how he wants to manage the error conditions (both contingencies and faults) 
  * A way to force/encourage the programmer to expose contingencies/faults that are appropriate for the conceptual level of the function the code is in (aka don’t expose implementation details for the function,&#160; i.e. don’t throw SQLException from a getUser method where the caller is supposed to catch it) 

Remember that I can use the word ‘force’ here because the programmer has already taken the decision to analyse each line of code for error conditions. As we discussed in the previous post, In many/most cases, such level of scrutiny is unwarranted.

Let’s use the below scenario to unravel the design:

<pre class="code"><span style="background:white;color:blue;">type </span><span style="background:white;color:black;">User = {Name:string; Age:int}</span></pre>

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">fetchUser userName =
    </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">userText            = dbQuery (userName + </span><span style="background:white;color:#a31515;">".user"</span><span style="background:white;color:black;">)
    </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">user                = parseUser(userText)
    user</span></pre>

This looks like a very reasonable .NET function and it is indeed reasonable in Normal code, but not in Critical code. Note that the caller likely needs to handle the user-not-in-repository case because there is no way for the caller to check such condition beforehand without incurring the performance cost of two network roundtrips.

Albeit the beauty and simplicity, there are issues with this function in a Critical context: 

  * The function throws implementation related exceptions, breaking encapsulation when the user needs to catch them 
  * It is not clear from the code if the developer thought about error management (do you think he did?) 
  * Preconditions are not checked, what about empty or null strings? 

To test our design let’s define a fake dbQuery:

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">dbQuery     = </span><span style="background:white;color:blue;">function
    </span><span style="background:white;color:black;">| </span><span style="background:white;color:#a31515;">"parseError.user"     </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:#a31515;">"parseError"
    </span><span style="background:white;color:black;">| </span><span style="background:white;color:#a31515;">"notFound.user"       </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">raise (FileNotFoundException())
    | </span><span style="background:white;color:#a31515;">"notAuthorized.user"  </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">raise (UnauthorizedAccessException())
    | </span><span style="background:white;color:#a31515;">"unknown.user"        </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">failwith </span><span style="background:white;color:#a31515;">"Unknown error reading the file"
    </span><span style="background:white;color:black;">| _                     </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:#a31515;">"FoundUser"</span></pre>

The first two exceptions are contingencies, the caller of fetchUser is supposed to manage them. The unknown.user exception is a fault in the implementation. parseError triggers a problem in the parseUser function.

ParseUser looks like this:

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">parseUser   = </span><span style="background:white;color:blue;">function
    </span><span style="background:white;color:black;">| </span><span style="background:white;color:#a31515;">"parseError"          </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">failwith </span><span style="background:white;color:#a31515;">"Error parsing the user text"
    </span><span style="background:white;color:black;">| u                     </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">{Name = u; Age = 43}
</span></pre>

Let’s now create a test function to test the different versions of fetchUser that we are going to create:

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">test fetchUser =
    </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">p x                 = </span><span style="background:white;color:blue;">try </span><span style="background:white;color:black;">printfn </span><span style="background:white;color:#a31515;">"%A" </span><span style="background:white;color:black;">(fetchUser x) </span><span style="background:white;color:blue;">with </span><span style="background:white;color:black;">ex </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">printfn </span><span style="background:white;color:#a31515;">"%A %s" </span><span style="background:white;color:black;">(ex.GetType()) ex.Message
    p </span><span style="background:white;color:#a31515;">"found"
    </span><span style="background:white;color:black;">p </span><span style="background:white;color:#a31515;">"notFound"
    </span><span style="background:white;color:black;">p </span><span style="background:white;color:#a31515;">"notAuthorized"
    </span><span style="background:white;color:black;">p </span><span style="background:white;color:#a31515;">"parseError"
    </span><span style="background:white;color:black;">p </span><span style="background:white;color:#a31515;">"unknown"</span></pre>

Running the function exposes the problems described above. From the point of view of the caller, there is no way to know what to expect by just inspecting the signature of the function. There is no differentiation between contingencies and faults. The only way to achieve that is to catch some implementation-specific exceptions.

How would we translate this to Critical code?

First, we would define a type to represent the result of a function:

<pre class="code"><span style="background:white;color:blue;">type </span><span style="background:white;color:black;">Result&lt;'a, 'b&gt; =
| Success </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">'a
| Failure </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">'b
</span></pre>

This is called the Either type, but the names have been customized to represent this scenario. We then need to define which kind of contingencies our function could return.

<pre class="code"><span style="background:white;color:blue;">type </span><span style="background:white;color:black;">UserFetchError =
| UserNotFound  </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">exn
| NotAuthorized </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">int * exn</span></pre>

So we assume that the caller can manage the fact that the user is not found or not authorized. This type contains an Exception member.&#160; This is useful in cases where the caller doesn’t want to manage a contingency, but wants to treat it like a fault (for example when some Normal code is calling some Critical code).

In such cases, we don’t lose important debugging information. But we still don’t break encapsulation because the caller is not supposed to ‘catch’ a fault.

Notice that NotAuthorized contains an int member. This is to show that contingencies can carry some more information than just their type. For example, a caller could match on both the type and the additional data.

With that in place, let’s see how the previous function looks like:

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">tryFetchUser1 userName =
    </span><span style="background:white;color:blue;">if </span><span style="background:white;color:black;">String.IsNullOrEmpty userName </span><span style="background:white;color:blue;">then </span><span style="background:white;color:black;">invalidArg </span><span style="background:white;color:#a31515;">"userName" "userName cannot be null/empty"
    </span><span style="background:white;color:green;">// Could check for file existence in this case, but often not (i.e. db)
    </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">userResult =    </span><span style="background:white;color:blue;">try
                            </span><span style="background:white;color:black;">Success(dbQuery(userName + </span><span style="background:white;color:#a31515;">".user"</span><span style="background:white;color:black;">))
                        </span><span style="background:white;color:blue;">with
                        </span><span style="background:white;color:black;">| FileNotFoundException </span><span style="background:white;color:blue;">as </span><span style="background:white;color:black;">ex        </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">Failure(UserNotFound ex)
                        | UnauthorizedAccessException </span><span style="background:white;color:blue;">as </span><span style="background:white;color:black;">ex  </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">Failure(NotAuthorized(2, ex))
                        | ex                                    </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">reraise ()
    </span><span style="background:white;color:blue;">match </span><span style="background:white;color:black;">userResult </span><span style="background:white;color:blue;">with
    </span><span style="background:white;color:black;">| Success(userText) </span><span style="background:white;color:blue;">-&gt;
        let </span><span style="background:white;color:black;">user        = Success(parseUser(userText))
        user
    | Failure(ex)       </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">Failure(ex)</span></pre>

Here is what changed:

  * Changed name to tryXXX to convey the fact that the method has contingencies 
  * Added precondition test, which generates a fault 
  * The signature of the function now conveys the contingencies that the user is supposed to know about 

But still, there are problems:

  * The code became very long and convoluted obfuscating the success code path 
  * Still, has the developer thought about the error conditions in parseUser and decided to let exceptions get out, or did she forget about it? 

The return value crowd at this point is going to shout: “Get over it!! Your code doesn’t need to be elegant, it needs to be correct!”. But I disagree, obfuscating the success code path is a problem because it becomes harder to figure out if your business logic is correct. It is harder to know if you solved the problem you set out to solve in the first place.

In the next post we’ll see what we can do about keeping beauty and being correct.