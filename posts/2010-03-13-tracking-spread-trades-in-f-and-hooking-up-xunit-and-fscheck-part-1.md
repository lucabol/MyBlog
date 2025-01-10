---
id: 30
title: 'Tracking spread trades in F# (and hooking up XUnit and FsCheck) – Part 1'
date: 2010-03-13T01:18:37+00:00
author: lucabol
layout: post
guid: http://lucabolognese.wordpress.com/2010/03/13/tracking-spread-trades-in-f-and-hooking-up-xunit-and-fscheck-part-1/
categories:
  - fsharp
  - Investing
tags:
  - fsharp
  - Financial
---
I have a bunch of spread trades open. Spread trades are trades where you buy something and you sell something else generally in the same amount. You hope to profit from the widening of the spread between the price of the two instruments.
  
I place stop loss orders or trailing stops for all my trades. I have various tool that automatically notify me when a stop loss or trailing stop is hit. For spread trades I don't have such a tool, hence I decided to build it.
  
I defined maximum adverse excursion for a spread trade as the percentage difference between the current value of 'long price' / 'short price' and its maximum value from the point the trade was placed (aka Current('long price' / 'short price') / max ('long price' / 'short price') – 1 ). This goes from 0 to 100. If the maximum adverse excursion is larger than the trailing stop (using closing prices only), then I want to be notified by email.
  
I decided to create a simple exe and use Task Scheduler to run it at the end of the trading day. The program reads a file with all the open spread trades, downloads their prices, calculates maximum adverse excursion and sends an email if it is larger than the trailing stop. I also built a little WPF veneer to manipulate the configuration file.
  
Here is what my _common.fs_ file looks like.

```fsharp
namespace Spread
module internal Common =
    open System
    let internal isValidDate s =
        let v, _ = DateTime.TryParse(s)
        v
    let internal isValidTrailingStop s =
        let v1, n = Int32.TryParse(s)
        if not(v1) then
            false
        else
            n >= 0 && n <= 100
    let internal isValidTicker (t:string) = not(t.Contains(","))
    let internal isValidLine (l:string) = l.Split([|','|]).Length = 4
    let internal elseThrow message expression = if not(expression) then raise message
    let internal elseThrowi i message expression = if not(expression) then failwith (sprintf "On line %i : %s" i message)
```

Notice the _isValidTicker_ function. Yep, I'm using a CSV file to store the list of spread trades. Also I often end up using the little _elseThrow_ functions that I originally used in the [Excel functions library](http://code.msdn.microsoft.com/FinancialFunctions/Wiki/View.aspx?title=Home) to check preconditions.
  
Here is an example of using them for the _parseLine_ function:

```fsharp
// parse a line in the csv config file, assumes valid csv, dates and trailing stop in [0,100]
let internal parseLine lineNumber line =
    isValidLine line                |> elseThrowi lineNumber "badly formatted line"
    let values = line.Split([|','|])
    isValidDate values.[0]          |> elseThrowi lineNumber "badly formatted date"
    isValidTicker values.[1]        |> elseThrowi lineNumber "long ticker has a comma in it"
    isValidTicker values.[2]        |> elseThrowi lineNumber "short ticker has a comma in it"
    isValidTrailingStop values.[3]  |> elseThrowi lineNumber "trailing stop has to be between 0 and 100 included"
    DateTime.Parse(values.[0]), values.[1].Trim(), values.[2].Trim(), int values.[3]
```

As you can see, the csv format is (dateOfTrade, longTicker, shortTicker, trailingStop). Let's now look and the FsCheck testcase for this function.

```fsharp
let writeLine (date:DateTime) (tickerLong:string) (tickerShort:string) (trailingStopValue:int) =
    sprintf "%s,%s,%s,%i" (date.ToShortDateString()) tickerLong tickerShort trailingStopValue
[<Fact;Category("Fast Tests")>]
let can_parse_valid_lines () =
    let  prop_parseLine (lineNumber:int) date tickerLong tickerShort trailingStopValue =
        let line = writeLine date tickerLong tickerShort trailingStopValue
        let values = line.Split([|','|])
        (isValidLine(line) && isValidDate values.[0] && isValidTicker values.[1] && isValidTicker values.[2]
                                                                                        && isValidTrailingStop values.[3])
            ==> lazy
                let actual = parseLine lineNumber line
                (date, tickerLong.Trim(), tickerShort.Trim(), trailingStopValue) = actual
    check config prop_parseLine
```

