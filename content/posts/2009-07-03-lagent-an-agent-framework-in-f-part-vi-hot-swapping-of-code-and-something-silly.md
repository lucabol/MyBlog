---
id: 163
title: 'LAgent: an agent framework in F# – Part VI – Hot swapping of code (and something silly)'
date: 2009-07-03T15:23:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/07/03/lagent-an-agent-framework-in-f-part-vi-hot-swapping-of-code-and-something-silly/
permalink: /2009/07/03/lagent-an-agent-framework-in-f-part-vi-hot-swapping-of-code-and-something-silly/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/07/03/lagent-an-agent-framework-in-f-part-vi-hot-swapping-of-code-and-something-silly.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9649341"
orig_parent_id:
  - "9649341"
orig_thread_id:
  - "657941"
orig_application_key:
  - lucabol
orig_post_author_id:
  - "3896"
orig_post_author_username:
  - lucabol
orig_post_author_created:
  - 'Apr  2 2005 10:57:56:453AM'
orig_is_approved:
  - "1"
orig_attachment_count:
  - "0"
orig_url_title:
  - http://blogs.msdn.com/b/lucabol/archive/2009/07/03/lagent-an-agent-framework-in-f-part-vi-hot-swapping-of-code-and-something-silly.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="LAgent: an agent framework in F# &ndash; Part VI &ndash; Hot swapping of code (and something silly)" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/07/03/lagent-an-agent-framework-in-f-part-vi-hot-swapping-of-code-and-something-silly/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="LAgent: an agent framework in F# &ndash; Part VI &ndash; Hot swapping of code (and something silly)" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/07/03/lagent-an-agent-framework-in-f-part-vi-hot-swapping-of-code-and-something-silly/" />
    <meta name="twitter:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - fsharp
