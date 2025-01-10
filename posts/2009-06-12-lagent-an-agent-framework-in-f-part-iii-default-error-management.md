---
id: 193
title: 'LAgent: an agent framework in F# – Part III – Default error management'
date: 2009-06-12T14:07:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/06/12/lagent-an-agent-framework-in-f-part-iii-default-error-management/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/06/12/lagent-an-agent-framework-in-f-part-iii-default-error-management.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9649127"
orig_parent_id:
  - "9649127"
orig_thread_id:
  - "657926"
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
  - http://blogs.msdn.com/b/lucabol/archive/2009/06/12/lagent-an-agent-framework-in-f-part-iii-default-error-management.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="LAgent: an agent framework in F# &ndash; Part III &ndash; Default error management" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/06/12/lagent-an-agent-framework-in-f-part-iii-default-error-management/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="LAgent: an agent framework in F# &ndash; Part III &ndash; Default error management" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/06/12/lagent-an-agent-framework-in-f-part-iii-default-error-management/" />
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
  * [Part IX – Counting words …](http://blogs.msdn.com/lucabol/archive/2009/09/18/lagent-an-agent-framework-in-f-part-ix-counting-words.aspx) 

## Default error management

What happens when an error occurs? Well, ideally you want to notify someone and continue processing messages. By default you want to print the error and as much information as you can about it.

Let's first see what happens if you pass the wrong message type:

```fsharp
counter1 <-- "fst"
```

Generates:

> **> The exception below occurred on agent Undefined at state 3 with message "fst". The agent was started with state 0.
        
>   
> System.InvalidCastException: Specified cast is not valid.
        
>   
> &#160;&#160; at Microsoft.FSharp.Core.LanguagePrimitives.IntrinsicFunctions.UnboxGeneric\[T\](Object source)
        
>   
> &#160;&#160; at FSI_0003.AgentSystem.f@158.Invoke(Object a, Object b)
        
>   
> &#160;&#160; at Microsoft.FSharp.Core.FastFunc\`2.InvokeFast\[V\](FastFunc\`2 func, T arg1, TResult arg2)
        
>   
> &#160;&#160; at Microsoft.FSharp.Core.FastFunc\`2.InvokeFast\[V\](FastFunc\`2 func, T arg1, TResult arg2)
        
>   
> &#160;&#160; at FSI_0003.AgentSystem.loop@20-3.Invoke(Unit unitVar)
        
>   
> &#160;&#160; at Microsoft.FSharp.Control.AsyncBuilderImpl.callA@245.Invoke(AsyncParams\`1 args)**

You get information about the current state of the agent, the message that generated the error, the initial state of the agent and the exception that was generated. But, in a system with several agents, you'd like to know which one agent failed. Then you need to name your agent:

```fsharp
counter1 <-- SetName("Bob")
counter1 <-- "fadfad"
```

Now you get (important part in blue):

> **> The exception below occurred on agent <font color="#0000ff">Bob</font> at state 3 with message "fadfad". The agent was started with state 0.
        
>   
> System.InvalidCastException: Specified cast is not valid.
        
>   
> &#160;&#160; at Microsoft.FSharp.Core.LanguagePrimitives.IntrinsicFunctions.UnboxGeneric\[T\](Object source)
        
>   
> &#160;&#160; at FSI_0003.AgentSystem.f@158.Invoke(Object a, Object b)
        
>   
> &#160;&#160; at Microsoft.FSharp.Core.FastFunc\`2.InvokeFast\[V\](FastFunc\`2 func, T arg1, TResult arg2)
        
>   
> &#160;&#160; at Microsoft.FSharp.Core.FastFunc\`2.InvokeFast\[V\](FastFunc\`2 func, T arg1, TResult arg2)
        
>   
> &#160;&#160; at FSI_0003.AgentSystem.loop@20-3.Invoke(Unit unitVar)
        
>   
> &#160;&#160; at Microsoft.FSharp.Control.AsyncBuilderImpl.callA@245.Invoke(AsyncParams\`1 args)**

The important thing is that the agent continues running. It lives to fight another day. Hence:

```fsharp
counter1 <-- 3
```

Produces:

> **From 3 to 6**

Which shows that the agent is running and that it has kept its current state. Also errors can occur inside the message handler with a similar result:

```fsharp
(spawnAgent (fun msg state -> state / msg) 100) <-- 0
```

Produces:

> **> The exception below occurred on agent Undefined at state 100 with message 0. The agent was started with state 100.
        
>   
> System.DivideByZeroException: Attempted to divide by zero.
        
>   
> &#160;&#160; at FSI_0013.it@48-3.Invoke(Int32 msg, Int32 state)
        
>   
> &#160;&#160; at Microsoft.FSharp.Core.FastFunc\`2.InvokeFast\[V\](FastFunc\`2 func, T arg1, TResult arg2)
        
>   
> &#160;&#160; at FSI_0003.AgentSystem.f@158.Invoke(Object a, Object b)
        
>   
> &#160;&#160; at Microsoft.FSharp.Core.FastFunc\`2.InvokeFast\[V\](FastFunc\`2 func, T arg1, TResult arg2)
        
>   
> &#160;&#160; at Microsoft.FSharp.Core.FastFunc\`2.InvokeFast\[V\](FastFunc\`2 func, T arg1, TResult arg2)
        
>   
> &#160;&#160; at FSI_0003.AgentSystem.loop@20-3.Invoke(Unit unitVar)
        
>   
> &#160;&#160; at Microsoft.FSharp.Control.AsyncBuilderImpl.callA@245.Invoke(AsyncParams\`1 args)**

But this might not be what you want. You might want to customize what happens when an error occurs. We'll talk about that next.
