---
id: 1064
title: 'LAgent : an agent framework in F# – Part II – Agents and control messages'
date: 2009-06-05T14:03:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/06/05/lagent-an-agent-framework-in-f-part-ii-agents-and-control-messages/
permalink: /2009/06/05/lagent-an-agent-framework-in-f-part-ii-agents-and-control-messages/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/06/05/lagent-an-agent-framework-in-f-part-ii-agents-and-control-messages.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9649041"
orig_parent_id:
  - "9649041"
orig_thread_id:
  - "657919"
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
  - http://blogs.msdn.com/b/lucabol/archive/2009/06/05/lagent-an-agent-framework-in-f-part-ii-agents-and-control-messages.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="LAgent : an agent framework in F# &ndash; Part II &ndash; Agents and control messages" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/06/05/lagent-an-agent-framework-in-f-part-ii-agents-and-control-messages/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="LAgent : an agent framework in F# &ndash; Part II &ndash; Agents and control messages" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/06/05/lagent-an-agent-framework-in-f-part-ii-agents-and-control-messages/" />
    <meta name="twitter:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    
restapi_import_id:
  - 5c011e0505e67
original_post_id:
  - "203"
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

## Agents

Agents are entities that process messages and keep state between one message and the next. As such they need to be initialized with a lambda that takes a message and a state and returns a new state. In F# pseudo code: msg –> state –> newState. For example the following:

<pre class="code"><span style="color:blue;">let </span>counter = spawnAgent (<span style="color:blue;">fun </span>msg state <span style="color:blue;">-&gt; </span>state + msg) 0</pre>

This is a counter that starts from 0 and gets incremented by the value of the received message. Let’s make it print something when it receives a message:

<pre class="code"><span style="color:blue;">let </span>counter1 = spawnAgent<br />                (<span style="color:blue;">fun </span>msg state <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"From %i to %i" </span>state (state + msg); state + msg) 0
counter1 &lt;-- 3
counter1 &lt;-- 4</pre>

Which produces:

> **From 0 to 3
        
>   
> From 3 to 7**

There is no _spawnParallelAgent_, because I couldn’t figure out its usage patterns. Maybe I don’t have enough creativity. Obviously _msg_ and _state_ could be of whatever type (in real application they end up being tuples more often than not).

## Control messages

You can do things to agents. I’m always adding to them but at this stage they are:

<pre class="code"><span style="color:blue;">type </span>Command =
| Restart
| Stop
| SetManager <span style="color:blue;">of </span>AsyncAgent
| SetName <span style="color:blue;">of </span>string</pre></p> 

Plus some others. I’ll describe most of them later on, right now I want to talk about _Restart_ and _Stop_. You use the former like this:

<pre class="code">counter1 &lt;-- Restart
counter1 &lt;-- 3</pre>

Which produces:

> **From 0 to 3**

This should be somehow surprising to you. You would have thought that you could just post integers to a counter. This is not the case. You can post whatever object. This is useful because it allows to have a common model for passing all sort of messages, it allows for the agent not to be parameterized by the type of the message (and of state) so that you can store them in data structures and allows advanced scenarios (i.e. hot swapping of code).

This is a debatable decision. I tried to get the best of strongly typing and dynamic typing, while keeping simplicity of usage. The implementation of this is kind of a mess though. We’ll get there.

BTW: you use Stop just by posting Stop, which stops the agent (forever).