In FsCheck you state properties of your functions and FsCheck generates random values to test them. In this case I'm asserting that, given a _date, tickerLong, tickerShort, trailingStopValue_, I can write them to a string, read them back and I get the same values. Frankly, I was skeptical on the utility of such exercise, but I was wrong. That's how I discovered that tickers cannot have commas in them (among other things).
  
To hook up FsCheck and XUnit (aka to run FsCheck property checking as normal testcases), you need to write the below black magic code.

```fsharp
let xUnitRunner =
    { new IRunner with
        member x.OnArguments(_,_,_) = ()
        member x.OnShrink(_,_) = ()
        member x.OnFinished(name, result) =
            match result with
                | True data -> Assert.True(true)
                | _ -> failwith (testFinishedToString name result)
    }
let config = {quick with Runner = xUnitRunner}
```

Also, to run XUnit with your brand new .net 4.0 project, you need to add xunit.gui.exe.config to the XUnit directory with the following content:
  
<configuration>
  
<startup>
  
<requiredRuntime version=v4.0.20506&#8243; safemode=true/>
  
</startup>
  
</configuration>
  
While we are talking about such trivialities, I compile my testcases as executable, so that I can easily run them under debug. I also add the InternalsVisibleTo attribute, so that I can test internal stuff. Many of my algorithms are in internal functions and I want to test them in isolation.

```fsharp
[<assembly:InternalsVisibleTo("SpreadTrackingTests")>]
    do
```

Given the previous function, I can then parse text and files with the following:

```fsharp
let internal parseText (lines:string) = lines.Trim().Split([|'\n'|]) |> Array.mapi parseLine
let public parseFile fileName = File.ReadAllText fileName |> parseText
```

I need to load closing prices. I'm using [my own library](http://code.msdn.microsoft.com/DownloadStockPrices) to load prices. That library is pretty badly designed. Also, the function below should be factorized in several sub-functions. It kind of shows how you can write spaghetti code in a beautiful functional language as F# if you really try hard. But let's not worry about such subtleties for now …

```fsharp
let internal loadClosingPrices (endDate:DateTime) tickersStartDate  =
    // format parameters to conform to loadTickersAsync
    let tickersLong, tickersShort =
        tickersStartDate
        |> Array.map (fun (startDate:DateTime, ticker1:string, ticker2:string, _) ->
                (ticker1, {Start = startDate; End = endDate}), (ticker2, {Start = startDate; End = endDate}))
        |> Array.unzip
    let prices = tickersShort
                 |> Array.append tickersLong
                 |> Array.toList
                 |> loadTickersAsync
                 |> Async.RunSynchronously
                 |> Array.map (fun (ticker, span, obs) -> ticker, obs (*|> asHappened 1. |> adjusted adjStart*))
    let len = tickersLong.Length
    let longObs = Array.sub prices 0 len
    let shortObs = Array.sub prices len len
    // removes divs and splits
    let choosePrices observation = match observation.Event with Price(pr) -> Some(observation) | _ -> None
    let combineOverTickerObservations f tickerObservations =
        tickerObservations
        |> Array.map (fun (ticker, observations) ->
                                            ticker,
                                            observations |> List.choose f |> List.rev)
    let longPrices = combineOverTickerObservations choosePrices longObs
    let shortPrices = combineOverTickerObservations choosePrices shortObs
    longPrices, shortPrices
```

In the above, _tickerStartDate_ is an array of (trade date \* long ticker \* short ticker * trailingStop) which is what is produced by our _parseLine_ function. The function first separates out long tickers from short ones.

```fsharp
let tickersLong, tickersShort =
    tickersStartDate
    |> Array.map (fun (startDate:DateTime, ticker1:string, ticker2:string, _) ->
            (ticker1, {Start = startDate; End = endDate}), (ticker2, {Start = startDate; End = endDate}))
    |> Array.unzip
```

It then puts them together again in a single Array, to be able to pass it to the loadTickerAsync functions. It runs the function, waits for the results and then returns an array of (ticker * observations).

```fsharp
let prices = tickersShort
             |> Array.append tickersLong
             |> Array.toList
             |> loadTickersAsync
             |> Async.RunSynchronously
             |> Array.map (fun (ticker, span, obs) -> ticker, obs |> asHappened 1. |> adjusted adjStart)
```

