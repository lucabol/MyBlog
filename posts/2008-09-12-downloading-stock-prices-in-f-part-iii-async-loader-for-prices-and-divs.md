---
id: 423
title: 'Downloading stock prices in F# - Part III - Async loader for prices and divs'
date: 2008-09-12T16:18:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/09/12/downloading-stock-prices-in-f-part-iii-async-loader-for-prices-and-divs/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/09/12/downloading-stock-prices-in-f-part-iii-async-loader-for-prices-and-divs.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "8948077"
orig_parent_id:
  - "8948077"
orig_thread_id:
  - "605926"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/09/12/downloading-stock-prices-in-f-part-iii-async-loader-for-prices-and-divs.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Downloading stock prices in F#  - Part III  - Async loader for prices and divs" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/09/12/downloading-stock-prices-in-f-part-iii-async-loader-for-prices-and-divs/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other parts: Part I  - Data modeling Part II  - Html scraping Part IV  - Async loader for splits Part V  - Adjusting historical data Part VI  - Code posted It is now time to load our data. There is a bit of uninteresting code to start with, but things get interesting afterward. Let's start..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Downloading stock prices in F#  - Part III  - Async loader for prices and divs" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/09/12/downloading-stock-prices-in-f-part-iii-async-loader-for-prices-and-divs/" />
    <meta name="twitter:description" content="Other parts: Part I  - Data modeling Part II  - Html scraping Part IV  - Async loader for splits Part V  - Adjusting historical data Part VI  - Code posted It is now time to load our data. There is a bit of uninteresting code to start with, but things get interesting afterward. Let's start..." />
    
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
  * [Part IV  - Async loader for splits](http://blogs.msdn.com/lucabol/archive/2008/09/19/downloading-stock-prices-in-f-part-iv-async-loader-for-splits.aspx)
  * [Part V  - Adjusting historical data](http://blogs.msdn.com/lucabol/archive/2008/09/26/downloading-stock-prices-in-f-part-v-adjusting-historical-data.aspx)
  * [Part VI  - Code posted](http://blogs.msdn.com/lucabol/archive/2008/10/20/downloading-stock-prices-in-f-part-vi-code-posted.aspx)

It is now time to load our data. There is a bit of uninteresting code to start with, but things get interesting afterward. Let's start with functions that create the right URLs to download prices and dividends. We'll talk about splits in the next installment.

```fsharp
let commonUrl ticker span =
    @"http://ichart.finance.yahoo.com/table.csv?s=" + ticker + "&a="
    + (span.Start.Month - 1).ToString() + "&b=" + span.Start.Day.ToString() + "&c="
    + span.Start.Year.ToString() + "&d=" + (span.End.Month - 1).ToString() + "&e=" 
    + span.End.Day.ToString() + "&f=" + span.End.Year.ToString()
let priceUrl ticker span = commonUrl ticker span + "&g=d&ignore=.csv"
let divUrl ticker span = commonUrl ticker span + "&g=v&ignore=.csv"
```

We will also need to construct an observation given a comma delimitated line of text. Again, for spits things will be harder.

```fsharp
let parsePrice (line: string) =
    let tokens = line.Split([|','|])
    { Date = DateTime.Parse(tokens.[0]);
      Event = Price ({Open = money (Double.Parse(tokens.[1])) ;
      High = money (Double.Parse(tokens.[2]));
      Low = money (Double.Parse(tokens.[3])); Close = money (Double.Parse(tokens.[4]));
      Volume = volume (Double.Parse(tokens.[5]))})}
let parseDiv (line: string) =
    let tokens = line.Split([|','|])
    let date = DateTime.Parse(tokens.[0])
    let amount = money (Double.Parse(tokens.[1]))
    {Date = date; Event = Div amount}        
```

Nothing noteworthy about this code. We have a couple of other 'infrastructure pieces before we get to the Async pieces. The next function is recursive. It takes a StringReader and reads lines out of it. For each line it calls a parsing function that takes the line as input and returns an object as output. The function gathers all such objects in the <u>listOfThings</u> list. If you are new to F# the following construct (parseLineFunc line:: listOfThings) means: execute the parseLineFunc with argument line, take the result and create a list that has the result as head and listOfThings as tail).

```fsharp
let rec loadFromLineReader (reader:StringReader) listOfThings parseLineFunc =
    match  reader.ReadLine () with
    | null  -> listOfThings
    | line  -> loadFromLineReader reader (parseLineFunc line::listOfThings) parseLineFunc        
```

The next function is rather uninteresting. It just converts a string to a <u>StringReader</u>, cut out the first line (header) and calls <u>loadFromLineReader</u>.

```fsharp
let loadFromLineString text listOfThings parseLineFunc =
    let reader = new StringReader(text)
    reader.ReadLine ()|> ignore // skip header
    loadFromLineReader reader listOfThings parseLineFunc
```

We now come to the first Async function. But what is an Async function? There are several possible technically correct definition as: it is an instance of the monad pattern or it is a function that returns an Async object or it is a way to release your thread to the thread pool. These definition don't help me much. I need something intuitive to latch one.

The way that I personally visualize it is: there are things in the world that are very good at executing certain tasks and like to be hit by multiple parallel requests for these tasks. They'd like me to give them their workload and get out of their way. They'll call me when they are done with it. These 'things' are disk drives, web servers, processors, etc Async is a way to say: hey, go and do this, call me when you are done.

Now, you can [call the asynchronous APIs directly](http://msdn.microsoft.com/en-us/library/aa719595(VS.71).aspx), or you can use the nice F# language structures to do it. Let's do the latter.

```fsharp
let loadWebStringAsync url =
    async {
        let req = WebRequest.Create(url: string)
        use! response = req.AsyncGetResponse()
        use reader = new StreamReader(response.GetResponseStream())
        return! reader.AsyncReadToEnd()}
```

This function retrieves a web page as a string asynchronously. Notice that even if the code looks rather normal, this function will likely be executed on three different thread. The first thread is the one the caller of the function lives on. The function <u>AsyncGetResponse</u> causes the thread to be returned to the thread pool waiting for a response back from the web server. Once such a response arrives, the execution resumes on a different thread until <u>AsyncReadToEnd</u>. That instruction returns the execution thread to the thread pool. A new thread is then instantiated when the string has been completely read. The good thing is that all of this is not explicitly managed by the programmer. The compiler 'writes the code' to make it all happen. You just have to follow a set of simple conventions (i.e. putting exclamation marks in the right place).

The return result of this function is an <u>Async<string></u>, which is something that, when executed, returns a string. I cannot emphasize this enough: always look at the signature of your F# functions. Type inference can be tricky

Async is somehow contagious. If you are calling an Async function you have to decide if propagate the Asyncness to your callers or remove it by executing the function. Often propagating it is the right thing to do as your callers might want to batch your function with other aync ones to be executed together in parallel. Your callers have more information than you do and you don't want to short-circuit them. The following function propagates ayncness.

```fsharp
let loadFromUrlAsync url parseFunc =
    async {
        let! text = loadWebStringAsync url
        return loadFromLineString text [] parseFunc}
```

Let's see how the functions presented to this point compose to provide a way to load prices and dividends (splits will be shown afterward).

```fsharp
let loadPricesAsync ticker span = loadFromUrlAsync (priceUrl ticker span) parsePrice
let loadDivsAsync ticker span = loadFromUrlAsync (divUrl ticker span) parseDiv
```

This composition of functions is very common in functional code. You construct your building blocks and assemble them to achieve your final goal. Functional programming is good at almost forcing you to identify the primitive blocks in your code. All right, next in line is how to load splits.
