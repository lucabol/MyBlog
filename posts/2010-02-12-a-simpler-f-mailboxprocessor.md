---
id: 1078
title: 'A simpler F# MailboxProcessor'
date: 2010-02-12T15:29:46+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2010/02/12/a-simpler-f-mailboxprocessor/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2010/02/12/a-simpler-f-mailboxprocessor.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9962927"
orig_parent_id:
  - "9962927"
orig_thread_id:
  - "700984"
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
  - http://blogs.msdn.com/b/lucabol/archive/2010/02/12/a-simpler-f-mailboxprocessor.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="A simpler F# MailboxProcessor" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2010/02/12/a-simpler-f-mailboxprocessor/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="I always forget the pattern to use to create a functioning MailboxProcessor in F#. I mean, which piece has to be async and how to structure the recursive loop. When I find myself in that kind of a situation situation, my instincts scream at me: "Wrap it and make it work how your mind expects..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="A simpler F# MailboxProcessor" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2010/02/12/a-simpler-f-mailboxprocessor/" />
    <meta name="twitter:description" content="I always forget the pattern to use to create a functioning MailboxProcessor in F#. I mean, which piece has to be async and how to structure the recursive loop. When I find myself in that kind of a situation situation, my instincts scream at me: "Wrap it and make it work how your mind expects..." />
    
restapi_import_id:
  - 5c011e0505e67
original_post_id:
  - "63"
categories:
  - Uncategorized
tags:
  - fsharp
---
I always forget the pattern to use to create a functioning _MailboxProcessor_ in F#. I mean, which piece has to be async and how to structure the recursive loop. When I find myself in that kind of a situation situation, my instincts scream at me: "Wrap it and make it work how your mind expects it to work". So here is a simplification of the paradigm.

Let's see how some standard _MailboxProcessor_ code looks like:

```fsharp
let counter0 =
    MailboxProcessor.Start(fun inbox ->
        let rec loop n =
            async {
                    let! msg = inbox.Receive()
                    return! loop(n+msg) }
        loop 0)
```

This keeps a running sum of the messages it receives. The only part that is really unique to this guy is "n + msg". All the rest is infrastructure.

You'd probably prefer to write code like the following:

```fsharp
let counter1 = MailboxProcessor.SpawnAgent((fun msg n -> msg + n), 0)
```

Yep, just one line of code. But, is it possible? Let's look at one way of doing it:

```fsharp
type AfterError<'state> =
| ContinueProcessing of 'state
| StopProcessing
| RestartProcessing
type MailboxProcessor<'a> with
    static member public SpawnAgent<'b>(messageHandler :'a->'b->'b,
                                        initialState : 'b, ?timeout:'b -> int,
                                        ?timeoutHandler:'b -> AfterError<'b>,
                                        ?errorHandler:
                                            Exception -> 'a option -> 'b -> AfterError<'b>)
                                        : MailboxProcessor<'a> =
        let timeout = defaultArg timeout (fun _ -> -1)
        let timeoutHandler = defaultArg timeoutHandler (fun state ->
                                                                  ContinueProcessing(state))
        let errorHandler = defaultArg errorHandler (fun _ _ state ->
                                                                  ContinueProcessing(state))
        MailboxProcessor.Start(fun inbox ->
            let rec loop(state) = async {
                let! msg = inbox.TryReceive(timeout(state))
                try
                    match msg with
                    | None      -> match timeoutHandler state with
                                    | ContinueProcessing(newState)    ->
                                                                   return! loop(newState)
                                    | StopProcessing        -> return ()
                                    | RestartProcessing     -> return! loop(initialState)
                    | Some(m)   -> return! loop(messageHandler m state)
                with
                | ex -> match errorHandler ex msg state with
                        | ContinueProcessing(newState)    -> return! loop(newState)
                        | StopProcessing        -> return ()
                        | RestartProcessing     -> return! loop(initialState)
                }
            loop(initialState))
```