The data is downloaded as it comes from Yahoo, which is a mix of adjusted and not adjusted data. _asHappened_ transforms it so that everything is as it really happened, _adjusted_ then adjusts it for the effect of dividends and splits. Think of this two function as 'make the data right'.
  
We then split them again to get the long and short series. The point of merging them and splitting them is to call _loadTickersAsync_ just once instead of twice. There are better ways to do it.

```fsharp
let len = tickersLong.Length
        let longObs = Array.sub prices 0 len
        let shortObs = Array.sub prices len len
```

At this point we remove the observations that represents dividends or splits, as we are interested just in prices and we return the resulting observations.

```fsharp
let choosePrices observation = match observation.Event with Price(pr) -> Some(observation) | _ -> None
let combineOverTickerObservations f tickerObservations =
    tickerObservations
    |> Array.map (fun (ticker, observations) ->
                                        ticker,
                                        observations |> List.choose f |> List.rev)
let longPrices = combineOverTickerObservations choosePrices longObs
let shortPrices = combineOverTickerObservations choosePrices shortObs
longPrices, shortPrices
```

The List.rev at the end is interesting. Somewhere in the loadTickerAsync/asHappened/adjusted triad of functions I end up reversing the list. I should fix the bug instead of workaround it, but this is just a blog post, not production code, so I'll let it slip.
  
Now that we have our price observations, we need to extract the price values and calculate the sequence of ratios (long price / short price).

```fsharp
let internal calcRatioSeries longPrices shortPrices =
    let extractPrice obs = match obs.Event with Price(pr) -> pr.Close | _ -> failwith "At this point divs and splits should have been removed"
    let longValues = longPrices |>  List.map extractPrice
    let shortValues = shortPrices |> List.map extractPrice
    shortValues |> List.map2 (/) longValues
```

Having this ratio series, we can calculate the maximum adverse excursion, incorrectly called trailing stop below.

```fsharp
let internal calcTrailingStop ratioSeries = List.head ratioSeries / List.max ratioSeries - 1.
```

We then create a function that puts it all together.

```fsharp
type public Result = {RatioName:string; CurrentTrailing:int; TrailingStop:int} with
    override x.ToString() = x.RatioName + "\t\t" + x.CurrentTrailing.ToString() + "\t\t" + x.TrailingStop.ToString()
// reads a csv file (startDate, longTicker, shortTicker, trailingStop) and returns an array of results
let public processFile fileName endDate =
    let fileInfo = parseFile fileName
    let longPrices, shortPrices = loadClosingPrices endDate fileInfo
    let ratioSeries = Array.map2 (fun l s -> fst l + "/" + fst s, calcRatioSeries (snd l) (snd s)) longPrices shortPrices
    ratioSeries |> Array.mapi (fun i (name, series) ->
                    let (_,_,_,ts) = fileInfo.[i]
                    {RatioName = name; CurrentTrailing = - int (Math.Round (calcTrailingStop series * 100., 0));
                                                                                                       TrailingStop = ts})
```

The function takes a fileName and an endDate, the latter parameter is for the sake of testcases that has to work in the past, so that the data doesn't change on them.
  
Now we need to send an email. The code below works for me:

```fsharp
let sendEmail smtpServer port fromField toField subject body (user:string) (password:string) =
    let client = new SmtpClient(smtpServer, port)
    client.Credentials <- new NetworkCredential(user, password)
    client.EnableSsl <- true
    client.Send(fromField, toField, subject, body)
// gets the password from a file under C: so that when I post it on my blog I don't forget to delete it
let getPassword () =
    File.ReadAllText(@"D:\Documents and Settings\Luca\My Documents\config.txt")
```

Almost done, in the main part of the program, we gather the data, create the content of the email and send it out:

```fsharp
do
    let file = "spreads.csv"
    let spreads = processFile file DateTime.Today
    let mutable builder = new System.Text.StringBuilder()
    builder <- builder.AppendLine("Name\t\tCurrent\t\tStop")
    for s in spreads do
        builder <- builder.AppendLine(s.ToString())
    let password = getPassword()
    sendEmail "smtp.gmail.com" 587 "***@***.com" "***@***.com" "Alert Trigger Spread" (builder.ToString())
                                                                                           "lucabolg@gmail.com" password;;
```

Next stop, the WPF veneer on top of the file.
