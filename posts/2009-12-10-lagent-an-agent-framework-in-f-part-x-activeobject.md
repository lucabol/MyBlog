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

If you stare long enough at agents, you start to realize that they are just 'glorified locks'. They are a convenient programming model to protect a resource from concurrent access. The programming model is convenient because both the client and the server can write their code without worrying about concurrency problems, and yet the program runs in parallel. Protecting a resource sounds a lot like state encapsulation and the concept of state encapsulation is what object orientation is all about.

So you start thinking if there is a way to enhance vanilla objects to make them agents. You want to reuse all the concepts that you are familiar with (i.e. inheritance, visibility rules, etc…) and you want your clients to call agents as if they were calling normal objects. Obviously, under the cover, the method calls won't execute immediately, but they would be queued. Let's look at an example.

This is our simple counter agent:

```fsharp
type CounterMessage =
| Add of int
| Print
let counterF = fun msg count ->
    match msg with
    | Add(i)    -> count + i
    | Print     -> printfn "The value is %i" count; count
let c1 = spawnAgent counterF 0
c1 <-- Add(3)
c1 <-- Print
```

As nice as this looks, there are unfamiliar things in this model:

  1. The communication is through messages. This requires packing and unpacking which, albeit easy in F#, is unfamiliar and feels like machinery that we'd like to get rid off. 
  2. The management of state is bizarre, it gets passed into the lambda and returned from it instead of being represented as fields and properties on the agent 

My best attempt at creating an object-like syntax follows:

```fsharp
type Counter() =
    let w = new WorkQueue()
    let mutable count = 0
    member c.Add x = w.Queue (fun () ->
        count <- count + x
        )
    member c.Print () = w.Queue (fun () ->
        printfn "The value is %i" count
        )
```

```fsharp
let c = new Counter()
c.Add 3
c.Print
```

With this syntax, you write your agents like you write your vanilla classes except:

  1. You need a private field of type _WorkQueue_ 
  2. You need to write your methods as lambdas passed to the _WorkQueue.Queue_ function 
  3. Your methods cannot return values 

The most worrisome of these constraints is 2. because you can easily forget about it. If you do forget, then everything compiles just fine, but it doesn't do what you expect. That's pure badness. I haven't found a way to enforce it. This is a place where the language could help me. Other than that, the whole model works rather nicely.

Regarding the third point, you can concoct a programming model that allows you to return values from your methods. Here it is:

```fsharp
member c.CountTask = w.QueueWithTask(fun () ->
    count
    )
member c.CountAsync = w.QueueWithAsync(fun () ->
    count
    )
```

```fsharp
printfn "The count using Task is %i" (c.CountTask.Result)
```

