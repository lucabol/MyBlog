---
id: 413
title: 'Downloading stock prices in F# - Part IV - Async loader for splits'
date: 2008-09-19T17:59:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/09/19/downloading-stock-prices-in-f-part-iv-async-loader-for-splits/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/09/19/downloading-stock-prices-in-f-part-iv-async-loader-for-splits.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "8959474"
orig_parent_id:
  - "8959474"
orig_thread_id:
  - "607256"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/09/19/downloading-stock-prices-in-f-part-iv-async-loader-for-splits.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Downloading stock prices in F#  - Part IV  - Async loader for splits" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/09/19/downloading-stock-prices-in-f-part-iv-async-loader-for-splits/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other parts: Part I  - Data modeling Part II  - Html scraping Part III  - Async loader for prices and divs Part V  - Adjusting historical data Part VI  - Code posted Downloading splits is a messy affair. The problem is that Yahoo doesn't give you&nbsp; a nice comma-delimitated stream to work with. You have..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Downloading stock prices in F#  - Part IV  - Async loader for splits" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/09/19/downloading-stock-prices-in-f-part-iv-async-loader-for-splits/" />
    <meta name="twitter:description" content="Other parts: Part I  - Data modeling Part II  - Html scraping Part III  - Async loader for prices and divs Part V  - Adjusting historical data Part VI  - Code posted Downloading splits is a messy affair. The problem is that Yahoo doesn't give you&nbsp; a nice comma-delimitated stream to work with. You have..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - fsharp
  - Financial
