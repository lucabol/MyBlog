---
id: 30
title: 'Tracking spread trades in F# (and hooking up XUnit and FsCheck) – Part 1'
date: 2010-03-13T01:18:37+00:00
author: lucabol
layout: post
guid: http://lucabolognese.wordpress.com/2010/03/13/tracking-spread-trades-in-f-and-hooking-up-xunit-and-fscheck-part-1/
permalink: /2010/03/13/tracking-spread-trades-in-f-and-hooking-up-xunit-and-fscheck-part-1/
categories:
  - fsharp
  - Investing
tags:
  - fsharp
  - Financial
---
I have a bunch of spread trades open. Spread trades are trades where you buy something and you sell something else generally in the same amount. You hope to profit from the widening of the spread between the price of the two instruments.
  
I place stop loss orders or trailing stops for all my trades. I have various tool that automatically notify me when a stop loss or trailing stop is hit. For spread trades I don’t have such a tool, hence I decided to build it.
  
I defined maximum adverse excursion for a spread trade as the percentage difference between the current value of ‘long price’ / ‘short price’ and its maximum value from the point the trade was placed (aka Current(‘long price’ / ‘short price’) / max (‘long price’ / ‘short price’) – 1 ). This goes from 0 to 100. If the maximum adverse excursion is larger than the trailing stop (using closing prices only), then I want to be notified by email.
  
I decided to create a simple exe and use Task Scheduler to run it at the end of the trading day. The program reads a file with all the open spread trades, downloads their prices, calculates maximum adverse excursion and sends an email if it is larger than the trailing stop. I also built a little WPF veneer to manipulate the configuration file.
  
Here is what my _common.fs_ file looks like.

<pre class="code"><span style="color:blue;">namespace </span>Spread
<span style="color:blue;">module internal </span>Common =
    <span style="color:blue;">open </span>System
    <span style="color:blue;">let internal </span>isValidDate s =
        <span style="color:blue;">let </span>v, _ = DateTime.TryParse(s)
        v
    <span style="color:blue;">let internal </span>isValidTrailingStop s =
        <span style="color:blue;">let </span>v1, n = Int32.TryParse(s)
        <span style="color:blue;">if </span>not(v1) <span style="color:blue;">then
            false
        else
            </span>n &gt;= 0 && n &lt;= 100
    <span style="color:blue;">let internal </span>isValidTicker (t:string) = not(t.Contains(<span style="color:maroon;">","</span>))
    <span style="color:blue;">let internal </span>isValidLine (l:string) = l.Split([|<span style="color:maroon;">','</span>|]).Length = 4
    <span style="color:blue;">let internal </span>elseThrow message expression = <span style="color:blue;">if </span>not(expression) <span style="color:blue;">then </span>raise message
    <span style="color:blue;">let internal </span>elseThrowi i message expression = <span style="color:blue;">if </span>not(expression) <span style="color:blue;">then </span>failwith (sprintf <span style="color:maroon;">"On line %i : %s" </span>i message)</pre>

&nbsp;
  
