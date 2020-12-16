---
id: 1085
title: 'LAgent: an agent framework in F# – Part VIII  - Implementing MapReduce (user model)'
date: 2009-09-04T13:57:48+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/09/04/lagent-an-agent-framework-in-f-part-viii-implementing-mapreduce-user-model/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/09/04/lagent-an-agent-framework-in-f-part-viii-implementing-mapreduce-user-model.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9891606"
orig_parent_id:
  - "9891606"
orig_thread_id:
  - "674761"
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
  - http://blogs.msdn.com/b/lucabol/archive/2009/09/04/lagent-an-agent-framework-in-f-part-viii-implementing-mapreduce-user-model.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="LAgent: an agent framework in F# &ndash; Part VIII  - Implementing MapReduce (user model)" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/09/04/lagent-an-agent-framework-in-f-part-viii-implementing-mapreduce-user-model/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="LAgent: an agent framework in F# &ndash; Part VIII  - Implementing MapReduce (user model)" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/09/04/lagent-an-agent-framework-in-f-part-viii-implementing-mapreduce-user-model/" />
    <meta name="twitter:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    
restapi_import_id:
  - 5c011e0505e67
original_post_id:
  - "143"
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



For this post I use a newer version of the framework that I just uploaded on CodeGallery. In the process of using LAgent I grew more and more unhappy with the weakly typed way of sending messages. The code that implements that feature is nasty: full of upcasts and downcasts. I was losing faith in it. Bugs were cropping up in all sorts of scenarios (i.e. using generic union types as messages).

In the end I decided to re-architecture the framework so to make it strongly typed. In essence now each agent can just receive messages of a single type. The limitations that this design choice introduces (i.e. more limited hot swapping) are compensated by the catching of errors at compile time and the streamlining of the code. I left the old framework on the site in case you disagree with me.

In any case, today’s post is about _MapReduce_. It assumes that you know what it is (link to the original Google paper that served as inspiration is here: [Google Research Publication- MapReduce](http://labs.google.com/papers/mapreduce.html "Google Research Publication- MapReduce")). What would it take to implement an in-memory _MapReduce_ using my agent framework?

Let’s start with the user model.

<pre class="code"><span style="color:blue;">let </span>mapReduce   (inputs:seq&lt;'in_key * 'in_value&gt;)
                (map:'in_key <span style="color:blue;">-&gt; </span>'in_value <span style="color:blue;">-&gt; </span>seq&lt;'out_key * 'out_value&gt;)
                (reduce:'out_key <span style="color:blue;">-&gt; </span>seq&lt;'out_value&gt; <span style="color:blue;">-&gt; </span>seq&lt;'reducedValues&gt;)
                outputAgent
                M R partitionF =                </pre>

_mapReduce_ takes seven parameters:

  1. <u>inputs</u>: a sequence of input key/value pairs. 
  2. <u>map</u>: this function operates on each input key/value pair. It&#160; returns a sequence of output key/value pairs. The type of the output sequence can be different from the type of the inputs. 
  3. <u>reduce</u>: this function operates on an output key and all the values associated with it. It returns a sequence of reduced values (i.e. the average of all the values for this key) 
  4. <u>ouputAgent</u>: this is the agent that gets notified every time a new output key has been reduced and at the end when all the operation ends. 
  5. <u>M</u>: how many mapper agents to instantiate 
  6. <u>R</u>: how many reducer agents to instantiate 
  7. <u>partitionF</u>: the partition function used to choose which of the reducers is associated with a key 

Let’s look at how to use this function to find how often each word is used in a set of files. First a simple partition function can be defined as:

<pre class="code"><span style="color:blue;">let </span>partitionF = <span style="color:blue;">fun </span>key M <span style="color:blue;">-&gt; </span>abs(key.GetHashCode()) % M </pre>

Given a key and some buckets, it picks one of the buckets. Its type is: ‘a –> int –> int, so it’s fairly reusable.

Let’s also create a basic agent that just prints out the reduced values:

<pre class="code"><span style="color:blue;">let </span>printer = spawnWorker (<span style="color:blue;">fun </span>msg <span style="color:blue;">-&gt;
                            match </span>msg <span style="color:blue;">with
                            </span>| Reduced(key, value)   <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"%A %A" </span>key value
                            | MapReduceDone         <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"All done!!"</span>)</pre>

The agent gets notified whenever a new key is reduced or the algorithm ends. It is useful to be notified immediately instead of waiting for everything to be done. If I hadn’t written this code using agents I would have not realized that possibility. I would simply have framed the problem as a function that takes an input and returns an output. Agents force you to think explicitly about the parallelism in your app. That’s a good thing.

The mapping function simply split the content of a file into words and adds a word/1 pair to the list. I know that there are much better ways to do this (i.e. regular expressions for the parsing and summing words counts inside the function), but I wanted to test the basic framework capabilities and doing it this way does it better.

<pre class="code"><span style="color:blue;">let </span>map = <span style="color:blue;">fun </span>(fileName:string) (fileContent:string) <span style="color:blue;">-&gt;
            let </span>l = <span style="color:blue;">new </span>List&lt;string * int&gt;()
            <span style="color:blue;">let </span>wordDelims = [|<span style="color:maroon;">' '</span>;<span style="color:maroon;">','</span>;<span style="color:maroon;">';'</span>;<span style="color:maroon;">'.'</span>;<span style="color:maroon;">':'</span>;<span style="color:maroon;">'?'</span>;<span style="color:maroon;">'!'</span>;<span style="color:maroon;">'('</span>;<span style="color:maroon;">')'</span>;<span style="color:maroon;">'n'</span>;<span style="color:maroon;">'t'</span>;<span style="color:maroon;">'f'</span>;<span style="color:maroon;">'r'</span>;<span style="color:maroon;">'b'</span>|]
            fileContent.Split(wordDelims) |&gt; Seq.iter (<span style="color:blue;">fun </span>word <span style="color:blue;">-&gt; </span>l.Add((word, <span style="color:brown;">1</span>)))
            l :&gt; seq&lt;string * int&gt;</pre>



The reducer function simply sums the various word statistics sent by the mappers:

<pre class="code"><span style="color:blue;">let </span>reduce = <span style="color:blue;">fun </span>key (values:seq&lt;int&gt;) <span style="color:blue;">-&gt; </span>[values |&gt; Seq.sum] |&gt; seq&lt;int&gt;</pre>

Now we can create some fake input to check that it works:

<pre class="code"><span style="color:blue;">let </span>testInput = [<span style="color:maroon;">"File1"</span>, <span style="color:maroon;">"I was going to the airport when I saw someone crossing"</span>;<br />                               <span style="color:maroon;">"File2"</span>, <span style="color:maroon;">"I was going home when I saw you coming toward me"</span>]   </pre>

And execute the _mapReduce_:

<pre class="code">mapReduce testInput map reduce printer <span style="color:brown;">2 2 </span>partitionF</pre>

On my machine I get the following. You might get a different order because of the async/parallel processing involved. If I wanted a stable order I would need to change the _printer_ agent to cache results on _Reduced_ and process them on _MapReduceDone_ (see next post).

"I" [4]
    
  
"crossing" [1]
    
  
"going" [2]
    
  
"home" [1]
    
  
"me" [1]
    
  
"the" [1]
    
  
"toward" [1]
    
  
"airport" [1]
    
  
"coming" [1]
    
  
"saw" [2]
    
  
"someone" [1]
    
  
"to" [1]
    
  
"was" [2]
    
  
"when" [2]
    
  
"you" [1]

In the next post we’ll process some real books …