---
id: 173
title: 'LAgent: an agent framework in F# – Part V – Timeout management'
date: 2009-06-26T14:56:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/06/26/lagent-an-agent-framework-in-f-part-v-timeout-management/
permalink: /2009/06/26/lagent-an-agent-framework-in-f-part-v-timeout-management/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/06/26/lagent-an-agent-framework-in-f-part-v-timeout-management.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9649246"
orig_parent_id:
  - "9649246"
orig_thread_id:
  - "657936"
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
  - http://blogs.msdn.com/b/lucabol/archive/2009/06/26/lagent-an-agent-framework-in-f-part-v-timeout-management.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="LAgent: an agent framework in F# &ndash; Part V &ndash; Timeout management" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/06/26/lagent-an-agent-framework-in-f-part-v-timeout-management/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="LAgent: an agent framework in F# &ndash; Part V &ndash; Timeout management" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/06/26/lagent-an-agent-framework-in-f-part-v-timeout-management/" />
    <meta name="twitter:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - 'F#'
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

#### Timeout management

Timeouts are very important in message based systems. In essence, if you are not getting messages for a certain period of time, that usually means something. It might be that something crashed, that other agents think that you are not online, or any other number of things. Hence the need to set timeouts and react when they are triggered.

You do that by writing the following:

<pre class="code">counter1 &lt;--SetTimeoutHandler 1000 <br />            (<span style="color:blue;">fun </span>state <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"I'm still waiting for a message in state %A, come on ..." <br />                                                            </span>state; ContinueProcessing(state))              </pre>

Which generates the following message every second:

> **I'm still waiting for a message in state 2, come on
        
>   
> I'm still waiting for a message in state 2, come on .…**

The first parameter to _SetTimeoutHandler_ is how long to wait before triggering the handler. The second parameter is the handler that gets called whenever no message is received for that amount of time. Notice that the handler takes the current state of the agent and returns _ContinueProcessing(state)_.&#160; This tells the agent to continue processing messages and sets the current state to _state_.

The following code:

<pre class="code">counter1 &lt;-- 2</pre>

Then generates:

> **I'm still waiting for a message in state 4, come on
        
>   
> I'm still waiting for a message in state 4, come on**

_ContinueProcessing_ is just one of the three possible values of the (terribly named) _AfterError_:

<pre class="code"><span style="color:blue;">type </span>AfterError =
| ContinueProcessing <span style="color:blue;">of </span>obj
| StopProcessing
| RestartProcessing</pre>

Let’s see what RestartProcessing does.

<pre class="code">counter1 &lt;-- SetTimeoutHandler 1000  (<span style="color:blue;">fun </span>state <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"Restart from state %A" </span>state<br />                                                                        ; RestartProcessing)</pre>

Which, as expected, generates a nice stream of:

> **Restart from state 0
        
>   
> Restart from state 0**

To bring things back to normal (aka no timeout) you can just pass –1 as in:

<pre class="code">counter1 &lt;-- SetTimeoutHandler -1  (<span style="color:blue;">fun </span>state <span style="color:blue;">-&gt; </span>ContinueProcessing(state))</pre>

Also, you can stop the agent when a timeout occurs by returning the aptly named _StopProcessing_:

<pre class="code">counter1 &lt;-- SetTimeoutHandler 1000  (<span style="color:blue;">fun </span>state <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"Restart from state %A" </span>state; <br />                                                                             StopProcessing)</pre>

Another interesting thing you might want to do is hot swapping of code. More on that in the next part …