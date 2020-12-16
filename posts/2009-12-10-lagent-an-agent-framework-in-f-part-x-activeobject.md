---
id: 1080
title: 'LAgent: an agent framework in F# – Part X – ActiveObject'
date: 2009-12-10T10:09:14+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/12/10/lagent-an-agent-framework-in-f-part-x-activeobject/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/12/10/lagent-an-agent-framework-in-f-part-x-activeobject.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9935251"
orig_parent_id:
  - "9935251"
orig_thread_id:
  - "691559"
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
  - http://blogs.msdn.com/b/lucabol/archive/2009/12/10/lagent-an-agent-framework-in-f-part-x-activeobject.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="LAgent: an agent framework in F# &ndash; Part X &ndash; ActiveObject" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/12/10/lagent-an-agent-framework-in-f-part-x-activeobject/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="LAgent: an agent framework in F# &ndash; Part X &ndash; ActiveObject" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/12/10/lagent-an-agent-framework-in-f-part-x-activeobject/" />
    <meta name="twitter:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    
restapi_import_id:
  - 5c011e0505e67
original_post_id:
  - "83"
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

If you stare long enough at agents, you start to realize that they are just ‘glorified locks’. They are a convenient programming model to protect a resource from concurrent access. The programming model is convenient because both the client and the server can write their code without worrying about concurrency problems, and yet the program runs in parallel. Protecting a resource sounds a lot like state encapsulation and the concept of state encapsulation is what object orientation is all about.

So you start thinking if there is a way to enhance vanilla objects to make them agents. You want to reuse all the concepts that you are familiar with (i.e. inheritance, visibility rules, etc…) and you want your clients to call agents as if they were calling normal objects. Obviously, under the cover, the method calls won’t execute immediately, but they would be queued. Let’s look at an example.

This is our simple counter agent:

<pre class="code"><span style="color:blue;">type </span>CounterMessage =
| Add <span style="color:blue;">of </span>int
| Print
<span style="color:blue;">let </span>counterF = <span style="color:blue;">fun </span>msg count <span style="color:blue;">-&gt;
    match </span>msg <span style="color:blue;">with
    </span>| Add(i)    <span style="color:blue;">-&gt; </span>count + i
    | Print     <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"The value is %i" </span>count; count
<span style="color:blue;">let </span>c1 = spawnAgent counterF <span style="color:brown;">0
</span>c1 &lt;-- Add(<span style="color:brown;">3</span>)
c1 &lt;—Print</pre>

As nice as this looks, there are unfamiliar things in this model:

  1. The communication is through messages. This requires packing and unpacking which, albeit easy in F#, is unfamiliar and feels like machinery that we’d like to get rid off. 
  2. The management of state is bizarre, it gets passed into the lambda and returned from it instead of being represented as fields and properties on the agent 

My best attempt at creating an object-like syntax follows:

<pre class="code"><span style="color:blue;">type </span>Counter() =
    <span style="color:blue;">let </span>w = <span style="color:blue;">new </span>WorkQueue()
    <span style="color:blue;">let mutable </span>count = <span style="color:brown;">0
    </span><span style="color:blue;">member </span>c.Add x = w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
        </span>count &lt;- count + x
        )
    <span style="color:blue;">member </span>c.Print () = w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
        </span>printfn <span style="color:maroon;">"The value is %i" </span>count
        )</pre>

<pre class="code"><span style="color:blue;">let </span>c = <span style="color:blue;">new </span>Counter()
c.Add <span style="color:brown;">3
</span>c.Print</pre>

With this syntax, you write your agents like you write your vanilla classes except:

  1. You need a private field of type _WorkQueue_ 
  2. You need to write your methods as lambdas passed to the _WorkQueue.Queue_ function 
  3. Your methods cannot return values 

The most worrisome of these constraints is 2. because you can easily forget about it. If you do forget, then everything compiles just fine, but it doesn’t do what you expect. That’s pure badness. I haven’t found a way to enforce it. This is a place where the language could help me. Other than that, the whole model works rather nicely.

