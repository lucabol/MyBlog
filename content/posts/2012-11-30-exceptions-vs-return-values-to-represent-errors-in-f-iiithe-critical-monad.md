---
id: 107
title: 'Exceptions vs. Return Values to represent errors (in F#) – III–The Critical monad'
date: 2012-11-30T16:41:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=107
permalink: /2012/11/30/exceptions-vs-return-values-to-represent-errors-in-f-iiithe-critical-monad/
categories:
  - 'F#'
tags:
  - 'F#'
---
Code for this post is [here](https://github.com/lucabol/ErrorExceptional).

In the last post we looked at some Critical code and decided that, albeit correct, it is convoluted. The error management path obfuscates the underlying logic. Also we have no way of knowing if a developer had thought about the error path or not when invoking a function.

Let’s tackle the latter concern first as it is easier. We want the developer to declaratively tag each method call with something that represents his intent about managing the Contingencies or Faults of the function.&#160; Moreover if the function has contingencies, we want to force the developer to manage them explicitly.

We cannot use attributes for this as function calls happen in the middle of the code, so there is no place to stick attributes into. So we are going to use higher level functions to wrap the function calls. 

The first case is easy. If the developer thinks that the caller of his code has no way to recover from all the exceptions thrown by a function, he can prepend his function call with the ‘fault’ word as in:

<pre class="code"><span style="background:white;color:black;">fault parseUser userText</span></pre>

That signals readers of the code that the developer is willing to propagate up all the exceptions thrown by the function parseUser. Embarrassingly, ‘fault’ is implemented as:

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">fault f = f
</span></pre>

So it is just a tag. Things get trickier when the function has contingencies. We want to find a way to manage them without introducing undue complexity in the code. 

We’d like to catch some exceptions thrown by the function and convert them to return values and then either return such return values or manage the contingency immediately after the function call. On top of that, we’d want all of the code written after the function call to appear as clean as if no error management were taking place. Monads (computation values) can be used to achieve these goals.

Last time we introduced a type to represent error return values:

<pre class="code"><span style="background:white;color:blue;">type </span><span style="background:white;color:black;">Result&lt;'a, 'b&gt; =
| Success </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">'a
| Failure </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">'b
</span></pre>

<pre class="code"><span style="background:white;color:blue;">type </span><span style="background:white;color:black;">UserFetchError =
| UserNotFound  </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">exn
| NotAuthorized </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">int * exn </span></pre>

We can then create a computation expression that ‘abstracts out’ the Failure case and let you write the code as cleanly as if you were not handling errors. Let’s call such thing ‘critical’. Here is how the final code looks like:

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">tryFetchUser3 userName =
    </span><span style="background:white;color:blue;">if </span><span style="background:white;color:black;">String.IsNullOrEmpty userName </span><span style="background:white;color:blue;">then </span><span style="background:white;color:black;">invalidArg </span><span style="background:white;color:#a31515;">"userName" "userName cannot be null/empty"
    </span><span style="background:white;color:blue;">critical </span><span style="background:white;color:black;">{
        </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">Unauthorized (ex:exn) = NotAuthorized (ex.Message.Length, ex)</span><span style="background:white;color:green;">
        </span><span style="background:white;color:blue;">let! </span><span style="background:white;color:black;">userText = contingent1
                            [FileNotFoundException()        :&gt; exn, UserNotFound;
                             UnauthorizedAccessException()  :&gt; exn, Unauthorized]
                            dbQuery (userName + </span><span style="background:white;color:#a31515;">".user"</span><span style="background:white;color:black;">)
        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">fault parseUser userText
    }</span></pre>

You can compare this with the code you would have to write without the ‘critical’ library (from last post):

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
    | Failure(ex)       </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">Failure(ex)
</span></pre>

And with the original (not critical) function:

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">fetchUser userName =
    </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">userText            = dbQuery (userName + </span><span style="background:white;color:#a31515;">".user"</span><span style="background:white;color:black;">)
    </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">user                = parseUser(userText)
    user
</span></pre>

<span style="background:white;color:black;"></span>

Let’s go step by step and see how it works. First of all, you need to enclose the Critical parts of your code (perhaps your whole program) in a ‘critical’ computation:

<pre class="code"><span style="background:white;color:black;">    </span><span style="background:white;color:blue;">critical </span><span style="background:white;color:black;">{<br />       …
</span><span style="background:white;color:black;">    }
</span></pre>

This allows you to call functions that return a Result and manage the return result as if it were the successful result. If an error were generated, it would be returned instead. We will show how to manage contingencies immediately after the function call later.

The above is illustrated by the following:

<pre class="code"><span style="background:white;color:black;">        </span><span style="background:white;color:blue;">let! </span><span style="background:white;color:black;">userText = contingent1
                            [FileNotFoundException()        :&gt; exn, UserNotFound;
                             UnauthorizedAccessException()  :&gt; exn, Unauthorized]
                            dbQuery (userName + </span><span style="background:white;color:#a31515;">".user"</span><span style="background:white;color:black;">)</span></pre>

Here ‘contingent1’ is a function that returns a Result, but userText has type string. The Critical monad, and in particular the usage of ‘let!’ is what allows the magic to happen.

‘contingentN’ is a function that you call when you want to manage certain exceptions thrown by a function as contingencies. The N part represents how many parameters the function takes.

The first parameter to ‘contingent1’ is a list of pairs (Exception, ErrorReturnConstructor). That means: when an exception of type Exception is thrown, return the result of calling ‘ErrorReturnConstructor(Exception)’ wrapped inside a ‘Failure’ object. The second parameter to ‘contingent1’ is the function to invoke and the third is the argument to pass to it.

Conceptually, ‘ContingentN’ is a tag that says: if the function throws one of these exceptions, wrap them in these return values and propagate all the other exceptions. Notice that Unauthorized takes an integer and an exception as parameters while the ErrorReturnConstructor takes just an exception. So we need to add this line of code:

<pre class="code"><span style="background:white;color:black;">        </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">Unauthorized (ex:exn) = NotAuthorized (ex.Message.Length, ex) </span></pre>

After the contingent1 call, we can then write code as if the function returned a normal string:

<pre class="code"><span style="background:white;color:black;">        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">fault parseUser userText
</span></pre>

This achieves that we set up to do at the start of the series:

  * Contingencies are now explicit in the signature of tryFetchUser3 
  * The developer needs to indicate for each function call how he intend to manage contingencies and faults 
  * The code is only slightly more complex than the non-critical one 

You can also decide to manage your contingencies immediately after calling a function. Perhaps there is a way to recover from the problem. For example, if the user is not in the database, you might want to add a standard one:

<pre class="code"><span style="background:white;color:blue;"><font color="#000000" face="Lucida Sans Unicode">

<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">createAndReturnUser userName = </span><span style="background:white;color:blue;">critical </span><span style="background:white;color:black;">{ </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">{Name = userName; Age = 43}}<br />
</span>&lt;/font>let &lt;/span><span style="background:white;color:black;">tryFetchUser4 userName =
    </span><span style="background:white;color:blue;">if </span><span style="background:white;color:black;">String.IsNullOrEmpty userName </span><span style="background:white;color:blue;">then </span><span style="background:white;color:black;">invalidArg </span><span style="background:white;color:#a31515;">"userName" "userName cannot be null/empty"
    </span><span style="background:white;color:blue;">critical </span><span style="background:white;color:black;">{
        </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">Unauthorized (ex:exn) = NotAuthorized (ex.Message.Length, ex) </span><span style="background:white;color:green;">// depends on ex
        </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">userFound = contingent1
                            [FileNotFoundException()        :&gt; exn, UserNotFound;
                             UnauthorizedAccessException()  :&gt; exn, Unauthorized]
                            dbQuery (userName + </span><span style="background:white;color:#a31515;">".user"</span><span style="background:white;color:black;">)
        </span><span style="background:white;color:blue;">match </span><span style="background:white;color:black;">userFound </span><span style="background:white;color:blue;">with
        </span><span style="background:white;color:black;">| Success(userText)         </span><span style="background:white;color:blue;">-&gt; return  </span><span style="background:white;color:black;">fault parseUser userText
        | Failure(UserNotFound(_))  </span><span style="background:white;color:blue;">-&gt; return! </span><span style="background:white;color:black;">createAndReturnUser(userName)
        | Failure(x)                </span><span style="background:white;color:blue;">-&gt; return! </span><span style="background:white;color:black;">Failure(x)
    }</span></pre>


