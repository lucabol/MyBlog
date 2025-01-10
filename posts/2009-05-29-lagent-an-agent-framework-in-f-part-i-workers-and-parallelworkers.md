---
id: 1065
title: 'LAgent : an agent framework in F# – Part I – Workers and ParallelWorkers'
date: 2009-05-29T13:26:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/05/29/lagent-an-agent-framework-in-f-part-i-workers-and-parallelworkers/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/05/29/lagent-an-agent-framework-in-f-part-i-workers-and-parallelworkers.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9648937"
orig_parent_id:
  - "9648937"
orig_thread_id:
  - "657915"
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
  - http://blogs.msdn.com/b/lucabol/archive/2009/05/29/lagent-an-agent-framework-in-f-part-i-workers-and-parallelworkers.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="LAgent : an agent framework in F# &ndash; Part I &ndash; Workers and ParallelWorkers" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/05/29/lagent-an-agent-framework-in-f-part-i-workers-and-parallelworkers/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="LAgent : an agent framework in F# &ndash; Part I &ndash; Workers and ParallelWorkers" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/05/29/lagent-an-agent-framework-in-f-part-i-workers-and-parallelworkers/" />
    <meta name="twitter:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    
restapi_import_id:
  - 5c011e0505e67
original_post_id:
  - "213"
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
  * [Part IX – Counting words …](http://blogs.msdn.com/lucabol/archive/2009/09/18/lagent-an-agent-framework-in-f-part-ix-counting-words.aspx) 

## Introduction

I like to try out different programming paradigms. I started out as an object oriented programmer. In university, I used Prolog. I then learned functional programming. I also experimented with various shared memory parallel paradigms (i.e. async, tasks and such). I now want to learn more about message based parallel programming ([Erlang](http://www.amazon.com/Programming-Erlang-Software-Concurrent-World/dp/193435600X) style). I'm convinced that doing so makes me a better programmer. Plus, I enjoy it …

My usual learning style is to build a framework that replicates a particular programming model and then write code using it. In essence, I build a very constrained environment. For example, when learning functional programming, I didn't use any OO construct for a while even if my programming language supports them.

In this case, I built myself a little agent framework based on F# _MailboxProcessors_. I could have used _MailboxProcessors_ directly, but they are too flexible for my goal. Even to write a simple one of these guys, you need to use async and recursion in a specific pattern, which I always forget. Also, there are multiple ways to to do Post. I wanted things to be as simple as possible. I was willing to sacrifice flexibility for that.

Notice that there are serious efforts in this space (as [Axum](http://blogs.msdn.com/maestroteam/)). This is not one of them. It's just a simple thing I enjoy working on between one meeting and the next.

## Workers and ParallelWorkers

The two major primitives are spawning an agent and posting a message.

```fsharp
let echo = spawnWorker (fun msg -> printfn "%s" msg)
echo <-- "Hello guys!"
```

There are two kinds of agents in my system. A _worker_ is an agent that doesn't keep any state between consecutive messages. It is a stateless guy. Notice that the lambda that you pass to create the agent is strongly typed (aka _msg_ is of type _string_). Also notice that I overloaded the _<—_ operator to mean _Post_.

Given that a worker is stateless, you can create a whole bunch of them and, when a message is posted, route it to one of them transparently.

```fsharp
let parallelEcho = spawnParallelWorker(fun s -> printfn "%s" s) 10
parallelEcho <-- "Hello guys!"
```

For example, in the above code, 10 workers are created and, when a message is posted, it gets routed to one of them (using a super duper innovative dispatching algorithm I'll describe in the implementation part). This _parallelWorker_ guy is not really needed, you could easily built it out of the other primitives, but it is kind of cute.

To show the difference between a worker and a _parallelWorker_, consider this:

```fsharp
let tprint s = printfn "%s running on thread %i" s Thread.CurrentThread.ManagedThreadId
let echo1 = spawnWorker (fun s -> tprint s)
let parallelEcho1 = spawnParallelWorker(fun s -> tprint s) 10
let messages = ["a";"b";"c";"d";"e";"f";"g";"h";"i";"l";"m";"n";"o";"p";"q";"r";"s";"t"]
messages |> Seq.iter (fun msg -> echo1 <-- msg)
messages |> Seq.iter (fun msg -> parallelEcho1 <-- msg)
```

The result of the _echo1_ iteration is:

> **a running on thread 11
        
>   
> b running on thread 11
        
>   
> c running on thread 11
        
>   
> d running on thread 11
        
>   
> …**

While the result of the _parallelEcho1_ iteration is:

> **a running on thread 13
        
>   
> c running on thread 14
        
>   
> b running on thread 12
        
>   
> o running on thread 14
        
>   
> m running on thread 13
        
>   
> …**

Notice how the latter executes on multiple threads (but not in order). Next time I'll talk about agents, control messages and error management.