Regarding the third point, you can concoct a programming model that allows you to return values from your methods. Here it is:

<pre class="code"><span style="color:blue;">member </span>c.CountTask = w.QueueWithTask(<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
    </span>count
    )
<span style="color:blue;">member </span>c.CountAsync = w.QueueWithAsync(<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
    </span>count
    )</pre>

<pre class="code">printfn <span style="color:maroon;">"The count using Task is %i" </span>(c.CountTask.Result)</pre>

The first method returns a _Task;_ the second method returns an _AsyncResultCell_. Both are ways to represent a [promise](http://en.wikipedia.org/wiki/Future_(programming)). The latter allows a natural integration with the async block in F# as in the following code:

<pre class="code">Async.RunSynchronously (
            async {
                <span style="color:blue;">let! </span>count = c.CountAsync
                printfn <span style="color:maroon;">"The countusing Async is %i" </span>count
            })</pre>



As for myself, I don’t like methods returning values. Every time I use them, I end up going back and thinking about my problem in a traditional way, aka as method calls that return results, instead of thinking about it in a more actor oriented fashion. I end up waiting for these promises to be materialized and, by doing so, I limit the amount of parallelism that I unleash. As a matter of fact, the whole business of hiding the message passing nature of the programming model is dubious. It makes for a nicer syntax, but you need to make an extra effort in your mind to translate it to what it really is: just message passing with a nice syntactical veneer. I haven’t decided yet which model I like the most.

You should have a sense of what _WorkQueue_ is. In essence, it is a _Mailbox_ of lambdas (look at the red bold code below). 

<pre class="code"><span style="color:blue;">type </span>WorkQueue() =
    <font color="#ff0000"><strong><span style="color:blue;">let </span>workQueue = spawnWorker (<span style="color:blue;">fun </span>f <span style="color:blue;">-&gt; </span>f())</strong></font>
    <span style="color:blue;">member </span>w.Queue (f) = workQueue &lt;-- f
    <span style="color:blue;">member </span>w.QueueWithTask f : Task&lt;'T&gt; =
        <span style="color:blue;">let </span>source = <span style="color:blue;">new </span>TaskCompletionSource&lt;_&gt;()
        workQueue &lt;-- (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt; </span>f() |&gt; source.SetResult)
        source.Task
    <span style="color:blue;">member </span>w.QueueWithAsync (f:unit <span style="color:blue;">-&gt; </span>'T) : Async&lt;'T&gt; =
        <span style="color:blue;">let </span>result = <span style="color:blue;">new </span>AsyncResultCell&lt;'T&gt;()
        workQueue &lt;-- (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt; </span>f() |&gt; result.RegisterResult )
        result.AsyncWaitResult
    <span style="color:blue;">member </span>w.Restart () = workQueue &lt;-! Restart
    <span style="color:blue;">member </span>w.Stop () = workQueue &lt;-! Stop
    <span style="color:blue;">member </span>w.SetErrorHandler(h) =
        <span style="color:blue;">let </span>managerF = <span style="color:blue;">fun </span>(_, name:string, ex:Exception, _, _, _) <span style="color:blue;">-&gt; </span>h name ex
        <span style="color:blue;">let </span>manager = spawnWorker managerF
        workQueue &lt;-! SetManager manager
    <span style="color:blue;">member </span>w.SetName(name) = workQueue &lt;-! SetName(name)
    <span style="color:blue;">member </span>w.SetQueueHandler(g) = workQueue &lt;-! SetWorkerHandler(g)
    <span style="color:blue;">member </span>w.SetTimeoutHandler(timeout, f) = workQueue &lt;-! SetTimeoutHandler(timeout, f)</pre>

I implemented all the services that are in the message passing model. The two are equivalent as expressing power goes. In case you wonder how a real piece of code looks like using this model, here is an _ActiveObject_ version of the map reduce algorithm. One of these days, I will gather the strength to go trough this code and explain what it does, but not today 🙂

<pre class="code"><span style="color:blue;">#load </span><span style="color:maroon;">"AgentSystem.fs"
</span><span style="color:blue;">open </span>AgentSystem.LAgent
<span style="color:blue;">open </span>System
<span style="color:blue;">open </span>System.Collections
<span style="color:blue;">open </span>System.Collections.Generic
<span style="color:blue;">open </span>System.Threading
<span style="color:blue;">type </span>IOutput&lt;'out_key, 'out_value&gt; =
    <span style="color:blue;">abstract </span>Reduced: 'out_key <span style="color:blue;">-&gt; </span>seq&lt;'out_value&gt; <span style="color:blue;">-&gt; </span>unit
    <span style="color:blue;">abstract </span>MapReduceDone: unit <span style="color:blue;">-&gt; </span>unit
<span style="color:blue;">type </span>Mapper&lt;'in_key, 'in_value, 'my_out_key, 'out_value <span style="color:blue;">when </span>'my_out_key : comparison&gt;<br />                                                      (map:'in_key <span style="color:blue;">-&gt; </span>'in_value <span style="color:blue;">-&gt; </span>seq&lt;'my_out_key * 'out_value&gt;, i, partitionF) =
    <span style="color:blue;">let </span>w = <span style="color:blue;">new </span>WorkQueue()
    <span style="color:blue;">let mutable </span>reducerTracker: BitArray = <span style="color:blue;">null
    let mutable </span>controller = Unchecked.defaultof&lt;Controller&lt;'in_key, 'in_value, 'my_out_key, 'out_value&gt;&gt;
    <span style="color:blue;">let mutable </span>reducers = Unchecked.defaultof&lt;Reducer&lt;'in_key, 'in_value, 'my_out_key, 'out_value&gt; array&gt;
    <span style="color:blue;">member </span>m.Init c reds =
        w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
            </span>controller &lt;- c
            reducers &lt;- reds
            reducerTracker &lt;- <span style="color:blue;">new </span>BitArray(reducers.Length, <span style="color:blue;">false</span>))
    <span style="color:blue;">member </span>m.Process inKey inValue =
        w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
            let </span>outKeyValues = map inKey inValue
            outKeyValues |&gt; Seq.iter (<span style="color:blue;">fun </span>(outKey, outValue) <span style="color:blue;">-&gt;
                                        let </span>reducerUsed = partitionF outKey (reducers.Length)
                                        reducerTracker.Set(reducerUsed, <span style="color:blue;">true</span>)
                                        reducers.[reducerUsed].Add(outKey, outValue)))
    <span style="color:blue;">member </span>m.Done () =
        w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
            </span>controller.MapDone i reducerTracker)
    <span style="color:blue;">member </span>m.Stop () = w.Stop ()
