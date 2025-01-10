---
id: 403
title: 'Downloading stock prices in F# - Part V - Adjusting historical data'
date: 2008-09-26T16:04:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/09/26/downloading-stock-prices-in-f-part-v-adjusting-historical-data/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/09/26/downloading-stock-prices-in-f-part-v-adjusting-historical-data.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "8966978"
orig_parent_id:
  - "8966978"
orig_thread_id:
  - "608470"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/09/26/downloading-stock-prices-in-f-part-v-adjusting-historical-data.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Downloading stock prices in F#  - Part V  - Adjusting historical data" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/09/26/downloading-stock-prices-in-f-part-v-adjusting-historical-data/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other parts: Part I  - Data modeling Part II  - Html scraping Part III  - Async loader for prices and divs Part IV  - Async loader for splits Part VI  - Code posted&nbsp; Here is the problem. When you download prices/divs/splits from Yahoo you get a strange mix of historical numbers and adjusted numbers. To..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Downloading stock prices in F#  - Part V  - Adjusting historical data" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/09/26/downloading-stock-prices-in-f-part-v-adjusting-historical-data/" />
    <meta name="twitter:description" content="Other parts: Part I  - Data modeling Part II  - Html scraping Part III  - Async loader for prices and divs Part IV  - Async loader for splits Part VI  - Code posted&nbsp; Here is the problem. When you download prices/divs/splits from Yahoo you get a strange mix of historical numbers and adjusted numbers. To..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - fsharp