Notice the _isValidTicker_ function. Yep, I’m using a CSV file to store the list of spread trades. Also I often end up using the little _elseThrow_� functions that I originally used in the [Excel functions library](http://code.msdn.microsoft.com/FinancialFunctions/Wiki/View.aspx?title=Home) to check preconditions.
  
Here is an example of using them for the _parseLine_ function:

<pre class="code"><span style="color:green;">// parse a line in the csv config file, assumes valid csv, dates and trailing stop in [0,100]
</span><span style="color:blue;">let internal </span>parseLine lineNumber line =
    isValidLine line                |&gt; elseThrowi lineNumber <span style="color:maroon;">"badly formatted line"
    </span><span style="color:blue;">let </span>values = line.Split([|<span style="color:maroon;">','</span>|])
    isValidDate values.[0]          |&gt; elseThrowi lineNumber <span style="color:maroon;">"badly formatted date"
    </span>isValidTicker values.[1]        |&gt; elseThrowi lineNumber <span style="color:maroon;">"long ticker has a comma in it"
    </span>isValidTicker values.[2]        |&gt; elseThrowi lineNumber <span style="color:maroon;">"short ticker has a comma in it"
    </span>isValidTrailingStop values.[3]  |&gt; elseThrowi lineNumber <span style="color:maroon;">"trailing stop has to be between 0 and 100 included"
    </span>DateTime.Parse(values.[0]), values.[1].Trim(), values.[2].Trim(), int values.[3]</pre>

&nbsp;
  
As you can see, the csv format is (dateOfTrade, longTicker, shortTicker, trailingStop). Let’s now look and the FsCheck testcase for this function.

<pre class="code"><span style="color:blue;">let </span>writeLine (date:DateTime) (tickerLong:string) (tickerShort:string) (trailingStopValue:int) =
    sprintf <span style="color:maroon;">"%s,%s,%s,%i" </span>(date.ToShortDateString()) tickerLong tickerShort trailingStopValue
[&lt;Fact;Category(<span style="color:maroon;">"Fast Tests"</span>)&gt;]
<span style="color:blue;">let </span>can_parse_valid_lines () =
    <span style="color:blue;">let  </span>prop_parseLine (lineNumber:int) date tickerLong tickerShort trailingStopValue =
        <span style="color:blue;">let </span>line = writeLine date tickerLong tickerShort trailingStopValue
        <span style="color:blue;">let </span>values = line.Split([|<span style="color:maroon;">','</span>|])
        (isValidLine(line) && isValidDate values.[0] && isValidTicker values.[1] && isValidTicker values.[2]
                                                                                        && isValidTrailingStop values.[3])
            ==&gt; <span style="color:blue;">lazy
                let </span>actual = parseLine lineNumber line
                (date, tickerLong.Trim(), tickerShort.Trim(), trailingStopValue) = actual
    check config prop_parseLine</pre>

In FsCheck you state properties of your functions and FsCheck generates random values to test them. In this case I’m asserting that, given a _date, tickerLong, tickerShort, trailingStopValue_, I can write them to a string, read them back and I get the same values. Frankly, I was skeptical on the utility of such exercise, but I was wrong. That’s how I discovered that tickers cannot have commas in them (among other things).
  
To hook up FsCheck and XUnit (aka to run FsCheck property checking as normal testcases), you need to write the below black magic code.

<pre class="code"><span style="color:blue;">let </span>xUnitRunner =
    { <span style="color:blue;">new </span>IRunner <span style="color:blue;">with
        member </span>x.OnArguments(_,_,_) = ()
        <span style="color:blue;">member </span>x.OnShrink(_,_) = ()
        <span style="color:blue;">member </span>x.OnFinished(name, result) =
            <span style="color:blue;">match </span>result <span style="color:blue;">with
                </span>| True data <span style="color:blue;">-&gt; </span>Assert.True(<span style="color:blue;">true</span>)
                | _ <span style="color:blue;">-&gt; </span>failwith (testFinishedToString name result)
    }
<span style="color:blue;">let </span>config = {quick <span style="color:blue;">with </span>Runner = xUnitRunner}</pre>

Also, to run XUnit with your brand new .net 4.0 project, you need to add xunit.gui.exe.config to the XUnit directory with the following content:
  
<configuration>
  
<startup>
  
<requiredRuntime version=v4.0.20506&#8243; safemode=true/>
  
</startup>
  
</configuration>
  
While we are talking about such trivialities, I compile my testcases as executable, so that I can easily run them under debug. I also add the InternalsVisibleTo attribute, so that I can test internal stuff. Many of my algorithms are in internal functions and I want to test them in isolation.

<pre class="code">[&lt;assembly:InternalsVisibleTo(<span style="color:maroon;">"SpreadTrackingTests"</span>)&gt;]
    <span style="color:blue;">do
</span></pre>

&nbsp;
  
Given the previous function, I can then parse text and files with the following:

<pre class="code"><span style="color:blue;">let internal </span>parseText (lines:string) = lines.Trim().Split([|<span style="color:maroon;">'\n'</span>|]) |&gt; Array.mapi parseLine
<span style="color:blue;">let public </span>parseFile fileName = File.ReadAllText fileName |&gt; parseText</pre>

I need to load closing prices. I’m using [my own library](http://code.msdn.microsoft.com/DownloadStockPrices) to load prices. That library is pretty badly designed. Also, the function below should be factorized in several sub-functions. It kind of shows how you can write spaghetti code in a beautiful functional language as F# if you really try hard. But let’s not worry about such subtleties for now …

<pre class="code"><span style="color:blue;">let internal </span>loadClosingPrices (endDate:DateTime) tickersStartDate  =
    <span style="color:green;">// format parameters to conform to loadTickersAsync
    </span><span style="color:blue;">let </span>tickersLong, tickersShort =
        tickersStartDate
        |&gt; Array.map (<span style="color:blue;">fun </span>(startDate:DateTime, ticker1:string, ticker2:string, _) <span style="color:blue;">-&gt;
                </span>(ticker1, {Start = startDate; End = endDate}), (ticker2, {Start = startDate; End = endDate}))
        |&gt; Array.unzip
    <span style="color:blue;">let </span>prices = tickersShort
                 |&gt; Array.append tickersLong
                 |&gt; Array.toList
                 |&gt; loadTickersAsync
                 |&gt; Async.RunSynchronously
                 |&gt; Array.map (<span style="color:blue;">fun </span>(ticker, span, obs) <span style="color:blue;">-&gt; </span>ticker, obs <span style="color:green;">(*|&gt; asHappened 1. |&gt; adjusted adjStart*)</span>)
    <span style="color:blue;">let </span>len = tickersLong.Length
    <span style="color:blue;">let </span>longObs = Array.sub prices 0 len
    <span style="color:blue;">let </span>shortObs = Array.sub prices len len
    <span style="color:green;">// removes divs and splits
    </span><span style="color:blue;">let </span>choosePrices observation = <span style="color:blue;">match </span>observation.Event <span style="color:blue;">with </span>Price(pr) <span style="color:blue;">-&gt; </span>Some(observation) | _ <span style="color:blue;">-&gt; </span>None
    <span style="color:blue;">let </span>combineOverTickerObservations f tickerObservations =
        tickerObservations
        |&gt; Array.map (<span style="color:blue;">fun </span>(ticker, observations) <span style="color:blue;">-&gt;
                                            </span>ticker,
                                            observations |&gt; List.choose f |&gt; List.rev)
    <span style="color:blue;">let </span>longPrices = combineOverTickerObservations choosePrices longObs
    <span style="color:blue;">let </span>shortPrices = combineOverTickerObservations choosePrices shortObs
    longPrices, shortPrices</pre>

In the above, _tickerStartDate_ is an array of (trade date \* long ticker \* short ticker * trailingStop) which is what is produced by our _parseLine_ function. The function first separates out long tickers from short ones.

<pre class="code"><span style="color:blue;">let </span>tickersLong, tickersShort =
    tickersStartDate
    |&gt; Array.map (<span style="color:blue;">fun </span>(startDate:DateTime, ticker1:string, ticker2:string, _) <span style="color:blue;">-&gt;
            </span>(ticker1, {Start = startDate; End = endDate}), (ticker2, {Start = startDate; End = endDate}))
    |&gt; Array.unzip</pre>

It then puts them together again in a single Array, to be able to pass it to the loadTickerAsync functions. It runs the function, waits for the results and then returns an array of (ticker * observations).

<pre class="code"><span style="color:blue;">let </span>prices = tickersShort
             |&gt; Array.append tickersLong
             |&gt; Array.toList
             |&gt; loadTickersAsync
             |&gt; Async.RunSynchronously
             |&gt; Array.map (<span style="color:blue;">fun </span>(ticker, span, obs) <span style="color:blue;">-&gt; </span>ticker, obs |&gt; asHappened 1. |&gt; adjusted adjStart)</pre>

&nbsp;
  
The data is downloaded as it comes from Yahoo, which is a mix of adjusted and not adjusted data. _asHappened_ transforms it so that everything is as it really happened, _adjusted_ then adjusts it for the effect of dividends and splits. Think of this two function as ‘make the data right’.
  
We then split them again to get the long and short series. The point of merging them and splitting them is to call _loadTickersAsync_ just once instead of twice. There are better ways to do it.

<pre class="code"><span style="color:blue;">let </span>len = tickersLong.Length
        <span style="color:blue;">let </span>longObs = Array.sub prices 0 len
        <span style="color:blue;">let </span>shortObs = Array.sub prices len len</pre>

At this point we remove the observations that represents dividends or splits, as we are interested just in prices and we return the resulting observations.

<pre class="code"><span style="color:blue;">let </span>choosePrices observation = <span style="color:blue;">match </span>observation.Event <span style="color:blue;">with </span>Price(pr) <span style="color:blue;">-&gt; </span>Some(observation) | _ <span style="color:blue;">-&gt; </span>None
<span style="color:blue;">let </span>combineOverTickerObservations f tickerObservations =
    tickerObservations
    |&gt; Array.map (<span style="color:blue;">fun </span>(ticker, observations) <span style="color:blue;">-&gt;
                                        </span>ticker,
                                        observations |&gt; List.choose f |&gt; List.rev)
<span style="color:blue;">let </span>longPrices = combineOverTickerObservations choosePrices longObs
<span style="color:blue;">let </span>shortPrices = combineOverTickerObservations choosePrices shortObs
longPrices, shortPrices</pre>

The List.rev at the end is interesting. Somewhere in the loadTickerAsync/asHappened/adjusted triad of functions I end up reversing the list. I should fix the bug instead of workaround it, but this is just a blog post, not production code, so I’ll let it slip.
  
Now that we have our price observations, we need to extract the price values and calculate the sequence of ratios (long price / short price).

<pre class="code"><span style="color:blue;">let internal </span>calcRatioSeries longPrices shortPrices =
    <span style="color:blue;">let </span>extractPrice obs = <span style="color:blue;">match </span>obs.Event <span style="color:blue;">with </span>Price(pr) <span style="color:blue;">-&gt; </span>pr.Close | _ <span style="color:blue;">-&gt; </span>failwith <span style="color:maroon;">"At this point divs and splits should have been removed"
    </span><span style="color:blue;">let </span>longValues = longPrices |&gt;  List.map extractPrice
    <span style="color:blue;">let </span>shortValues = shortPrices |&gt; List.map extractPrice
    shortValues |&gt; List.map2 (/) longValues</pre>

Having this ratio series, we can calculate the maximum adverse excursion, incorrectly called trailing stop below.

<pre class="code"><span style="color:blue;">let internal </span>calcTrailingStop ratioSeries = List.head ratioSeries / List.max ratioSeries - 1.</pre>

We then create a function that puts it all together.

<pre class="code"><span style="color:blue;">type public </span>Result = {RatioName:string; CurrentTrailing:int; TrailingStop:int} <span style="color:blue;">with
    override </span>x.ToString() = x.RatioName + <span style="color:maroon;">"\t\t" </span>+ x.CurrentTrailing.ToString() + <span style="color:maroon;">"\t\t" </span>+ x.TrailingStop.ToString()
<span style="color:green;">// reads a csv file (startDate, longTicker, shortTicker, trailingStop) and returns an array of results
</span><span style="color:blue;">let public </span>processFile fileName endDate =
    <span style="color:blue;">let </span>fileInfo = parseFile fileName
    <span style="color:blue;">let </span>longPrices, shortPrices = loadClosingPrices endDate fileInfo
    <span style="color:blue;">let </span>ratioSeries = Array.map2 (<span style="color:blue;">fun </span>l s <span style="color:blue;">-&gt; </span>fst l + <span style="color:maroon;">"/" </span>+ fst s, calcRatioSeries (snd l) (snd s)) longPrices shortPrices
    ratioSeries |&gt; Array.mapi (<span style="color:blue;">fun </span>i (name, series) <span style="color:blue;">-&gt;
                    let </span>(_,_,_,ts) = fileInfo.[i]
                    {RatioName = name; CurrentTrailing = - int (Math.Round (calcTrailingStop series * 100., 0));
                                                                                                       TrailingStop = ts})</pre>

The function takes a fileName and an endDate, the latter parameter is for the sake of testcases that has to work in the past, so that the data doesn’t change on them.
  
Now we need to send an email. The code below works for me:

<pre class="code"><span style="color:blue;">let </span>sendEmail smtpServer port fromField toField subject body (user:string) (password:string) =
    <span style="color:blue;">let </span>client = <span style="color:blue;">new </span>SmtpClient(smtpServer, port)
    client.Credentials &lt;- <span style="color:blue;">new </span>NetworkCredential(user, password)
    client.EnableSsl &lt;- <span style="color:blue;">true
    </span>client.Send(fromField, toField, subject, body)
<span style="color:green;">// gets the password from a file under C: so that when I post it on my blog I don't forget to delete it
</span><span style="color:blue;">let </span>getPassword () =
    File.ReadAllText(<span style="color:maroon;">@"D:\Documents and Settings\Luca\My Documents\config.txt"</span>)</pre>

Almost done, in the main part of the program, we gather the data, create the content of the email and send it out:

<pre class="code"><span style="color:blue;">do
    let </span>file = <span style="color:maroon;">"spreads.csv"
    </span><span style="color:blue;">let </span>spreads = processFile file DateTime.Today
    <span style="color:blue;">let mutable </span>builder = <span style="color:blue;">new </span>System.Text.StringBuilder()
    builder &lt;- builder.AppendLine(<span style="color:maroon;">"Name\t\tCurrent\t\tStop"</span>)
    <span style="color:blue;">for </span>s <span style="color:blue;">in </span>spreads <span style="color:blue;">do
        </span>builder &lt;- builder.AppendLine(s.ToString())
    <span style="color:blue;">let </span>password = getPassword()
    sendEmail <span style="color:maroon;">"smtp.gmail.com" </span>587 <span style="color:maroon;">"***@***.com" <span style="color:maroon;">"***@***.com</span>" "Alert Trigger Spread" </span>(builder.ToString())
                                                                                           <span style="color:maroon;">"lucabolg@gmail.com" </span>password;;</pre>

Next stop, the WPF veneer on top of the file.