<span style="color:blue;">and </span>Reducer&lt;'in_key, 'in_value, 'out_key, 'out_value <span style="color:blue;">when </span>'out_key :<br />                     comparison&gt;(reduce:'out_key <span style="color:blue;">-&gt; </span>seq&lt;'out_value&gt; <span style="color:blue;">-&gt; </span>seq&lt;'out_value&gt;, i, output:IOutput&lt;'out_key, 'out_value&gt;) =
    <span style="color:blue;">let </span>w = <span style="color:blue;">new </span>WorkQueue()
    <span style="color:blue;">let mutable </span>workItems = <span style="color:blue;">new </span>List&lt;'out_key * 'out_value&gt;()
    <span style="color:blue;">let mutable </span>controller = Unchecked.defaultof&lt;Controller&lt;'in_key, 'in_value, 'out_key, 'out_value&gt;&gt;
    <span style="color:blue;">member </span>r.Init c =
        w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
            </span>controller &lt;- c)
    <span style="color:blue;">member </span>r.StartReduction () =
        w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
            </span>workItems
            |&gt; Seq.groupBy fst
            |&gt; Seq.sortBy fst
            |&gt; Seq.map (<span style="color:blue;">fun </span>(key, values) <span style="color:blue;">-&gt; </span>(key, reduce key (values |&gt; Seq.map snd)))
            |&gt; Seq.iter (<span style="color:blue;">fun </span>(key, value) <span style="color:blue;">-&gt; </span>output.Reduced key value)
            controller.ReductionDone i)
    <span style="color:blue;">member </span>r.Add (outKey:'out_key, outValue:'out_value) : unit =
        w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
            </span>workItems.Add((outKey, outValue)))
    <span style="color:blue;">member </span>m.Stop () = w.Stop ()
