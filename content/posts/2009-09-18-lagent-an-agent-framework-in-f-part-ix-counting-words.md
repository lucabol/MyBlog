---
id: 1084
title: 'LAgent: an agent framework in F# – Part IX – Counting words …'
date: 2009-09-18T14:43:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/09/18/lagent-an-agent-framework-in-f-part-ix-counting-words/
permalink: /2009/09/18/lagent-an-agent-framework-in-f-part-ix-counting-words/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/09/18/lagent-an-agent-framework-in-f-part-ix-counting-words.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9895168"
orig_parent_id:
  - "9895168"
orig_thread_id:
  - "676204"
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
  - http://blogs.msdn.com/b/lucabol/archive/2009/09/18/lagent-an-agent-framework-in-f-part-ix-counting-words.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="LAgent: an agent framework in F# &ndash; Part IX &ndash; Counting words &hellip;" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/09/18/lagent-an-agent-framework-in-f-part-ix-counting-words/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="LAgent: an agent framework in F# &ndash; Part IX &ndash; Counting words &hellip;" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/09/18/lagent-an-agent-framework-in-f-part-ix-counting-words/" />
    <meta name="twitter:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    
restapi_import_id:
  - 5c011e0505e67
original_post_id:
  - "133"
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



Let’s now use our mapReduce to do something more interesting, for example finding the frequency of words in several books. Now the agent that processes the output needs to be a bit more complex.

<pre class="code"><span style="color:blue;">let </span>gathererF = <span style="color:blue;">fun </span>msg (data:List&lt;string * int&gt;, counter, step) <span style="color:blue;">-&gt;
                    match </span>msg <span style="color:blue;">with
                    </span>| Reduced(key, value)   <span style="color:blue;">-&gt;
                        if </span>counter % step = <span style="color:brown;">0 </span><span style="color:blue;">then
                            </span>printfn <span style="color:maroon;">"Processed %i words. Now processing %s" </span>counter key
                        data.Add((key, value |&gt; Seq.hd))
                        data, counter + <span style="color:brown;">1</span>, step
                    | MapReduceDone         <span style="color:blue;">-&gt;
                        </span>data
                        |&gt; Seq.distinctBy (<span style="color:blue;">fun </span>(key, _) <span style="color:blue;">-&gt; </span>key.ToLower())
                        |&gt; Seq.filter (<span style="color:blue;">fun </span>(key, _) <span style="color:blue;">-&gt; </span>not(key = <span style="color:maroon;">"" </span>|| key = <span style="color:maroon;">""" </span>||<br />                                                             (fst (Double.TryParse(key)))))
                        |&gt; Seq.to_array
                        |&gt; Array.sortBy snd
                        |&gt; Array.rev
                        |&gt; Seq.take <span style="color:brown;">20
                        </span>|&gt; Seq.iter (<span style="color:blue;">fun </span>(key, value) <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"%Att%A" </span>key value)
                        printfn <span style="color:maroon;">"All done!!"
                        </span>data, counter, step
<span style="color:blue;">let </span>gatherer = spawnAgent gathererF (<span style="color:blue;">new </span>List&lt;string * int&gt;(), <span style="color:brown;"></span>, <span style="color:brown;">1000</span>)</pre>



Every time a new word is reduced, a message is printed out and the result is added to a running list. When everything is done such a list is printed out by first manipulating it to reduce weirdness and limit the number of items. BTW: there are at least two bugs in this code, maybe more (late night quick-and-dirty-see-if-the-algo-works kind of coding).

We want to maximize the number of processors to use, so let’s split the books in chunks so that they can be operated in parallel. The code below roughly does it (I say roughly because it doesn’t chunk the lines in the right order, but for this particular case it doesn’t matter).

<pre class="code"><span style="color:blue;">let </span>gatherer = spawnAgent gathererF (<span style="color:blue;">new </span>List&lt;string * int&gt;(), <span style="color:brown;"></span>, <span style="color:brown;">1000</span>)
<span style="color:blue;">let </span>splitBook howManyBlocks fileName =
    <span style="color:blue;">let </span>buffers = Array.init howManyBlocks (<span style="color:blue;">fun </span>_ <span style="color:blue;">-&gt; new </span>StringBuilder())
    fileName
    |&gt; File.ReadAllLines
    |&gt; Array.iteri (<span style="color:blue;">fun </span>i line <span style="color:blue;">-&gt; </span>buffers.[i % (howManyBlocks)].Append(line) |&gt; ignore)
    buffers
<span style="color:blue;">let </span>blocks1 = <span style="color:maroon;">"C:UserslucabolDesktopAgentsAgentskjv10.txt" </span>|&gt; splitBook <span style="color:brown;">100
</span><span style="color:blue;">let </span>blocks2 = <span style="color:maroon;">"C:UserslucabolDesktopAgentsAgentswarandpeace.txt" </span>|&gt; splitBook <span style="color:brown;">100
</span><span style="color:blue;">let </span>input =
    blocks1
    |&gt; Array.append blocks2
    |&gt; Array.mapi (<span style="color:blue;">fun </span>i b <span style="color:blue;">-&gt; </span>i.ToString(), b.ToString())</pre>

And let’s execute!!

<pre class="code">mapReduce input map reduce gatherer <span style="color:brown;">20 20 </span>partitionF</pre>

On my machine I get the following, which could be the right result.

<pre class="code">"a"        16147
"And"        13071
"I"        11349
"unto"        8125
"as"        6400
"her"        5865
"which"        5544
"from"        5378
"at"        5175
"on"        5155
"have"        5135
"me"        5068
"my"        4629
"this"        3782
"out"        3653
"ye"        3399
"when"        3312
"an"        2841
"upon"        2558
"so"        2489
All done!!</pre>