---
Download framework [here](http://code.msdn.microsoft.com/LAgent).

All posts are here:

  * [Part I  - Workers and ParallelWorkers](http://blogs.msdn.com/lucabol/archive/2009/05/29/lagent-an-agent-framework-in-f-part-i-workers-and-parallelworkers.aspx) 
  * [Part II  - Agents and control messages](http://blogs.msdn.com/lucabol/archive/2009/06/05/lagent-an-agent-framework-in-f-part-ii-agents-and-control-messages.aspx) 
  * [Part III  - Default error management](http://blogs.msdn.com/lucabol/archive/2009/06/12/lagent-an-agent-framework-in-f-part-iii-default-error-management.aspx) 
  * [Part IV  - Custom error management](http://blogs.msdn.com/lucabol/archive/2009/06/19/lagent-an-agent-framework-in-f-part-iv-custom-error-management.aspx) 
  * [Part V  - Timeout management](http://blogs.msdn.com/lucabol/archive/2009/06/26/lagent-an-agent-framework-in-f-part-v-timeout-management.aspx) 
  * [Part VI  - Hot swapping of code](http://blogs.msdn.com/lucabol/archive/2009/07/03/lagent-an-agent-framework-in-f-part-vi-hot-swapping-of-code-and-something-silly.aspx) 
  * [Part VII  - An auction framework](http://blogs.msdn.com/lucabol/archive/2009/07/10/lagent-an-agent-framework-in-f-part-vii-an-auction-application.aspx) 
  * [Part VIII – Implementing MapReduce (user model)](http://blogs.msdn.com/lucabol/archive/2009/09/04/lagent-an-agent-framework-in-f-part-viii-implementing-mapreduce-user-model.aspx) 
  * [Part IX – Counting words …](http://blogs.msdn.com/lucabol/archive/2009/09/18/lagent-an-agent-framework-in-f-part-ix-counting-words.aspx)&#160; 

#### Hot swapping of code

Let’s get back a couple of steps and consider what happens when you get an error. Sure, your agent will continue processing messages, but it might be doing the wrong thing. Your message handling code might be buggy.

Ideally you’d want to patch things on the fly. You’d want to replace the message processing code for an agent without stopping it.

Here is how you do it:

<pre class="code"><span style="color:blue;">let </span>counter2 = spawnAgent (<span style="color:blue;">fun </span>msg state <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"From %i to %i" </span>state (state + msg);<br />                                                                              state + msg) 0
counter2 &lt;-- 2
counter2 &lt;-- SetAgentHandler(<span style="color:blue;">fun </span>msg state –<span style="color:blue;">&gt;<br />                </span>printfn <span style="color:maroon;">"From %i to %i via multiplication" </span>state (state * msg); msg * state)
counter2 &lt;-- 3</pre>



Which generates:

> **From 0 to 2
        
>   
> From 2 to 6 via multiplication**

After the agent receives a _SetAgentHandler_ message, it switch from a ‘+’ agent to a ‘*’ agent on the fly!! All the messages that come after that one gets multiplied to the state. Also, the state is preserved between changes in behavior.

It might not be immediately apparent how to load a function at runtime, but it is really simple. Imagine that I get the data on the function to load from somewhere (i.e. a management console UI).

<pre class="code"><span style="color:blue;">let </span>assemblyNameFromSomewhere, typeNameFromSomewhere, methodNameFromSomewhere = <br />                                                <span style="color:maroon;">"mscorlib.dll"</span>, <span style="color:maroon;">"System.Console"</span>, <span style="color:maroon;">"WriteLine"</span></pre>

I can then use it to dynamically load a message handler (in this case _Console.Writeline_).

<pre class="code"><span style="color:blue;">let </span>a = Assembly.Load(assemblyNameFromSomewhere)
<span style="color:blue;">let </span>c = a.GetType(typeNameFromSomewhere)
<span style="color:blue;">let </span>m = c.GetMethod(methodNameFromSomewhere, [|<span style="color:maroon;">""</span>.GetType()|])
<span style="color:blue;">let </span>newF = <span style="color:blue;">fun </span>(msg:string) (state:obj) <span style="color:blue;">-&gt; </span>m.Invoke(<span style="color:blue;">null</span>, [| (msg:&gt;obj) |])</pre>

And then it is as simple as posting a _SetAgentHandler_.

<pre class="code">counter2 &lt;-- SetAgentHandler(newF)
counter2 &lt;-- <span style="color:maroon;">"blah"</span></pre>

Now our _counter2_ agent has become an echo agent on the fly, having loaded _Console.WriteLine_ dynamically. Note how the agent moved from being a ‘+’ agent taking integers to being a ‘*’ agent taking integers to being an ‘echo’ agent taking strings. And it didn’t stop processing messages for the whole time.

Obviously, you can do the same thing with workers:

<pre class="code">echo &lt;-- SetWorkerHandler(<span style="color:blue;">fun </span>msg <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"I'm an echo and I say: %s" </span>msg)
echo &lt;-- <span style="color:maroon;">"Hello"</span></pre>

And parallelWorkers:

<pre class="code">parallelEcho &lt;-- SetWorkerHandler(<span style="color:blue;">fun </span>msg <span style="color:blue;">-&gt; </span>tprint (<span style="color:maroon;">"I'm new and " </span>+ msg))
messages |&gt; Seq.iter (<span style="color:blue;">fun </span>msg <span style="color:blue;">-&gt; </span>parallelEcho &lt;-- msg)</pre>

#### A silly interlude

As a way to show some agents talking to each other, here is a simple program that simulates marital interactions (of the worst kind):

<pre class="code"><span style="color:blue;">let rec </span>husband = spawnWorker (<span style="color:blue;">fun </span>(To, msg) <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"Husband says: %s" </span>msg; To &lt;-- msg)
<span style="color:blue;">let rec </span>wife = spawnWorker (<span style="color:blue;">fun </span>msg <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"Wife says: screw you and your '%s'" </span>msg)
husband &lt;-- (wife, <span style="color:maroon;">"Hello"</span>)
husband &lt;-- (wife, <span style="color:maroon;">"But darling ..."</span>)
husband &lt;-- (wife, <span style="color:maroon;">"ok"</span>)</pre>

Which produces:

> **Husband says: Hello
        
>   
> Husband says: But darling
        
>   
> Wife says: screw you and your &#8216;Hello'
        
>   
> Wife says: screw you and your &#8216;But darling'
        
>   
> Husband says: ok
        
>   
> Wife says: screw you and your &#8216;ok'**

And yes, you cannot expect messages to be in the right sequence … Next up is an auction application.