<span style="color:blue;">and </span>Controller&lt;'in_key, 'in_value, 'out_key, 'out_value <span style="color:blue;">when </span>'out_key : comparison&gt;(output:IOutput&lt;'out_key, 'out_value&gt;) =
    <span style="color:blue;">let </span>w = <span style="color:blue;">new </span>WorkQueue()
    <span style="color:blue;">let mutable </span>mapperTracker: BitArray = <span style="color:blue;">null
    let mutable </span>reducerUsedByMappers: BitArray = <span style="color:blue;">null
    let mutable </span>reducerDone: BitArray = <span style="color:blue;">null
    let mutable </span>mappers = Unchecked.defaultof&lt;Mapper&lt;'in_key, 'in_value, 'out_key, 'out_value&gt; array&gt;
    <span style="color:blue;">let mutable </span>reducers = Unchecked.defaultof&lt;Reducer&lt;'in_key, 'in_value, 'out_key, 'out_value&gt; array&gt;
    <span style="color:blue;">let </span>BAtoSeq (b:BitArray) = [<span style="color:blue;">for </span>x <span style="color:blue;">in </span>b <span style="color:blue;">do yield </span>x]
    <span style="color:blue;">member </span>c.Init maps reds =
        w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
            </span>mappers &lt;- maps
            reducers &lt;- reds
            mapperTracker &lt;- <span style="color:blue;">new </span>BitArray(mappers.Length, <span style="color:blue;">false</span>)
            reducerUsedByMappers &lt;- <span style="color:blue;">new </span>BitArray(reducers.Length, <span style="color:blue;">false</span>)
            reducerDone &lt;- <span style="color:blue;">new </span>BitArray(reducers.Length, <span style="color:blue;">false</span>))
    <span style="color:blue;">member </span>c.MapDone (i : int) (reducerTracker : BitArray) : unit =
        w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
            </span>mapperTracker.Set(i, <span style="color:blue;">true</span>)
            <span style="color:blue;">let </span>reducerUsedByMappers = reducerUsedByMappers.Or(reducerTracker)
            <span style="color:blue;">if </span>not( BAtoSeq mapperTracker |&gt; Seq.exists(<span style="color:blue;">fun </span>bit <span style="color:blue;">-&gt; </span>bit = <span style="color:blue;">false</span>)) <span style="color:blue;">then
                </span>BAtoSeq reducerUsedByMappers |&gt; Seq.iteri (<span style="color:blue;">fun </span>i r <span style="color:blue;">-&gt; if </span>r = <span style="color:blue;">true then </span>reducers.[i].StartReduction ())
                mappers |&gt; Seq.iter (<span style="color:blue;">fun </span>m <span style="color:blue;">-&gt; </span>m.Stop ())
              )
    <span style="color:blue;">member </span>c.ReductionDone (i: int) : unit =
        w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
            </span>reducerDone.Set(i, <span style="color:blue;">true</span>)
            <span style="color:blue;">if </span>BAtoSeq reducerDone |&gt; Seq.forall2 (<span style="color:blue;">fun </span>x y <span style="color:blue;">-&gt; </span>x = y) (BAtoSeq reducerUsedByMappers) <span style="color:blue;">then
                </span>output.MapReduceDone ()
                reducers |&gt; Seq.iter (<span style="color:blue;">fun </span>r <span style="color:blue;">-&gt; </span>r.Stop ())
                c.Stop()
             )
    <span style="color:blue;">member </span>m.Stop () = w.Stop ()
