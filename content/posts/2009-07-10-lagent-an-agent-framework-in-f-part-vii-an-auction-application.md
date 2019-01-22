---
id: 1086
title: 'LAgent: an agent framework in F# – part VII – An auction application'
date: 2009-07-10T16:14:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/07/10/lagent-an-agent-framework-in-f-part-vii-an-auction-application/
permalink: /2009/07/10/lagent-an-agent-framework-in-f-part-vii-an-auction-application/
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



Here is an application that uses the framework we have been creating. It is an auction application and it is described in more detail [here](http://codebetter.com/blogs/matthew.podwysocki/archive/2009/05/20/f-actors-revisited.aspx).

Let’s go through it.

<pre class="code"><span style="color:blue;">type </span>AuctionMessage =
  | Offer <span style="color:blue;">of </span>int * AsyncAgent <span style="color:green;">// Make a bid
  </span>| Inquire <span style="color:blue;">of </span>AsyncAgent     <span style="color:green;">// Check the status
</span><span style="color:blue;">and </span>AuctionReply =
  | StartBidding
  | Status <span style="color:blue;">of </span>int * DateTime <span style="color:green;">// Asked sum and expiration
  </span>| BestOffer                <span style="color:green;">// Ours is the best offer
  </span>| BeatenOffer <span style="color:blue;">of </span>int       <span style="color:green;">// Yours is beaten by another offer
  </span>| AuctionConcluded <span style="color:blue;">of      </span><span style="color:green;">// Auction concluded
      </span>AsyncAgent * AsyncAgent
  | AuctionFailed            <span style="color:green;">// Failed without any bids
  </span>| AuctionOver              <span style="color:green;">// Bidding is closed
</span><span style="color:blue;">let </span>timeToShutdown = 3000
<span style="color:blue;">let </span>bidIncrement = 10 </pre>

This is the format of the messages that the clients can send and the action agent can reply to. F# is really good at this sort of thing. First, we need an auction agent:

<pre class="code"><span style="color:blue;">let </span>auctionAgent seller minBid closing =
    <span style="color:blue;">let </span>agent = spawnAgent (<span style="color:blue;">fun </span>msg (isConcluded, maxBid, maxBidder) <span style="color:blue;">-&gt;
                            match </span>msg <span style="color:blue;">with
                            </span>| Offer (_, client) <span style="color:blue;">when </span>isConcluded <span style="color:blue;">-&gt;
                                </span>client &lt;-- AuctionOver
                                (isConcluded, maxBid, maxBidder)
                            | Offer(bid, client) <span style="color:blue;">when </span>not(isConcluded) <span style="color:blue;">-&gt;
                                if </span>bid &gt;= maxBid + bidIncrement <span style="color:blue;">then
                                    if </span>maxBid &gt;= minBid <span style="color:blue;">then </span>maxBidder &lt;-- BeatenOffer bid
                                    client &lt;-- BestOffer
                                    (isConcluded, bid, client)
                                <span style="color:blue;">else
                                    </span>client &lt;-- BeatenOffer maxBid
                                    (isConcluded, maxBid, maxBidder)
                            | Inquire client    <span style="color:blue;">-&gt;
                                </span>client &lt;-- Status(maxBid, closing)
                                (isConcluded, maxBid, maxBidder))
                            (<span style="color:blue;">false</span>, (minBid - bidIncrement), spawnWorker (<span style="color:blue;">fun </span>_ <span style="color:blue;">-&gt; </span>()))                             </pre>

Notice that, if the action is concluded, the agent replies to offers by sending an _AuctionOver_ message. If the auction is still open, then, in case the bid is higher than the max, it sets a new max and notify the two parties involved; otherwise it notifies the bidder that the offer wasn’t successful. Also you can ask for the status of the auction.

This is what the code above says. Maybe the code is simpler than words. Anyhow, we need to treat the case where no message is received for some amount of time.

<pre class="code">agent &lt;-- SetTimeoutHandler
            (closing - DateTime.Now).Milliseconds
            (<span style="color:blue;">fun </span>(isConcluded: bool, maxBid, maxBidder) <span style="color:blue;">-&gt;
                if </span>maxBid &gt;= minBid <span style="color:blue;">then
                  let </span>reply = AuctionConcluded(seller, maxBidder)
                  maxBidder &lt;-- reply
                  seller &lt;-- reply
                <span style="color:blue;">else </span>seller &lt;-- AuctionFailed
                agent &lt;-- SetTimeoutHandler
                    timeToShutdown
                    (<span style="color:blue;">fun </span>(_:bool, _:int,_:AsyncAgent) <span style="color:blue;">-&gt; </span>StopProcessing)
                ContinueProcessing (<span style="color:blue;">true</span>, maxBid, maxBidder))
agent            </pre>

We start by waiting for the amount of time to the closing of the auction. If we get no messages, then two things might happen: we have an offer that is more than the minimum or we don’t. If we do, we tell everyone that it’s finished. Otherwise, we tell the seller that its item wasn’t successful.&#160; In any case, we prepare the agent to shutdown by setting its next timeout to be _timeoutToShutdown_.

It is interesting that we set the timeout handler inside the timeout handler. This is not a problem because of the nature of message processing (aka it processes one message at the time).

We then need a bunch of of symbols …

<pre class="code"><span style="color:blue;">module </span>Auction =
  <span style="color:blue;">let </span>random = <span style="color:blue;">new </span>Random()
  <span style="color:blue;">let </span>minBid = 100
  <span style="color:blue;">let </span>closing = DateTime.Now.AddMilliseconds 10000.
  <span style="color:blue;">let </span>seller = spawnWorker (<span style="color:blue;">fun </span>(msg:AuctionReply) <span style="color:blue;">-&gt; </span>())
  <span style="color:blue;">let </span>auction = auctionAgent seller minBid closing</pre>

Not a very smart seller we have here … Next up is our definition of a client.

<pre class="code"><span style="color:blue;">let rec </span>c = spawnAgent (
                <span style="color:blue;">fun </span>msg (max, current) <span style="color:blue;">-&gt;
                    let </span>processBid (aMax, aCurrent) =
                        <span style="color:blue;">if </span>aMax &gt;= top <span style="color:blue;">then
                            </span>log <span style="color:maroon;">"too high for me"
                            </span>(aMax, aCurrent)
                        <span style="color:blue;">elif </span>aCurrent &lt; aMax <span style="color:blue;">then
                              let </span>aCurrent = aMax + increment
                              Thread.Sleep (1 + random.Next 1000)
                              auction &lt;-- Offer(aCurrent, c)
                              (aMax, aCurrent)
                        <span style="color:blue;">else </span>(aMax, aCurrent)
                    <span style="color:blue;">match </span>msg <span style="color:blue;">with
                    </span>| StartBidding      <span style="color:blue;">-&gt;
                        </span>auction &lt;-- Inquire c
                        (max, current)
                    | Status(maxBid,_)  <span style="color:blue;">-&gt;
                        </span>log &lt;| sprintf <span style="color:maroon;">"status(%d)" </span>maxBid
                        <span style="color:blue;">let </span>s = processBid (maxBid, current)
                        c &lt;-- SetTimeoutHandler timeToShutdown (<span style="color:blue;">fun </span>_ <span style="color:blue;">-&gt; </span>StopProcessing)
                        s
                    | BestOffer <span style="color:blue;">-&gt;
                        </span>log &lt;| sprintf <span style="color:maroon;">"bestOffer(%d)" </span>current
                        processBid(max, current)
                    | BeatenOffer maxBid <span style="color:blue;">-&gt;
                        </span>log &lt;| sprintf <span style="color:maroon;">"beatenOffer(%d)" </span>maxBid
                        processBid(maxBid, current)
                    | AuctionConcluded(seller, maxBidder) <span style="color:blue;">-&gt;
                        </span>log <span style="color:maroon;">"auctionConcluded"
                        </span>c &lt;-- Stop
                        (max, current)
                    | AuctionOver <span style="color:blue;">-&gt;
                        </span>log <span style="color:maroon;">"auctionOver"
                        </span>c &lt;-- Stop
                        (max, current))
                 (0,0)
c</pre>

Something that I like about agents is the fact that you need to understand just small snippets of code at the time. For example, you can read the processing for BestOffer and figure out if it makes sense.&#160; I have an easy time personalizing them as in : “Ok, the guy just got a notification that there has been a better offer, what is he going to do next?”.

The code should be self explanatory for the most part. In essence, if you can offer more, do it otherwise wait for the auction to end. I’m not even sure the processing is completely right. I confess I’m just trying to do the same as Matthews code from the link above.

We can then start up the whole thing and enjoy the cool output.

<pre class="code"><span style="color:blue;">open </span>Auction
(client 1 20 200) &lt;-- StartBidding
(client 2 10 300) &lt;-- StartBidding
(client 3 30 150) &lt;-- StartBidding
Console.ReadLine() |&gt; ignore  </pre>

Now for the nasty part. Implementing the framework.