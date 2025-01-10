---
id: 183
title: 'LAgent: an agent framework in F# – Part IV – Custom error management'
date: 2009-06-19T14:36:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/06/19/lagent-an-agent-framework-in-f-part-iv-custom-error-management/
orig_url:
  - 'http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/06%20/19/lagent-an-agent-framework-in-f-part-iv-custom-error-management.aspx'
orig_site_id:
  - "3896"
orig_post_id:
  - "9649197"
orig_parent_id:
  - "9649197"
orig_thread_id:
  - "657930"
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
  - http://blogs.msdn.com/b/lucabol/archive/2009/06/19/lagent-an-agent-framework-in-f-part-iv-custom-error-management.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="LAgent: an agent framework in F# &ndash; Part IV &ndash; Custom error management" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/06/19/lagent-an-agent-framework-in-f-part-iv-custom-error-management/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="LAgent: an agent framework in F# &ndash; Part IV &ndash; Custom error management" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/06/19/lagent-an-agent-framework-in-f-part-iv-custom-error-management/" />
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

## Custom error management

In the last part we saw what happens by default in the framework when an error occurs. But that might not be what you want. You might want to have your sophisticated error detection and recovery distributed algorithm.

To make such a thing possible each agent has a manager. The manager is an agent that gets called whenever an error occurs in the agent it is monitoring.

In code:

```fsharp
let manager = spawnWorker (fun (agent, name:string, ex:Exception, msg:obj,
                 state, initialState) -> printfn "%s restarting ..." name; agent <-- Restart)
counter1 <-- SetManager(manager)
```

Whenever an error is generated the manager receives a tuple of:

> (agent, name, exception, message, currentState, inititialState)

This manager prints out something and then restarts the agent. Let's trigger an error by posting the wrong message:

```fsharp
counter1 <-- "afdaf"
counter1 <-- 2
```

The expectation is that the counter will restart from 0 whenever an error is triggered. This is what happens:

> **Bob restarting
        
>   
> From 0 to 2**

Which is what we expected. Obviously this is not a very sophisticated error recovery algorithm. You might want to do something more meaningful. Hopefully you have enough information to build whatever you need.

A particularly important class of unexpected event is timeouts. We'll talk about them next.