---
Other parts:

  * [Part I  - Data modeling](http://blogs.msdn.com/lucabol/archive/2008/08/29/downloading-stock-prices-in-f-part-i-data-modeling.aspx) 
  * [Part II  - Html scraping](http://blogs.msdn.com/lucabol/archive/2008/09/05/downloading-stock-prices-in-f-part-ii-html-scraping.aspx) 
  * [Part III  - Async loader for prices and divs](http://blogs.msdn.com/lucabol/archive/2008/09/12/downloading-stock-prices-in-f-part-iii-async-loader-for-prices-and-divs.aspx) 
  * [Part IV  - Async loader for splits](http://blogs.msdn.com/lucabol/archive/2008/09/19/downloading-stock-prices-in-f-part-iv-async-loader-for-splits.aspx)
  * [Part VI  - Code posted](http://blogs.msdn.com/lucabol/archive/2008/10/20/downloading-stock-prices-in-f-part-vi-code-posted.aspx)&nbsp;

Here is the problem. When you download prices/divs/splits from Yahoo you get a strange mix of historical numbers and adjusted numbers. To be more precise, the dividends are historically adjusted. The prices are not adjusted, but there is one last column in the data for Adjusted close. If you don't know what 'adjusted' means in this context read [here](http://help.yahoo.com/l/us/yahoo/finance/quotes/quote-12.html).

The problem with using the 'adjusted close' column is that, for a particular date in the past, 'adjusted close' changes whenever the company pays a dividend or splits its stock. So if I retrieve the value on two different days I might get different numbers because, in the meantime, the company paid a dividend. This prevents me from storing a subset of the data locally and then retrieving other subsets later on. It also has the limitation that just the closing price is present while I might need adjusted opening price, adjusted high price or even adjusted volume depending on the operations I want to perform on the data (i.e. calculating oscillators or volume-adjusted moving averages).

The solution I came up with is to download the data and transform it to an 'asHappened' state. This state is simply an unadjusted version of what happened in the past. Data in this state is not going to change in the future, which means that I can safely store it locally. I can then on demand produce 'historically adjusted' data whenever I need to.

Ok, to the code. As it often happens, I need some auxiliary functions before I get to the core of the algorithms. The first one is a way to compare two observations, I will use it later on to sort a list of observations.

```fsharp
let compareObservations obs1 obs2 =
    if obs1.Date <> obs2.Date then obs2.Date.CompareTo(obs1.Date)
    else
        match obs1.Event, obs2.Event with
            | Price _, Price _ | Div _, Div _ | Split _, Split _
                -> failwith "Two same date/ same kind observations"
            | Price _, _  -> -1
            | _, Price _  -> 1
            | _           -> 
```

This is rather simple. If the dates of these observations are different, just compare them. If they are the same then the two observations cannot be of the same type (i.e. I cannot have two prices for a particular date). Given that they are not of the same, then &(&^%!#$!4. Crap, that teaches me to put comments in my code! I think I'm putting the price information first, but I'm not sure. Anyhow my universal excuse not to figuring it out is that the testcases succeed so I must be doing it right (how lame, testcase-addiction I guess).

The next auxiliary function is just a wrapper over fold. I always tend to wrap fold calls in a method with a better name because I remember the old times when I didn't know what fold was. I want a reader of my code to be able to understand it even if they are not familiar with fold (the 'universal functional Swiss-Army-Knife). This function is a map that needs to know the value of an accumulator to correctly perform its mapping over each element.

```fsharp
let mapAcc acc newAccF newItemF inl =
    let foldF (acc, l) x = newAccF acc x, (newItemF acc x)::l
    let _, out = inl |> List.fold_left foldF (acc, [])
    out
```

Apart from the implementation details, this function takes an accumulator, an accumulator function, an item function and an input list. For each element in the list it calculates two things:

  1. a new value for the accumulator: newAccumulatorValue = <u>newAccF</u> oldAccValue itemValue 
  2. a new value for the item: new ItemValue = <u>newItemF</u> accValue oldItemValue 

Maybe there is a standard functional way to do such a thing with a specific name that I'm not aware of. [Luke](http://blogs.msdn.com/lukeh/default.aspx) might know. He is my resident <u>fold</u> expert.

All right, now to he main algorithm.

```fsharp
let asHappened splitFactor observations =
    let newSplitFactor splitFactor obs =
        match obs.Event with
            | Split(factor) -> splitFactor * factor
            | _             -> splitFactor
    let newObs splitFactor obs =
        let date = obs.Date
        let event = match obs.Event with
                        | Price(p)                  -> Price(p)
                        | Div(amount)               -> Div(amount * splitFactor)
                        | Split(factor)             -> Split(factor)
        {Date = date; Event = event}
    observations
    |> List.sort compareObservations
    |> mapAcc splitFactor newSplitFactor newObs
```

To understand what's going on start from the bottom. I'm taking the observation list downloaded from Yahoo and sorting it using my <u>compareObservations</u> function. I then take the resulting list and apply the previously described <u>mapAcc</u> to it. For this function splitFactor is the accumulator, newSplitFactor is the accumulator function and newObs is the function that generate a new value for each item in the list.

<u>NewSplitFactor</u> is trivial: every time it sees a Split observation it updates the value of the split factor. That's it. <u>NewObs</u> is rather simple as well. Every time it sees a dividend, it 'unadjust' it by multiplying its amount by the split factor. The end result is to transform the dividends downloaded from Yahoo (which are adjusted) to an unadjusted state. I could have filtered out the price observations before doing all of this and add them back afterward, but didn't. It'd probably be slower

Now that I can recreate the state of the world as it was at a particular point in time, what if I want to adjust the data? I can call <u>adjusted</u>

```fsharp
let adjusted (splitFactor, lastDiv, oFact, hFact, lFact, cFact, vFact)
                                                                   asHappenedObs =
    let newFactor (splitFactor, lastDiv, oFact, hFact, lFact, cFact, vFact) obs =
        match obs.Event with
            | Split(split)  ->
                 splitFactor * split, lastDiv, oFact, hFact, lFact, cFact, vFact
            | Div(div)      -> splitFactor, div, oFact, hFact, lFact, cFact, vFact
            | Price(p)      ->
                 splitFactor, 0.<money>, oFact / (1. - lastDiv / p.Open),
                 hFact / (1. - lastDiv / p.High), lFact / (1. - lastDiv / p.Low),
                 cFact / (1. - lastDiv / p.Close), vFact / (1. - lastDiv / p.Close)
    let newObs (splitFactor, lastDiv, oFact, hFact, lFact, cFact, vFact) obs =
        let date = obs.Date
        let event = match obs.Event with
                        | Price(p)          ->
                            Price({Open = p.Open / splitFactor / oFact;
                            High = p.High / splitFactor / hFact;
                            Low = p.Low / splitFactor / lFact;
                            Close = p.Close / splitFactor / cFact;
                            Volume = p.Volume / splitFactor / vFact })
                        | Div(amount)       -> Div (amount / splitFactor)
                        | Split(split)      -> Split(split)
        {Date = date; Event = event}
    asHappenedObs
        |> List.sort compareObservations
        |> mapAcc (splitFactor, lastDiv, oFact, hFact, lFact, cFact, vFact)
                                                                  newFactor newObs
        |> List.filter (fun x -> match x.Event with Split(_) -> false | _ -> true)        
```

Wow, ok, this looks messy. Let's go through it. Starting from the bottom: sort the observations, perform the right algorithm and filter away all the splits. It doesn't make sense to have splits in adjusted data.

The interesting piece is the <u>mappAcc</u> function. It take a tuple of factors as accumulator and the usual two functions to update such tuple and create new observations. The <u>newObs</u> function creates a new Observation using the factors in the accumulator tuple. Notice how the dividends are divided by the <u>splitFactor</u> (which is the opposite of our <u>asHappened</u> algorithm where we were multiplying them). Also notice how the prices are divided by both the <u>splitFactor</u> and the pertinent price factor. This is needed because the prices need to be adjusted by the dividends paid out and the adjustment factor is different for each kind of price (i.e. open, close, etc). The <u>newFactor</u> function simply updates all the factors depending on the current observation.

Notice how <u>asHappened</u> and <u>adjusted</u> are structurally similar. This is an artifact of having a functional approach to writing code: it kind of forces you to identify these commonality in the way an algorithm behave and abstract them out (in this case in the <u>mapAcc</u> function). You often discover that such abstracted-out pieces are more generally useful than the case at hand.