The funny formatting is because I have to fit it in the small horizontal space of this blog. In any case, this is just a simple (?) wrapper for the _MailboxProcessor_ pattern. The function takes two necessary parameters and two optional ones:

  * **messageHandler**: a function to execute when a message comes in, it takes the message and the current state as parameters and returns the new state.
  * **initialState**: the initial state for the _MailboxProcessor_
  * **timeoutHandler**: a function that is executed whenever a timeout occurs. It takes as a parameter the current state and returns one of _ContinueProcessing(newState), StopProcessing or RestartProcessing_
  * **errorHandler**: a function that gets call if an exception is generated inside the _messageHandler_ function. It takes the exception, the message, the current state and returns _ContinueProcessing(newState), StopProcessing or RestartProcessing_

An example of how to use _errorHandler_ to implement the CountingAgent in the Expert F# book follows:

```fsharp
type msg = Increment of int | Fetch of AsyncReplyChannel<int> | Stop
exception StopException
type CountingAgent() =
    let counter = MailboxProcessor.SpawnAgent((fun msg n ->
                    match msg with
                    | Increment m ->  n + m
                    | Stop -> raise(StopException)
                    | Fetch replyChannel ->
                        do replyChannel.Reply(n)
                        n
                  ), 0, errorHandler = (fun _ _ _ -> StopProcessing))
    member a.Increment(n) = counter.Post(Increment(n))
    member a.Stop() = counter.Post(Stop)
    member a.Fetch() = counter.PostAndReply(fun replyChannel -> Fetch(replyChannel))
let counter2 = CountingAgent()
counter2.Increment(1)
counter2.Fetch()
counter2.Increment(2)
counter2.Fetch()
counter2.Stop()
```

Sometimes your agent doesn't need a state, it is purely stateless. Something as simple as the following:

```fsharp
let echo = MailboxProcessor<_>.SpawnWorker(fun msg -> printfn "%s" msg)
```

You can easily make that happen by using this toned down version of an agent, called worker:

```fsharp
static member public SpawnWorker(messageHandler,  ?timeout, ?timeoutHandler,?errorHandler) =
    let timeout = defaultArg timeout (fun () -> -1)
    let timeoutHandler = defaultArg timeoutHandler (fun _ -> ContinueProcessing(()))
    let errorHandler = defaultArg errorHandler (fun _ _ -> ContinueProcessing(()))
    MailboxProcessor.SpawnAgent((fun msg _ -> messageHandler msg; ()),
                                 (), timeout, timeoutHandler,
                                 (fun ex msg _ -> errorHandler ex msg))
```

Given that they are parallel, you might want to run a whole bunch of them at the same time. You might want something that looks like a worker, but that, under the cover, execute each _messageHandler_ in parallel. Something like:

```fsharp
type msg1 = Message1 | Message2 of int | Message3 of string
let a = MailboxProcessor.SpawnParallelWorker(function
                | Message1 -> printfn "Message1";
                | Message2 n -> printfn "Message2 %i" n;
                | Message3 _ -> failwith "I failed"
                , 10
                , errorHandler = (fun ex _ -> printfn "%A" ex; ContinueProcessing()))
a.Post(Message1)
a.Post(Message2(100))
a.Post(Message3("abc"))
a.Post(Message2(100))
```

In this example, the different messages, are likely to cause things to print out of order. Notice the number 10 above which is how many workers you want to process your messages. This is implemented by round-robin messages to the various workers:

```fsharp
static member public SpawnParallelWorker(messageHandler, howMany, ?timeout,
                                                        ?timeoutHandler,?errorHandler) =
    let timeout = defaultArg timeout (fun () -> -1)
    let timeoutHandler = defaultArg timeoutHandler (fun _ -> ContinueProcessing(()))
    let errorHandler = defaultArg errorHandler (fun _ _ -> ContinueProcessing(()))
    MailboxProcessor<'a>.SpawnAgent((fun msg (workers:MailboxProcessor<'a> array, index) ->
                                        workers.[index].Post msg
                                        (workers, (index + 1) % howMany))
                                    , (Array.init howMany
                                      (fun _ -> MailboxProcessor<'a>.SpawnWorker(
                                                 messageHandler, timeout, timeoutHandler,
                                                 errorHandler)), 0))
```

One drawback with the current code is that it doesn't supports cancellations. It should be possible to wrap that too, but I haven't done it (yet). If you don't want to cut and paste the code, it is inside the AgentSystem.fs file [here](http://blogs.msdn.com/lucabol/archive/2009/06/12/lagent-an-agent-framework-in-f-part-iii-default-error-management.aspx).