The first method returns a _Task;_ the second method returns an _AsyncResultCell_. Both are ways to represent a [promise](http://en.wikipedia.org/wiki/Future_(programming)). The latter allows a natural integration with the async block in F# as in the following code:

```fsharp
Async.RunSynchronously (
            async {
                let! count = c.CountAsync
                printfn "The countusing Async is %i" count
            })
```

As for myself, I don't like methods returning values. Every time I use them, I end up going back and thinking about my problem in a traditional way, aka as method calls that return results, instead of thinking about it in a more actor oriented fashion. I end up waiting for these promises to be materialized and, by doing so, I limit the amount of parallelism that I unleash. As a matter of fact, the whole business of hiding the message passing nature of the programming model is dubious. It makes for a nicer syntax, but you need to make an extra effort in your mind to translate it to what it really is: just message passing with a nice syntactical veneer. I haven't decided yet which model I like the most.

You should have a sense of what _WorkQueue_ is. In essence, it is a _Mailbox_ of lambdas (look at the red bold code below). 

```fsharp
type WorkQueue() =
    let workQueue = spawnWorker (fun f -> f())
    member w.Queue (f) = workQueue <-- f
    member w.QueueWithTask f : Task<'T> =
        let source = new TaskCompletionSource<_>()
        workQueue <-- (fun () -> f() |> source.SetResult)
        source.Task
    member w.QueueWithAsync (f:unit -> 'T) : Async<'T> =
        let result = new AsyncResultCell<'T>()
        workQueue <-- (fun () -> f() |> result.RegisterResult )
        result.AsyncWaitResult
    member w.Restart () = workQueue <-! Restart
    member w.Stop () = workQueue <-! Stop
    member w.SetErrorHandler(h) =
        let managerF = fun (_, name:string, ex:Exception, _, _, _) -> h name ex
        let manager = spawnWorker managerF
        workQueue <-! SetManager manager
    member w.SetName(name) = workQueue <-! SetName(name)
    member w.SetQueueHandler(g) = workQueue <-! SetWorkerHandler(g)
    member w.SetTimeoutHandler(timeout, f) = workQueue <-! SetTimeoutHandler(timeout, f)
```

I implemented all the services that are in the message passing model. The two are equivalent as expressing power goes. In case you wonder how a real piece of code looks like using this model, here is an _ActiveObject_ version of the map reduce algorithm. One of these days, I will gather the strength to go trough this code and explain what it does, but not today 🙂

```fsharp
#load "AgentSystem.fs"
open AgentSystem.LAgent
open System
open System.Collections
open System.Collections.Generic
open System.Threading
type IOutput<'out_key, 'out_value> =
    abstract Reduced: 'out_key -> seq<'out_value> -> unit
    abstract MapReduceDone: unit -> unit
type Mapper<'in_key, 'in_value, 'my_out_key, 'out_value when 'my_out_key : comparison>
                                                      (map:'in_key -> 'in_value -> seq<'my_out_key * 'out_value>, i, partitionF) =
    let w = new WorkQueue()
    let mutable reducerTracker: BitArray = null
    let mutable controller = Unchecked.defaultof<Controller<'in_key, 'in_value, 'my_out_key, 'out_value>>
    let mutable reducers = Unchecked.defaultof<Reducer<'in_key, 'in_value, 'my_out_key, 'out_value> array>
    member m.Init c reds =
        w.Queue (fun () ->
            controller <- c
            reducers <- reds
            reducerTracker <- new BitArray(reducers.Length, false))
    member m.Process inKey inValue =
        w.Queue (fun () ->
            let outKeyValues = map inKey inValue
            outKeyValues |> Seq.iter (fun (outKey, outValue) ->
                                        let reducerUsed = partitionF outKey (reducers.Length)
                                        reducerTracker.Set(reducerUsed, true)
                                        reducers.[reducerUsed].Add(outKey, outValue)))
    member m.Done () =
        w.Queue (fun () ->
            controller.MapDone i reducerTracker)
    member m.Stop () = w.Stop ()
and Reducer<'in_key, 'in_value, 'out_key, 'out_value when 'out_key :
                     comparison>(reduce:'out_key -> seq<'out_value> -> seq<'out_value>, i, output:IOutput<'out_key, 'out_value>) =
    let w = new WorkQueue()
    let mutable workItems = new List<'out_key * 'out_value>()
    let mutable controller = Unchecked.defaultof<Controller<'in_key, 'in_value, 'out_key, 'out_value>>
    member r.Init c =
        w.Queue (fun () ->
            controller <- c)
    member r.StartReduction () =
        w.Queue (fun () ->
            workItems
            |> Seq.groupBy fst
            |> Seq.sortBy fst
            |> Seq.map (fun (key, values) -> (key, reduce key (values |> Seq.map snd)))
            |> Seq.iter (fun (key, value) -> output.Reduced key value)
            controller.ReductionDone i)
    member r.Add (outKey:'out_key, outValue:'out_value) : unit =
        w.Queue (fun () ->
            workItems.Add((outKey, outValue)))
    member m.Stop () = w.Stop ()
and Controller<'in_key, 'in_value, 'out_key, 'out_value when 'out_key : comparison>(output:IOutput<'out_key, 'out_value>) =
    let w = new WorkQueue()
    let mutable mapperTracker: BitArray = null
    let mutable reducerUsedByMappers: BitArray = null
    let mutable reducerDone: BitArray = null
    let mutable mappers = Unchecked.defaultof<Mapper<'in_key, 'in_value, 'out_key, 'out_value> array>
    let mutable reducers = Unchecked.defaultof<Reducer<'in_key, 'in_value, 'out_key, 'out_value> array>
    let BAtoSeq (b:BitArray) = [for x in b do yield x]
    member c.Init maps reds =
        w.Queue (fun () ->
            mappers <- maps
            reducers <- reds
            mapperTracker <- new BitArray(mappers.Length, false)
            reducerUsedByMappers <- new BitArray(reducers.Length, false)
            reducerDone <- new BitArray(reducers.Length, false))
    member c.MapDone (i : int) (reducerTracker : BitArray) : unit =
        w.Queue (fun () ->
            mapperTracker.Set(i, true)
            let reducerUsedByMappers = reducerUsedByMappers.Or(reducerTracker)
            if not( BAtoSeq mapperTracker |> Seq.exists(fun bit -> bit = false)) then
                BAtoSeq reducerUsedByMappers |> Seq.iteri (fun i r -> if r = true then reducers.[i].StartReduction ())
                mappers |> Seq.iter (fun m -> m.Stop ())
              )
    member c.ReductionDone (i: int) : unit =
        w.Queue (fun () ->
            reducerDone.Set(i, true)
            if BAtoSeq reducerDone |> Seq.forall2 (fun x y -> x = y) (BAtoSeq reducerUsedByMappers) then
                output.MapReduceDone ()
                reducers |> Seq.iter (fun r -> r.Stop ())
                c.Stop()
             )
    member m.Stop () = w.Stop ()
let mapReduce   (inputs:seq<'in_key * 'in_value>)
                (map:'in_key -> 'in_value -> seq<'out_key * 'out_value>)
                (reduce:'out_key -> seq<'out_value> -> seq<'out_value>)
                (output:IOutput<'out_key, 'out_value>)
                M R partitionF =
    let len = inputs |> Seq.length
    let M = if len < M then len else M
    let mappers = Array.init M (fun i -> new Mapper<'in_key, 'in_value, 'out_key, 'out_value>(map, i, partitionF))
    let reducers = Array.init R (fun i -> new Reducer<'in_key, 'in_value, 'out_key, 'out_value>(reduce, i, output))
    let controller = new Controller<'in_key, 'in_value, 'out_key, 'out_value>(output)
    mappers |> Array.iter (fun m -> m.Init controller reducers)
    reducers |> Array.iter (fun r -> r. Init controller )
    controller.Init mappers reducers
    inputs |> Seq.iteri (fun i (inKey, inValue) -> mappers.[i % M].Process inKey inValue)
    mappers |> Seq.iter (fun m -> m.Done ())
let partitionF = fun key M -> abs(key.GetHashCode()) % M
let map = fun (fileName:string) (fileContent:string) ->
            let l = new List<string * int>()
            let wordDelims = [|' ';',';';';'.';':';'?';'!';'(';')';'n';'t';'f';'r';'b'|]
            fileContent.Split(wordDelims) |> Seq.iter (fun word -> l.Add((word, 1)))
            l :> seq<string * int>
let reduce = fun key (values:seq<int>) -> [values |> Seq.sum] |> seq<int>
let printer () =
  { new IOutput<string, int> with
        member o.Reduced key values = printfn "%A %A" key values
        member o.MapReduceDone () = printfn "All done!!"}
let testInput =
     ["File1", "I was going to the airport when I saw someone crossing"; "File2", "I was going home when I saw you coming toward me"]
mapReduce testInput map reduce (printer ()) 2 2 partitionF
open System.IO
open System.Text
let gatherer(step) =
  let w = new WorkQueue()
  let data = new List<string * int>()
  let counter = ref 0
  { new IOutput<string, int> with
        member o.Reduced key values =
            w.Queue (fun () ->
                if !counter % step = 0 then
                    printfn "Processed %i words. Now processing %s" !counter key
                data.Add((key, values |> Seq.hd))
                counter := !counter + 1)
        member o.MapReduceDone () =
            w.Queue (fun () ->
                data
                |> Seq.distinctBy (fun (key, _) -> key.ToLower())
                |> Seq.filter (fun (key, _) -> not(key = "" || key = """ || (fst (Double.TryParse(key)))))
                |> Seq.to_array
                |> Array.sortBy snd
                |> Array.rev
                |> Seq.take 20
                |> Seq.iter (fun (key, value) -> printfn "%A\t%A" key value)
                printfn "All done!!")
        }
let splitBook howManyBlocks fileName =
    let buffers = Array.init howManyBlocks (fun _ -> new StringBuilder())
    fileName
    |> File.ReadAllLines
    |> Array.iteri (fun i line -> buffers.[i % (howManyBlocks)].Append(line) |> ignore)
    buffers
let blocks1 = __SOURCE_DIRECTORY__ + "kjv10.txt" |> splitBook 100
let blocks2 = __SOURCE_DIRECTORY__ + "warandpeace.txt" |> splitBook 100
let input =
    blocks1
    |> Array.append blocks2
    |> Array.mapi (fun i b -> i.ToString(), b.ToString())
//mapReduce input map reduce (gatherer(1000)) 20 20 partitionF
type BookSplitter () =
    let blocks = new List<string * string>()
    member b.Split howManyBlocks fileName =
            let b =
                fileName
                |> splitBook howManyBlocks
                |> Array.mapi (fun i b -> i.ToString(), b.ToString())
            blocks.AddRange(b)
    member b.Blocks () =
            blocks.ToArray() :> seq<string * string>
type WordCounter () =
    let w = new WorkQueue()
    let words = new Dictionary<string,int>()
    let worker(wordCounter:WordCounter, ev:EventWaitHandle) =
          let w1 = new WorkQueue()
          { new IOutput<string, int> with
                member o.Reduced key values =
                    w1.Queue (fun() ->
                        wordCounter.AddWord key (values |> Seq.hd))
                member o.MapReduceDone () =
                    w1.Queue(fun () ->
                        ev.Set() |> ignore)
           }
    member c.AddWord word count =
            let exist, value = words.TryGetValue(word)
            if exist then
                words.[word] <- value + count
            else
                words.Add(word, count)
    member c.Add fileName =
        w.Queue (fun () ->
            let s = new BookSplitter()
            fileName |> s.Split 100
            let ev = new EventWaitHandle(false, EventResetMode.AutoReset)
            let blocks = s.Blocks ()
            mapReduce blocks map reduce (worker(c, ev)) 20 20 partitionF
            ev.WaitOne() |> ignore
            )
    member c.Words =
        w.QueueWithAsync (fun () ->
            words |> Seq.to_array |> Array.map (fun kv -> kv.Key, kv.Value)
        )
let wc = new WordCounter()
wc.Add (__SOURCE_DIRECTORY__ + "kjv10.txt")
wc.Add (__SOURCE_DIRECTORY__ + "warandpeace.txt")
let wordsToPrint = async {
                    let! words = wc.Words
                    return words
                        |> Seq.distinctBy (fun (key, _) -> key.ToLower())
                        |> Seq.filter (fun (key, _) -> not(key = "" || key = """ || (fst (Double.TryParse(key)))))
                        |> Seq.to_array
                        |> Array.sortBy snd
                        |> Array.rev
                        |> Seq.take 20
                        |> Seq.iter (fun (key, value) -> printfn "%A\t%A" key value)}
Async.RunSynchronously wordsToPrint
Thread.Sleep(15000)
printfn "Closed session"
