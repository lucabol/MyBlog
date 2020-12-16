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
    <meta property="og:description" content="I always forget the pattern to use to create a functioning MailboxProcessor in F#. I mean, which piece has to be async and how to structure the recursive loop. When I find myself in that kind of a situation situation, my instincts scream at me: “Wrap it and make it work how your mind expects..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="A simpler F# MailboxProcessor" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2010/02/12/a-simpler-f-mailboxprocessor/" />
    <meta name="twitter:description" content="I always forget the pattern to use to create a functioning MailboxProcessor in F#. I mean, which piece has to be async and how to structure the recursive loop. When I find myself in that kind of a situation situation, my instincts scream at me: “Wrap it and make it work how your mind expects..." />
    
restapi_import_id:
  - 5c011e0505e67
original_post_id:
  - "63"
categories:
  - Uncategorized
tags:
  - fsharp
---
I always forget the pattern to use to create a functioning _MailboxProcessor_ in F#. I mean, which piece has to be async and how to structure the recursive loop. When I find myself in that kind of a situation situation, my instincts scream at me: “Wrap it and make it work how your mind expects it to work”. So here is a simplification of the paradigm.

Let’s see how some standard _MailboxProcessor_ code looks like:

<pre class="code"><span style="color:blue;">let </span>counter0 =
    MailboxProcessor.Start(<span style="color:blue;">fun </span>inbox <span style="color:blue;">-&gt;
        let rec </span>loop n =
            async {
                    <span style="color:blue;">let! </span>msg = inbox.Receive()
                    <span style="color:blue;">return! </span>loop(n+msg) }
        loop 0)</pre>

This keeps a running sum of the messages it receives. The only part that is really unique to this guy is “n + msg”. All the rest is infrastructure.

You’d probably prefer to write code like the following:

<pre class="code"><span style="color:blue;">let </span>counter1 = MailboxProcessor.SpawnAgent( (<span style="color:blue;">fun </span>msg n <span style="color:blue;">-&gt; </span>msg + n), 0)</pre>

Yep, just one line of code. But, is it possible? Let’s look at one way of doing it:

<pre class="code"><span style="color:blue;">type </span>AfterError&lt;'state&gt; =
| ContinueProcessing <span style="color:blue;">of </span>'state
| StopProcessing
| RestartProcessing
<span style="color:blue;">type </span>MailboxProcessor&lt;'a&gt; <span style="color:blue;">with
    static member public </span>SpawnAgent&lt;'b&gt;(messageHandler :'a<span style="color:blue;">-&gt;</span>'b<span style="color:blue;">-&gt;</span>'b,<br />                                        initialState : 'b, ?timeout:'b <span style="color:blue;">-&gt; </span>int,
                                        ?timeoutHandler:'b <span style="color:blue;">-&gt; </span>AfterError&lt;'b&gt;,<br />                                        ?errorHandler:<br />                                            Exception <span style="color:blue;">-&gt; </span>'a option <span style="color:blue;">-&gt; </span>'b <span style="color:blue;">-&gt; </span>AfterError&lt;'b&gt;)<br />                                        : MailboxProcessor&lt;'a&gt; =
        <span style="color:blue;">let </span>timeout = defaultArg timeout (<span style="color:blue;">fun </span>_ <span style="color:blue;">-&gt; </span>-1)
        <span style="color:blue;">let </span>timeoutHandler = defaultArg timeoutHandler (<span style="color:blue;">fun </span>state –<span style="color:blue;">&gt;<br />                                                                  </span>ContinueProcessing(state))
        <span style="color:blue;">let </span>errorHandler = defaultArg errorHandler (<span style="color:blue;">fun </span>_ _ state –<span style="color:blue;">&gt;<br />                                                                  </span>ContinueProcessing(state))
        MailboxProcessor.Start(<span style="color:blue;">fun </span>inbox <span style="color:blue;">-&gt;
            let rec </span>loop(state) = async {
                <span style="color:blue;">let! </span>msg = inbox.TryReceive(timeout(state))
                <span style="color:blue;">try
                    match </span>msg <span style="color:blue;">with
                    </span>| None      <span style="color:blue;">-&gt; match </span>timeoutHandler state <span style="color:blue;">with
                                    </span>| ContinueProcessing(newState)    <span style="color:blue;">-&gt;<br />                                                                   return! </span>loop(newState)
                                    | StopProcessing        <span style="color:blue;">-&gt; return </span>()
                                    | RestartProcessing     <span style="color:blue;">-&gt; return! </span>loop(initialState)
                    | Some(m)   <span style="color:blue;">-&gt; return! </span>loop(messageHandler m state)
                <span style="color:blue;">with
                </span>| ex <span style="color:blue;">-&gt; match </span>errorHandler ex msg state <span style="color:blue;">with
                        </span>| ContinueProcessing(newState)    <span style="color:blue;">-&gt; return! </span>loop(newState)
                        | StopProcessing        <span style="color:blue;">-&gt; return </span>()
                        | RestartProcessing     <span style="color:blue;">-&gt; return! </span>loop(initialState)
                }
            loop(initialState))</pre>