---
Other parts:

  * [Part I  - Data modeling](http://blogs.msdn.com/lucabol/archive/2008/08/29/downloading-stock-prices-in-f-part-i-data-modeling.aspx)
  * [Part II  - Html scraping](http://blogs.msdn.com/lucabol/archive/2008/09/05/downloading-stock-prices-in-f-part-ii-html-scraping.aspx)
  * [Part III  - Async loader for prices and divs](http://blogs.msdn.com/lucabol/archive/2008/09/12/downloading-stock-prices-in-f-part-iii-async-loader-for-prices-and-divs.aspx)
  * [Part V  - Adjusting historical data](http://blogs.msdn.com/lucabol/archive/2008/09/26/downloading-stock-prices-in-f-part-v-adjusting-historical-data.aspx)
  * [Part VI  - Code posted](http://blogs.msdn.com/lucabol/archive/2008/10/20/downloading-stock-prices-in-f-part-vi-code-posted.aspx)

Downloading splits is a messy affair. The problem is that Yahoo doesn't give you&nbsp; a nice comma-delimitated stream to work with. You have to parse the Html yourself (and it can be on multiple pages). At the end of the post, the overall result is kind of neat, but to get there we need a lot of busywork.

First, let's define a function that constructs the correct URL to download splits from. Notice that you need to pass a page number to it.

```fsharp
let splitUrl ticker span page =
    "http://finance.yahoo.com/q/hp?s=" + ticker + "&a="
    + (span.Start.Month - 1).ToString() + "&b=" + span.Start.Day.ToString() + "&c=" 
    + span.Start.Year.ToString() + "&d=" + (span.End.Month - 1).ToString() + "&e="
    + span.End.Day.ToString() + "&f=" + span.End.Year.ToString() + "&g=v&z=66&y="
    + (66 * page).ToString();
```

The reason for this particular url format (i.e. 66 * page) is completely unknown to me. I also have the feeling that it might change in the future. Or maybe not given how many people rely on it.

I then describe the driver function for loading splits:

```fsharp
let rec loadWebSplitAsync ticker span page splits =
    let parseSplit text splits =
        List.append splits (parseSplits (scrapHtmlRows text)),
                                           not(containsDivsOrSplits (scrapHtmlCells text))
    async {
        let url = splitUrl ticker span page
        let! text = loadWebStringAsync url
        let splits, beyondLastPage = parseSplit text splits
        if beyondLastPage then return splits else
                                 return! loadWebSplitAsync ticker span (page + 1) splits }
```

This is a bit convoluted (it is an Async recursive function). Let's go through it in some detail. First there is a nested function <u>parseSplit</u>. It takes an html string and a list of observations and returns a tuple of two elements. The first element is the same list of observations augmented with the splits found in the text. The second element is a boolean that is true if we have navigated beyond the last page for the splits.

The function to test that we are beyond the last page is the following:

```fsharp
let containsDivsOrSplits cells =
    cells |> Seq.exists
        (fun (x:string) -> Regex.IsMatch(x, @"$.+Dividend", RegexOptions.Multiline)
                           || Regex.IsMatch(x, "Stock Split"))  
```

This function just checks if the words Stock Split or Dividend are anywhere in the table. If they aren't, then we have finished processing the pages for this particular ticker and date span.

The function to extract the splits observations from the web page takes some cells (a <u>seq<seq<string>>)</u> as input and returns an observation list. It is reproduced below:

```fsharp
let parseSplits rows =
    let parseRow row =
        if row |> Seq.exists (fun (x:string) -> x.Contains("Stock Split"))
        then
            let dateS = Seq.hd row
            let splitS = Seq.nth 1 row
            let date = DateTime.Parse(dateS)
            let regex = Regex.Match(splitS,@"(d+)s+:s+(d+)s+Stock Split",
                                                                   RegexOptions.Multiline)
            let newShares = shares (float (regex.Groups.Item(1).Value))
            let oldShares = shares (float (regex.Groups.Item(2).Value))
            Some({Date = date; Event = Split(newShares / oldShares)})
        else None
    rows |> Seq.choose parseRow |> Seq.to_list
```

It just take a bunch of rows and choose the ones that contain stock split information. For these, it parses the information out of the text and creates a Split Observation out of it. I think it is intuitive what the various Seq functions do in this case. Also note my overall addiction to the pipe operator ( |> ). In my opinion this is the third most important keyword in F# (after 'let' and 'match').

Let's now go back to the loadWebSplitAsync function and discuss the rest of it. In particular this part:

```fsharp
async {
    let url = splitUrl ticker span page
    let! text = loadWebStringAsync url
    let splits, beyondLastPage = parseSplit text splits
    if beyondLastPage then return splits else
        return! loadWebSplitAsync ticker span (page + 1) splits }
```

First of all it is an Async function. You should expect some Async stuff to go on inside it. And indeed, after forming the URL in the first line, the very next line is a call to <u>loadWebStringAsync</u>. We discussed this one in the previous installment. It just asynchronously loads a string from an URL. Notice the bang after 'let'. This is your giveaway that async stuff is being performed.

The result of the async request is parsed to extract splits. Also, the <u>beyondLastPage</u> flag is set if we have finished our work. If we have, we return the split observation list; if we haven't, we do it again incrementing the page number to load the html text from.

Now that we have all the pieces in places, we can wrap up the split loading stuff inside this facade function:

```fsharp
let loadSplitsAsync ticker span = loadWebSplitAsync ticker span 0 []
```

And finally put together the results of this post and the previous one with the overall function-to-rule-them-all:

```fsharp
let loadTickerAsync ticker span =
    async {
        let prices = loadPricesAsync ticker span
        let divs =  loadDivsAsync ticker span
        let splits = loadSplitsAsync ticker span
        let! prices, divs, splits = Async.Parallel3 (prices, divs, splits)
        return prices |> List.append divs |> List.append splits
        }
```

All right, that was a lot of work to get to this simple thing. This is a good entry point to our price/divs/split loading framework. It has the right inputs and outputs: it takes a ticker and a date span and returns an Async of a list of observations. Our caller can decide when he wants to execute the returned Async object.

Notice that in the body of the function I call <u>Async.Parallel</u>. This is debatable. A more flexible solution is to return a tuple containing three Asyncs (prices, divs, splits) and let the caller decide how to put them together. I decided against this for simplicity reasons. This kind of trade-off is very common in Async programming: giving maximum flexibility to your caller against exposing something more understandable.

I have to admit I didn't enjoy much writing (and describing) all this boilerplate code. I'm sure it can be written in a better way. I might rewrite plenty of it if I discover bugs. I kind of like the end result though. <u>loadTickerAsync</u> has an overall structure I'm pretty happy with.

Next post,&nbsp; some algorithms with our observations