<p>
  The only difference in this case is the usage of ‘let’ instead of ‘let!’. This exposes the real return type of the function allowing you to pattern match against it.
</p>


<p>
  Sometimes a simple exception to return value mapping might not be enough and you want more control on which exceptions to catch and how to convert them to return values. In such cases you can use contingentGen:
</p>


<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">tryFetchUser2 userName =
    </span><span style="background:white;color:blue;">if </span><span style="background:white;color:black;">String.IsNullOrEmpty userName </span><span style="background:white;color:blue;">then </span><span style="background:white;color:black;">invalidArg </span><span style="background:white;color:#a31515;">"userName" "userName cannot be null/empty"
    </span><span style="background:white;color:blue;">critical </span><span style="background:white;color:black;">{
        </span><span style="background:white;color:blue;">let! </span><span style="background:white;color:black;">userText = contingentGen
                            (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">ex </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">ex FileNotFoundException || ex UnauthorizedAccessException)
                            (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">ex </span><span style="background:white;color:blue;">-&gt;
                                match </span><span style="background:white;color:black;">ex </span><span style="background:white;color:blue;">with
                                       </span><span style="background:white;color:black;">| FileNotFoundException       </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">UserNotFound(ex)
                                       | UnauthorizedAccessException </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">NotAuthorized(3, ex)
                                       | _ </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">raise ex)
                            (</span><span style="background:white;color:blue;">fun </span><span style="background:white;color:black;">_ </span><span style="background:white;color:blue;">-&gt; </span><span style="background:white;color:black;">dbQuery (userName + </span><span style="background:white;color:#a31515;">".user"</span><span style="background:white;color:black;">))
        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">fault parseUser userText
    }
</span></pre>


<p>
  The first parameter is a lambda describing when to catch an exception. The second lambda translate between exceptions and return values. The third lambda represents which function to call.
</p>


<p>
  Sometimes you might want to catch all the exceptions that a function might throw and convert them to a single return value:
</p>


<pre class="code"><span style="background:white;color:blue;">type </span><span style="background:white;color:black;">GenericError = GenericError </span><span style="background:white;color:blue;">of </span><span style="background:white;color:black;">exn
 </span><span style="background:white;color:green;">// 1. Wrapper that prevents exceptions for escaping the method by wrapping them in a generic critical result
</span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">tryFetchUserNoThrow userName =
    </span><span style="background:white;color:blue;">if </span><span style="background:white;color:black;">String.IsNullOrEmpty userName </span><span style="background:white;color:blue;">then </span><span style="background:white;color:black;">invalidArg </span><span style="background:white;color:#a31515;">"userName" "userName cannot be null/empty"
    </span><span style="background:white;color:blue;">critical </span><span style="background:white;color:black;">{
        </span><span style="background:white;color:blue;">let! </span><span style="background:white;color:black;">userText = neverThrow1 GenericError dbQuery (userName + </span><span style="background:white;color:#a31515;">".user"</span><span style="background:white;color:black;">)
        </span><span style="background:white;color:blue;">return </span><span style="background:white;color:black;">fault parseUser userText
    }</span></pre>


<p>
  And sometimes you might want to go the opposite way. Given a function that exposes some contingencies, you want to translate them to faults because you don’t know how to recover from them.
</p>


<pre class="code"><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">operateOnExistingUser userName =
    </span><span style="background:white;color:blue;">let </span><span style="background:white;color:black;">user = alwaysThrow GenericException tryFetchUserNoThrow userName
    ()</span></pre>


<p>
  Next time we’ll look at how the Critical computation expression is implemented.
</p>