The funny formatting is because I have to fit it in the small horizontal space of this blog. In any case, this is just a simple (?) wrapper for the _MailboxProcessor_ pattern. The function takes two necessary parameters and two optional ones:

  * **messageHandler**: a function to execute when a message comes in, it takes the message and the current state as parameters and returns the new state.
  * **initialState**: the initial state for the _MailboxProcessor_
  * **timeoutHandler**: a function that is executed whenever a timeout occurs. It takes as a parameter the current state and returns one of _ContinueProcessing(newState), StopProcessing or RestartProcessing_
  * **errorHandler**: a function that gets call if an exception is generated inside the _messageHandler_ function. It takes the exception, the message, the current state and returns _ContinueProcessing(newState), StopProcessing or RestartProcessing_

An example of how to use _errorHandler_ to implement the CountingAgent in the Expert F# book follows:

<pre class="code"><span style="color:blue;">type </span>msg = Increment <span style="color:blue;">of </span>int | Fetch <span style="color:blue;">of </span>AsyncReplyChannel&lt;int&gt; | Stop
<span style="color:blue;">exception </span>StopException
<span style="color:blue;">type </span>CountingAgent() =
    <span style="color:blue;">let </span>counter = MailboxProcessor.SpawnAgent((<span style="color:blue;">fun </span>msg n <span style="color:blue;">-&gt;
                    match </span>msg <span style="color:blue;">with
                    </span>| Increment m <span style="color:blue;">-&gt;  </span>n + m
                    | Stop <span style="color:blue;">-&gt; </span>raise(StopException)
                    | Fetch replyChannel <span style="color:blue;">-&gt;
                        do </span>replyChannel.Reply(n)
                        n
                  ), 0, errorHandler = (<span style="color:blue;">fun </span>_ _ _ <span style="color:blue;">-&gt; </span>StopProcessing))
    <span style="color:blue;">member </span>a.Increment(n) = counter.Post(Increment(n))
    <span style="color:blue;">member </span>a.Stop() = counter.Post(Stop)
    <span style="color:blue;">member </span>a.Fetch() = counter.PostAndReply(<span style="color:blue;">fun </span>replyChannel <span style="color:blue;">-&gt; </span>Fetch(replyChannel))
<span style="color:blue;">let </span>counter2 = CountingAgent()
counter2.Increment(1)
counter2.Fetch()
counter2.Increment(2)
counter2.Fetch()
counter2.Stop()                             </pre>

Sometimes your agent doesn’t need a state, it is purely stateless. Something as simple as the following:

<pre class="code"><span style="color:blue;">let </span>echo = MailboxProcessor&lt;_&gt;.SpawnWorker(<span style="color:blue;">fun </span>msg <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"%s" </span>msg)</pre>

You can easily make that happen by using this toned down version of an agent, called worker:

<pre class="code"><span style="color:blue;">static member public </span>SpawnWorker(messageHandler,  ?timeout, ?timeoutHandler,?errorHandler) =
    <span style="color:blue;">let </span>timeout = defaultArg timeout (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt; </span>-1)
    <span style="color:blue;">let </span>timeoutHandler = defaultArg timeoutHandler (<span style="color:blue;">fun </span>_ <span style="color:blue;">-&gt; </span>ContinueProcessing(()))
    <span style="color:blue;">let </span>errorHandler = defaultArg errorHandler (<span style="color:blue;">fun </span>_ _ <span style="color:blue;">-&gt; </span>ContinueProcessing(()))
    MailboxProcessor.SpawnAgent((<span style="color:blue;">fun </span>msg _ <span style="color:blue;">-&gt; </span>messageHandler msg; ()),<br />                                 (), timeout, timeoutHandler,<br />                                 (<span style="color:blue;">fun </span>ex msg _ <span style="color:blue;">-&gt; </span>errorHandler ex msg))</pre></p> 



Given that they are parallel, you might want to run a whole bunch of them at the same time. You might want something that looks like a worker, but that, under the cover, execute each _messageHandler_ in parallel. Something like:

<pre class="code"><span style="color:blue;">type </span>msg1 = Message1 | Message2 <span style="color:blue;">of </span>int | Message3 <span style="color:blue;">of </span>string
<span style="color:blue;">let </span>a = MailboxProcessor.SpawnParallelWorker(<span style="color:blue;">function
                </span>| Message1 <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"Message1"</span>;
                | Message2 n <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"Message2 %i" </span>n;
                | Message3 _ <span style="color:blue;">-&gt; </span>failwith <span style="color:maroon;">"I failed"
                </span>, 10
                , errorHandler = (<span style="color:blue;">fun </span>ex _ <span style="color:blue;">-&gt; </span>printfn <span style="color:maroon;">"%A" </span>ex; ContinueProcessing()))
a.Post(Message1)
a.Post(Message2(100))
a.Post(Message3(<span style="color:maroon;">"abc"</span>))
a.Post(Message2(100))</pre></p> 



In this example, the different messages, are likely to cause things to print out of order. Notice the number 10 above which is how many workers you want to process your messages. This is implemented by round-robin messages to the various workers:

<pre class="code"><span style="color:blue;">static member public </span>SpawnParallelWorker(messageHandler, howMany, ?timeout,<br />                                                        ?timeoutHandler,?errorHandler) =
    <span style="color:blue;">let </span>timeout = defaultArg timeout (<span style="color:blue;">fun </span>() <span style="color:blue;">-&gt; </span>-1)
    <span style="color:blue;">let </span>timeoutHandler = defaultArg timeoutHandler (<span style="color:blue;">fun </span>_ <span style="color:blue;">-&gt; </span>ContinueProcessing(()))
    <span style="color:blue;">let </span>errorHandler = defaultArg errorHandler (<span style="color:blue;">fun </span>_ _ <span style="color:blue;">-&gt; </span>ContinueProcessing(()))
    MailboxProcessor&lt;'a&gt;.SpawnAgent((<span style="color:blue;">fun </span>msg (workers:MailboxProcessor&lt;'a&gt; array, index) <span style="color:blue;">-&gt;
                                        </span>workers.[index].Post msg
                                        (workers, (index + 1) % howMany))
                                    , (Array.init howMany<br />                                      (<span style="color:blue;">fun </span>_ <span style="color:blue;">-&gt; </span>MailboxProcessor&lt;'a&gt;.SpawnWorker(<br />                                                 messageHandler, timeout, timeoutHandler,<br />                                                 errorHandler)), 0))</pre>

One drawback with the current code is that it doesn’t supports cancellations. It should be possible to wrap that too, but I haven’t done it (yet). If you don’t want to cut and paste the code, it is inside the AgentSystem.fs file [here](http://blogs.msdn.com/lucabol/archive/2009/06/12/lagent-an-agent-framework-in-f-part-iii-default-error-management.aspx).