<span style="color:blue;">let </span>mapReduce   (inputs:seq&lt;'in_key * 'in_value&gt;)
                (map:'in_key <span style="color:blue;">-&gt; </span>'in_value <span style="color:blue;">-&gt; </span>seq&lt;'out_key * 'out_value&gt;)
                (reduce:'out_key <span style="color:blue;">-&gt; </span>seq&lt;'out_value&gt; <span style="color:blue;">-&gt; </span>seq&lt;'out_value&gt;)
                (output:IOutput&lt;'out_key, 'out_value&gt;)
                M R partitionF =
    <span style="color:blue;">let </span>len = inputs |&gt; Seq.length
    <span style="color:blue;">let </span>M = <span style="color:blue;">if </span>len &lt; M <span style="color:blue;">then </span>len <span style="color:blue;">else </span>M
    <span style="color:blue;">let </span>mappers = Array.init M (<span style="color:blue;">fun </span>i <span style="color:blue;">-&gt; new </span>Mapper&lt;'in_key, 'in_value, 'out_key, 'out_value&gt;(map, i, partitionF))
    <span style="color:blue;">let </span>reducers = Array.init R (<span style="color:blue;">fun </span>i <span style="color:blue;">-&gt; new </span>Reducer&lt;'in_key, 'in_value, 'out_key, 'out_value&gt;(reduce, i, output))
    <span style="color:blue;">let </span>controller = <span style="color:blue;">new </span>Controller&lt;'in_key, 'in_value, 'out_key, 'out_value&gt;(output)
    mappers |&gt; Array.iter (<span style="color:blue;">fun </span>m <span style="color:blue;">-&gt; </span>m.Init controller reducers)
    reducers |&gt; Array.iter (<span style="color:blue;">fun </span>r <span style="color:blue;">-&gt; </span>r. Init controller )
    controller.Init mappers reducers
    inputs |&gt; Seq.iteri (<span style="color:blue;">fun </span>i (inKey, inValue) <span style="color:blue;">-&gt; </span>mappers.[i % M].Process inKey inValue)
    mappers |&gt; Seq.iter (<span style="color:blue;">fun </span>m <span style="color:blue;">-&gt; </span>m.Done ())
<span style="color:blue;">let </span>partitionF = <span style="color:blue;">fun </span>key M <span style="color:blue;">-&gt; </span>abs(key.GetHashCode()) % M
<span style="color:blue;">let </span>map = <span style="color:blue;">fun </span>(fileName:string) (fileContent:string) <span style="color:blue;">-&gt;
            let </span>l = <span style="color:blue;">new </span>List&lt;string * int&gt;()
            <span style="color:blue;">let </span>wordDelims = [|<span style="color:maroon;">' '</span>;<span style="color:maroon;">','</span>;<span style="color:maroon;">';'</span>;<span style="color:maroon;">'.'</span>;<span style="color:maroon;">':'</span>;<span style="color:maroon;">'?'</span>;<span style="color:maroon;">'!'</span>;<span style="color:maroon;">'('</span>;<span style="color:maroon;">')'</span>;<span style="color:maroon;">'n'</span>;<span style="color:maroon;">'t'</span>;<span style="color:maroon;">'f'</span>;<span style="color:maroon;">'r'</span>;<span style="color:maroon;">'b'</span>|]
            fileContent.Split(wordDelims) |&gt; Seq.iter (<span style="color:blue;">fun </span>word <span style="color:blue;">-&gt; </span>l.Add((word, <span style="color:brown;">1</span>)))
            l :&gt; seq&lt;string * int&gt;
<span style="color:blue;">let </span>reduce = <span style="color:blue;">fun </span>key (values:seq&lt;int&gt;) <span style="color:blue;">-&gt; </span>[values |&gt; Seq.sum] |&gt; seq&lt;int&gt;
<span style="color:blue;">let </span>printer () =
  { <span style="color:blue;">new </span>IOutput&lt;string, int&gt; <span style="color:blue;">with
        member </span>o.Reduced key values = printfn <span style="color:maroon;">"%A %A" </span>key values
        <span style="color:blue;">member </span>o.MapReduceDone () = printfn <span style="color:maroon;">"All done!!"</span>}
<span style="color:blue;">let </span>testInput =<br />     [<span style="color:maroon;">"File1"</span>, <span style="color:maroon;">"I was going to the airport when I saw someone crossing"</span>; <span style="color:maroon;">"File2"</span>, <span style="color:maroon;">"I was going home when I saw you coming toward me"</span>]
mapReduce testInput map reduce (printer ()) <span style="color:brown;">2 2 </span>partitionF
<span style="color:blue;">open </span>System.IO
<span style="color:blue;">open </span>System.Text
<span style="color:blue;">let </span>gatherer(step) =
  <span style="color:blue;">let </span>w = <span style="color:blue;">new </span>WorkQueue()
  <span style="color:blue;">let </span>data = <span style="color:blue;">new </span>List&lt;string * int&gt;()
  <span style="color:blue;">let </span>counter = ref <span style="color:brown;">0
  </span>{ <span style="color:blue;">new </span>IOutput&lt;string, int&gt; <span style="color:blue;">with
        member </span>o.Reduced key values =
            w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
                if </span>!counter % step = <span style="color:brown;">0 </span><span style="color:blue;">then
                    </span>printfn <span style="color:maroon;">"Processed %i words. Now processing %s" </span>!counter key
                data.Add((key, values |&gt; Seq.hd))
                counter := !counter + <span style="color:brown;">1</span>)
        <span style="color:blue;">member </span>o.MapReduceDone () =
            w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
                </span>data
                |&gt; Seq.distinctBy (<span style="color:blue;">fun </span>(key, _) <span style="color:blue;">-&gt; </span>key.ToLower())
                |&gt; Seq.filter (<span style="color:blue;">fun </span>(key, _) <span style="color:blue;">-&gt; </span>not(key = <span style="color:maroon;">"" </span>|| key = <span style="color:maroon;">""" </span>|| (fst (Double.TryParse(key)))))
                |&gt; Seq.to_array
                |&gt; Array.sortBy snd
                |&gt; Array.rev
                |&gt; Seq.take <span style="color:brown;">20
                </span>|&gt; Seq.iter (<span style="color:blue;">fun </span>(key, value) <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"%Att%A" </span>key value)
                printfn <span style="color:maroon;">"All done!!"</span>)
        }
<span style="color:blue;">let </span>splitBook howManyBlocks fileName =
    <span style="color:blue;">let </span>buffers = Array.init howManyBlocks (<span style="color:blue;">fun </span>_ <span style="color:blue;">-&gt; new </span>StringBuilder())
    fileName
    |&gt; File.ReadAllLines
    |&gt; Array.iteri (<span style="color:blue;">fun </span>i line <span style="color:blue;">-&gt; </span>buffers.[i % (howManyBlocks)].Append(line) |&gt; ignore)
    buffers
<span style="color:blue;">let </span>blocks1 = <span style="color:blue;">__SOURCE_DIRECTORY__ </span>+ <span style="color:maroon;">"kjv10.txt" </span>|&gt; splitBook <span style="color:brown;">100
</span><span style="color:blue;">let </span>blocks2 = <span style="color:blue;">__SOURCE_DIRECTORY__ </span>+ <span style="color:maroon;">"warandpeace.txt" </span>|&gt; splitBook <span style="color:brown;">100
</span><span style="color:blue;">let </span>input =
    blocks1
    |&gt; Array.append blocks2
    |&gt; Array.mapi (<span style="color:blue;">fun </span>i b <span style="color:blue;">-&gt; </span>i.ToString(), b.ToString())
<span style="color:green;">//mapReduce input map reduce (gatherer(1000)) 20 20 partitionF
</span><span style="color:blue;">type </span>BookSplitter () =
    <span style="color:blue;">let </span>blocks = <span style="color:blue;">new </span>List&lt;string * string&gt;()
    <span style="color:blue;">member </span>b.Split howManyBlocks fileName =
            <span style="color:blue;">let </span>b =
                fileName
                |&gt; splitBook howManyBlocks
                |&gt; Array.mapi (<span style="color:blue;">fun </span>i b <span style="color:blue;">-&gt; </span>i.ToString(), b.ToString())
            blocks.AddRange(b)
    <span style="color:blue;">member </span>b.Blocks () =
            blocks.ToArray() :&gt; seq&lt;string * string&gt;
<span style="color:blue;">type </span>WordCounter () =
    <span style="color:blue;">let </span>w = <span style="color:blue;">new </span>WorkQueue()
    <span style="color:blue;">let </span>words = <span style="color:blue;">new </span>Dictionary&lt;string,int&gt;()
    <span style="color:blue;">let </span>worker(wordCounter:WordCounter, ev:EventWaitHandle) =
          <span style="color:blue;">let </span>w1 = <span style="color:blue;">new </span>WorkQueue()
          { <span style="color:blue;">new </span>IOutput&lt;string, int&gt; <span style="color:blue;">with
                member </span>o.Reduced key values =
                    w1.Queue (<span style="color:blue;">fun</span>() <span style="color:blue;">-&gt;
                        </span>wordCounter.AddWord key (values |&gt; Seq.hd))
                <span style="color:blue;">member </span>o.MapReduceDone () =
                    w1.Queue(<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
                        </span>ev.Set() |&gt; ignore)
           }
    <span style="color:blue;">member </span>c.AddWord word count =
            <span style="color:blue;">let </span>exist, value = words.TryGetValue(word)
            <span style="color:blue;">if </span>exist <span style="color:blue;">then
                </span>words.[word] &lt;- value + count
            <span style="color:blue;">else
                </span>words.Add(word, count)
    <span style="color:blue;">member </span>c.Add fileName =
        w.Queue (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
            let </span>s = <span style="color:blue;">new </span>BookSplitter()
            fileName |&gt; s.Split <span style="color:brown;">100
            </span><span style="color:blue;">let </span>ev = <span style="color:blue;">new </span>EventWaitHandle(<span style="color:blue;">false</span>, EventResetMode.AutoReset)
            <span style="color:blue;">let </span>blocks = s.Blocks ()
            mapReduce blocks map reduce (worker(c, ev)) <span style="color:brown;">20 20 </span>partitionF
            ev.WaitOne() |&gt; ignore
            )
    <span style="color:blue;">member </span>c.Words =
        w.QueueWithAsync (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt;
            </span>words |&gt; Seq.to_array |&gt; Array.map (<span style="color:blue;">fun </span>kv <span style="color:blue;">-&gt; </span>kv.Key, kv.Value)
        )
<span style="color:blue;">let </span>wc = <span style="color:blue;">new </span>WordCounter()
wc.Add (<span style="color:blue;">__SOURCE_DIRECTORY__ </span>+ <span style="color:maroon;">"kjv10.txt"</span>)
wc.Add (<span style="color:blue;">__SOURCE_DIRECTORY__ </span>+ <span style="color:maroon;">"warandpeace.txt"</span>)
<span style="color:blue;">let </span>wordsToPrint = async {
                    <span style="color:blue;">let! </span>words = wc.Words
                    <span style="color:blue;">return </span>words
                        |&gt; Seq.distinctBy (<span style="color:blue;">fun </span>(key, _) <span style="color:blue;">-&gt; </span>key.ToLower())
                        |&gt; Seq.filter (<span style="color:blue;">fun </span>(key, _) <span style="color:blue;">-&gt; </span>not(key = <span style="color:maroon;">"" </span>|| key = <span style="color:maroon;">""" </span>|| (fst (Double.TryParse(key)))))
                        |&gt; Seq.to_array
                        |&gt; Array.sortBy snd
                        |&gt; Array.rev
                        |&gt; Seq.take <span style="color:brown;">20
                        </span>|&gt; Seq.iter (<span style="color:blue;">fun </span>(key, value) <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"%Att%A" </span>key value)}
Async.RunSynchronously wordsToPrint
Thread.Sleep(<span style="color:brown;">15000</span>)
printfn <span style="color:maroon;">"Closed session"
</span></pre>

