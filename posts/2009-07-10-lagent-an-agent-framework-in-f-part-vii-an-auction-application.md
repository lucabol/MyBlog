---
id: 1086
title: 'LAgent: an agent framework in F# – part VII – An auction application'
date: 2009-07-10T16:14:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/07/10/lagent-an-agent-framework-in-f-part-vii-an-auction-application/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/07/10/lagent-an-agent-framework-in-f-part-vii-an-auction-application.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9682539"
orig_parent_id:
  - "9682539"
orig_thread_id:
  - "658543"
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
  - http://blogs.msdn.com/b/lucabol/archive/2009/07/10/lagent-an-agent-framework-in-f-part-vii-an-auction-application.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="LAgent: an agent framework in F# &ndash; part VII &ndash; An auction application" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/07/10/lagent-an-agent-framework-in-f-part-vii-an-auction-application/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="LAgent: an agent framework in F# &ndash; part VII &ndash; An auction application" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/07/10/lagent-an-agent-framework-in-f-part-vii-an-auction-application/" />
    <meta name="twitter:description" content="Download framework here. All posts are here: Part I  - Workers and ParallelWorkers Part II  - Agents and control messages Part III  - Default error management Part IV  - Custom error management Part V  - Timeout management Part VI  - Hot swapping of code Part VII  - An auction framework Part VIII – Implementing MapReduce..." />
    
restapi_import_id:
  - 5c011e0505e67
original_post_id:
  - "153"
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

Here is an application that uses the framework we have been creating. It is an auction application and it is described in more detail [here](http://codebetter.com/blogs/matthew.podwysocki/archive/2009/05/20/f-actors-revisited.aspx).

Let's go through it.

```fsharp
type AuctionMessage =
  | Offer of int * AsyncAgent // Make a bid
  | Inquire of AsyncAgent     // Check the status
and AuctionReply =
  | StartBidding
  | Status of int * DateTime // Asked sum and expiration
  | BestOffer                // Ours is the best offer
  | BeatenOffer of int       // Yours is beaten by another offer
  | AuctionConcluded of      // Auction concluded
      AsyncAgent * AsyncAgent
  | AuctionFailed            // Failed without any bids
  | AuctionOver              // Bidding is closed
let timeToShutdown = 3000
let bidIncrement = 10 
```

This is the format of the messages that the clients can send and the action agent can reply to. F# is really good at this sort of thing. First, we need an auction agent:

```fsharp
let auctionAgent seller minBid closing =
    let agent = spawnAgent (fun msg (isConcluded, maxBid, maxBidder) ->
                            match msg with
                            | Offer (_, client) when isConcluded ->
                                client <-- AuctionOver
                                (isConcluded, maxBid, maxBidder)
                            | Offer(bid, client) when not(isConcluded) ->
                                if bid >= maxBid + bidIncrement then
                                    if maxBid >= minBid then maxBidder <-- BeatenOffer bid
                                    client <-- BestOffer
                                    (isConcluded, bid, client)
                                else
                                    client <-- BeatenOffer maxBid
                                    (isConcluded, maxBid, maxBidder)
                            | Inquire client    ->
                                client <-- Status(maxBid, closing)
                                (isConcluded, maxBid, maxBidder))
                            (false, (minBid - bidIncrement), spawnWorker (fun _ -> ()))                             
```

Notice that, if the action is concluded, the agent replies to offers by sending an _AuctionOver_ message. If the auction is still open, then, in case the bid is higher than the max, it sets a new max and notify the two parties involved; otherwise it notifies the bidder that the offer wasn't successful. Also you can ask for the status of the auction.

This is what the code above says. Maybe the code is simpler than words. Anyhow, we need to treat the case where no message is received for some amount of time.

```fsharp
agent <-- SetTimeoutHandler
            (closing - DateTime.Now).Milliseconds
            (fun (isConcluded: bool, maxBid, maxBidder) ->
                if maxBid >= minBid then
                  let reply = AuctionConcluded(seller, maxBidder)
                  maxBidder <-- reply
                  seller <-- reply
                else seller <-- AuctionFailed
                agent <-- SetTimeoutHandler
                    timeToShutdown
                    (fun (_:bool, _:int,_:AsyncAgent) -> StopProcessing)
                ContinueProcessing (true, maxBid, maxBidder))
agent            
```

We start by waiting for the amount of time to the closing of the auction. If we get no messages, then two things might happen: we have an offer that is more than the minimum or we don't. If we do, we tell everyone that it's finished. Otherwise, we tell the seller that its item wasn't successful.&#160; In any case, we prepare the agent to shutdown by setting its next timeout to be _timeoutToShutdown_.

It is interesting that we set the timeout handler inside the timeout handler. This is not a problem because of the nature of message processing (aka it processes one message at the time).

We then need a bunch of of symbols …

```fsharp
module Auction =
  let random = new Random()
  let minBid = 100
  let closing = DateTime.Now.AddMilliseconds 10000.
  let seller = spawnWorker (fun (msg:AuctionReply) -> ())
  let auction = auctionAgent seller minBid closing
```

Not a very smart seller we have here … Next up is our definition of a client.

```fsharp
let rec c = spawnAgent (
                fun msg (max, current) ->
                    let processBid (aMax, aCurrent) =
                        if aMax >= top then
                            log "too high for me"
                            (aMax, aCurrent)
                        elif aCurrent < aMax then
                              let aCurrent = aMax + increment
                              Thread.Sleep (1 + random.Next 1000)
                              auction <-- Offer(aCurrent, c)
                              (aMax, aCurrent)
                        else (aMax, aCurrent)
                    match msg with
                    | StartBidding      ->
                        auction <-- Inquire c
                        (max, current)
                    | Status(maxBid,_)  ->
                        log <| sprintf "status(%d)" maxBid
                        let s = processBid (maxBid, current)
                        c <-- SetTimeoutHandler timeToShutdown (fun _ -> StopProcessing)
                        s
                    | BestOffer ->
                        log <| sprintf "bestOffer(%d)" current
                        processBid(max, current)
                    | BeatenOffer maxBid ->
                        log <| sprintf "beatenOffer(%d)" maxBid
                        processBid(maxBid, current)
                    | AuctionConcluded(seller, maxBidder) ->
                        log "auctionConcluded"
                        c <-- Stop
                        (max, current)
                    | AuctionOver ->
                        log "auctionOver"
                        c <-- Stop
                        (max, current))
                 (0,0)
c
```

Something that I like about agents is the fact that you need to understand just small snippets of code at the time. For example, you can read the processing for BestOffer and figure out if it makes sense.&#160; I have an easy time personalizing them as in : "Ok, the guy just got a notification that there has been a better offer, what is he going to do next?".

The code should be self explanatory for the most part. In essence, if you can offer more, do it otherwise wait for the auction to end. I'm not even sure the processing is completely right. I confess I'm just trying to do the same as Matthews code from the link above.

We can then start up the whole thing and enjoy the cool output.

```fsharp
open Auction
(client 1 20 200) <-- StartBidding
(client 2 10 300) <-- StartBidding
(client 3 30 150) <-- StartBidding
Console.ReadLine() |> ignore  
```

Now for the nasty part. Implementing the framework.
