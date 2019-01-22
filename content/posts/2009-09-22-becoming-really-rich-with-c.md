---
id: 1083
title: 'Becoming really rich with C#'
date: 2009-09-22T19:40:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/09/22/becoming-really-rich-with-c/
permalink: /2009/09/22/becoming-really-rich-with-c/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/09/22/becoming-really-rich-with-c.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9896982"
orig_parent_id:
  - "9896982"
orig_thread_id:
  - "676951"
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
  - "1"
orig_url_title:
  - http://blogs.msdn.com/b/lucabol/archive/2009/09/22/becoming-really-rich-with-c.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Becoming really rich with C#" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/09/22/becoming-really-rich-with-c/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Or maybe not, please do not hold me responsible if you lose money following this system. Having said that, it is my opinion that there are very few concepts that are important in investing. Three big ones are value, diversification and momentum. This post is about the latter two and how to use C# to..." />
    <meta property="og:image" content="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/BecomingreallyrichwithC_C128/image_thumb.png" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Becoming really rich with C#" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/09/22/becoming-really-rich-with-c/" />
    <meta name="twitter:description" content="Or maybe not, please do not hold me responsible if you lose money following this system. Having said that, it is my opinion that there are very few concepts that are important in investing. Three big ones are value, diversification and momentum. This post is about the latter two and how to use C# to..." />
    <meta name="twitter:image" content="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/BecomingreallyrichwithC_C128/image_thumb.png" />
    
restapi_import_id:
  - 5c011e0505e67
original_post_id:
  - "123"
categories:
  - Uncategorized
tags:
  - 'C# Programming'
---
Or maybe not, please do not hold me responsible if you lose money following this system. Having said that, it is my opinion that there are very few concepts that are important in investing. Three big ones are value, diversification and momentum. This post is about the latter two and how to use C# to create a simple trading system that uses both.

Diversification is ‘not put all your eggs in one basket’ (contrary to ‘put all of them in one basket and watch that basket’). I don’t believe you can ‘watch’ very much in financial markets, so I tend to prefer diversification.

Momentum is a mysterious tendency of financial prices that have risen the most in the recent past, to continue outperforming in the close future. In essence, buying the top stocks/sectors/asset classes tends to outperform buying the bottom ones over horizons from three months to one year.

The idea then is to rank some assets (i.e. ETFs) by how fast they have risen in the past, go long the top ones and short the bottom ones. There are hundreds of variations of this basic strategy, we’ll add the rule that we won’t buy assets that are below their 200 days moving average or sell short assets that are above it.

I’m writing this code with VS 2010 Beta 2 (which hasn’t shipped yet). It should be trivial to modify it to run on B1 (or maybe it does run on it already). I attach the code and data files to this post.

<pre class="code"><span style="color:blue;">struct </span><span style="color:#2b91af;">Event </span>{
    <span style="color:blue;">internal </span>Event(<span style="color:#2b91af;">DateTime </span>date, <span style="color:blue;">double </span>price) { Date = date; Price = price; }
    <span style="color:blue;">internal readonly </span><span style="color:#2b91af;">DateTime </span>Date;
    <span style="color:blue;">internal readonly double </span>Price;
}</pre>

We’ll use this simple structure to load the closing price for a particular date. My use of internal is kind of bizarre. Actually the whole code might look strange. It is an interesting (maybe un-elegant) mix of object orientation and functional programming.

<pre class="code"><span style="color:blue;">class </span><span style="color:#2b91af;">Summary </span>{
    <span style="color:blue;">internal </span>Summary(<span style="color:blue;">string </span>ticker, <span style="color:blue;">string </span>name, <span style="color:blue;">string </span>assetClass,
                    <span style="color:blue;">string </span>assetSubClass, <span style="color:blue;">double</span>? weekly, <span style="color:blue;">double</span>? fourWeeks,
                    <span style="color:blue;">double</span>? threeMonths, <span style="color:blue;">double</span>? sixMonths, <span style="color:blue;">double</span>? oneYear,
                    <span style="color:blue;">double</span>? stdDev, <span style="color:blue;">double </span>price, <span style="color:blue;">double</span>? mav200) {
        Ticker = ticker;
        Name = name;
        AssetClass = assetClass;
        AssetSubClass = assetSubClass;
        <span style="color:green;">// Abracadabra ...
        </span>LRS = (fourWeeks + threeMonths + sixMonths + oneYear) / <span style="color:brown;">4</span>;
        Weekly = weekly;
        FourWeeks = fourWeeks;
        ThreeMonths = threeMonths;
        SixMonths = sixMonths;
        OneYear = oneYear;
        StdDev = stdDev;
        Mav200 = mav200;
        Price = price;
    }
    <span style="color:blue;">internal readonly string </span>Ticker;
    <span style="color:blue;">internal readonly string </span>Name;
    <span style="color:blue;">internal readonly string </span>AssetClass;
    <span style="color:blue;">internal readonly string </span>AssetSubClass;
    <span style="color:blue;">internal readonly double</span>? LRS;
    <span style="color:blue;">internal readonly double</span>? Weekly;
    <span style="color:blue;">internal readonly double</span>? FourWeeks;
    <span style="color:blue;">internal readonly double</span>? ThreeMonths;
    <span style="color:blue;">internal readonly double</span>? SixMonths;
    <span style="color:blue;">internal readonly double</span>? OneYear;
    <span style="color:blue;">internal readonly double</span>? StdDev;
    <span style="color:blue;">internal readonly double</span>? Mav200;
    <span style="color:blue;">internal double </span>Price;
    <span style="color:blue;">internal static void </span>Banner() {
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,-6}"</span>, <span style="color:#a31515;">"Ticker"</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,-50}"</span>, <span style="color:#a31515;">"Name"</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,-12}"</span>, <span style="color:#a31515;">"Asset Class"</span>);
        <span style="color:green;">//Console.Write("{0,-30}t", "Asset SubClass";
        </span><span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,4}"</span>, <span style="color:#a31515;">"RS"</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,4}"</span>, <span style="color:#a31515;">"1Wk"</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,4}"</span>, <span style="color:#a31515;">"4Wk"</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,4}"</span>, <span style="color:#a31515;">"3Ms"</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,4}"</span>, <span style="color:#a31515;">"6Ms"</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,4}"</span>, <span style="color:#a31515;">"1Yr"</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,6}"</span>, <span style="color:#a31515;">"Vol"</span>);
        <span style="color:#2b91af;">Console</span>.WriteLine(<span style="color:#a31515;">"{0,2}"</span>, <span style="color:#a31515;">"Mv"</span>);
        <span style="color:green;">//Console.Write("{0,6}", "Pr");
        //Console.WriteLine("{0,6}", "M200");
    </span>}
    <span style="color:blue;">internal void </span>Print() {
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,-6}"</span>, Ticker);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,-50}"</span>, <span style="color:blue;">new </span><span style="color:#2b91af;">String</span>(Name.Take(<span style="color:brown;">48</span>).ToArray()));
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,-12}"</span>, <span style="color:blue;">new </span><span style="color:#2b91af;">String</span>(AssetClass.Take(<span style="color:brown;">10</span>).ToArray()));
        <span style="color:green;">//Console.Write("{0,-30}t", new String(AssetSubClass.Take(28).ToArray()));
        </span><span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,4:N0}"</span>, LRS * <span style="color:brown;">100</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,4:N0}"</span>, Weekly * <span style="color:brown;">100</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,4:N0}"</span>, FourWeeks * <span style="color:brown;">100</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,4:N0}"</span>, ThreeMonths * <span style="color:brown;">100</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,4:N0}"</span>, SixMonths * <span style="color:brown;">100</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,4:N0}"</span>, OneYear * <span style="color:brown;">100</span>);
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0,6:N0}"</span>, StdDev * <span style="color:brown;">100</span>);
        <span style="color:blue;">if </span>(Price &lt;= Mav200)
            <span style="color:#2b91af;">Console</span>.WriteLine(<span style="color:#a31515;">"{0,2}"</span>, <span style="color:#a31515;">"X"</span>);
        <span style="color:blue;">else
            </span><span style="color:#2b91af;">Console</span>.WriteLine();
        <span style="color:green;">//Console.Write("{0,6:N2}", Price);
        //Console.WriteLine("{0,6:N2}", Mav200);
    </span>}
}</pre>

The class Summary above is how I want to present my results. A few comments on the code. I use _Nullable<T>_ because some of this values can be null (i.e. not enough history), but I still don’t want to worry about it. It ends up working rather neatly.

I also print the results out to _Console,_ which is crazy. I really should be using WPF/Silverlight as the presentation layer. Also the _{0,4:N0}_ notation might be unfamiliar to some of you, but this is how mad _Console_ guys like myself avoid using real UI frameworks. Sometimes we print things in color too.

The real meat is in the following line:

<pre class="code">LRS = (fourWeeks + threeMonths + sixMonths + oneYear) / <span style="color:brown;">4</span>;</pre>

That is our highway to richness. It’s a very elaborated quant formula, never before shown, that calculate a magick relative strength (aka momentum) factor as the average of the performance of four weeks, three months, six months and one year.

<pre class="code"><span style="color:blue;">class </span><span style="color:#2b91af;">TimeSeries </span>{
    <span style="color:blue;">internal readonly string </span>Ticker;
    <span style="color:blue;">readonly </span><span style="color:#2b91af;">DateTime </span>_start;
    <span style="color:blue;">readonly </span><span style="color:#2b91af;">Dictionary</span>&lt;<span style="color:#2b91af;">DateTime</span>, <span style="color:blue;">double</span>&gt; _adjDictionary;
    <span style="color:blue;">readonly string </span>_name;
    <span style="color:blue;">readonly string </span>_assetClass;
    <span style="color:blue;">readonly string </span>_assetSubClass;
    <span style="color:blue;">internal </span>TimeSeries(<span style="color:blue;">string </span>ticker, <span style="color:blue;">string </span>name, <span style="color:blue;">string </span>assetClass, <span style="color:blue;">string </span>assetSubClass, <br />                                                                <span style="color:#2b91af;">IEnumerable</span>&lt;<span style="color:#2b91af;">Event</span>&gt; events) {
        Ticker = ticker;
        _name = name;
        _assetClass = assetClass;
        _assetSubClass = assetSubClass;
        _start = events.Last().Date;
        _adjDictionary = events.ToDictionary(e =&gt; e.Date, e =&gt; e.Price);
    }</pre>

I then built myself a little TimeSeries class that represents a series of (date, price). I choose a dictionary to store it because of my assumption that I will be accessing it by date a lot. In retrospect, I was kind of right and kind of wrong. It doesn’t really matter much.

<pre class="code"><span style="color:blue;">bool </span>GetPrice(<span style="color:#2b91af;">DateTime </span>when, <span style="color:blue;">out double </span>price, <span style="color:blue;">out double </span>shift) {
    <span style="color:green;">// To nullify the effect of hours/min/sec/millisec being different from 0
    </span>when = <span style="color:blue;">new </span><span style="color:#2b91af;">DateTime</span>(when.Year, when.Month, when.Day);
    <span style="color:blue;">var </span>found = <span style="color:blue;">false</span>;
    shift = <span style="color:brown;">1</span>;
    <span style="color:blue;">double </span>aPrice = <span style="color:brown;"></span>;
    <span style="color:blue;">while </span>(when &gt;= _start && !found) {
        <span style="color:blue;">if </span>(_adjDictionary.TryGetValue(when, <span style="color:blue;">out </span>aPrice)) {
            found = <span style="color:blue;">true</span>;
        }
        when = when.AddDays(-<span style="color:brown;">1</span>);
        shift -= <span style="color:brown;">1</span>;
    }
    price = aPrice;
    <span style="color:blue;">return </span>found;
}</pre>

A TimeSeries can give you back the price at a particular date. This looks bizarre and complex, but there is a reason for it. I might ask for a date that doesn’t have a price associated with it (i.e. holidays, week-ends). In such cases I want to return the previous price which could be N days in the past.

I also want to return how many days in the past I had to go, so that other calculations (i.e. _Return_) can modify their end date by the same amount. Also I might not find such a price at all, in which case I don’t want to throw an exception, but instead notify the caller. In retrospect, I should have used _double?_ to signify ‘price not found’.

<pre class="code"><span style="color:blue;">double</span>? GetReturn(<span style="color:#2b91af;">DateTime </span>start, <span style="color:#2b91af;">DateTime </span>end) {
    <span style="color:blue;">var </span>startPrice = <span style="color:brown;">0.0</span>;
    <span style="color:blue;">var </span>endPrice = <span style="color:brown;">0.0</span>;
    <span style="color:blue;">var </span>shift = <span style="color:brown;">0.0</span>;
    <span style="color:blue;">var </span>foundEnd = GetPrice(end, <span style="color:blue;">out </span>endPrice, <span style="color:blue;">out </span>shift);
    <span style="color:blue;">var </span>foundStart = GetPrice(start.AddDays(shift), <span style="color:blue;">out </span>startPrice, <span style="color:blue;">out </span>shift);
    <span style="color:blue;">if </span>(!foundStart || !foundEnd)
        <span style="color:blue;">return null</span>;
    <span style="color:blue;">else
        return </span>endPrice / startPrice - <span style="color:brown;">1</span>;
}</pre>

We can now go and calculate the return between two dates. Also the _TimeSeries_ object needs to perform a little more calculations.

<pre class="code"><span style="color:blue;">internal double</span>? LastWeekReturn() {
        <span style="color:blue;">return </span>GetReturn(<span style="color:#2b91af;">DateTime</span>.Now.AddDays(-<span style="color:brown;">7</span>), <span style="color:#2b91af;">DateTime</span>.Now);
    }
    <span style="color:blue;">internal double</span>? Last4WeeksReturn() {
        <span style="color:blue;">return </span>GetReturn(<span style="color:#2b91af;">DateTime</span>.Now.AddDays(-<span style="color:brown;">28</span>), <span style="color:#2b91af;">DateTime</span>.Now);
    }
    <span style="color:blue;">internal double</span>? Last3MonthsReturn() {
        <span style="color:blue;">return </span>GetReturn(<span style="color:#2b91af;">DateTime</span>.Now.AddMonths(-<span style="color:brown;">3</span>), <span style="color:#2b91af;">DateTime</span>.Now);
    }
    <span style="color:blue;">internal double</span>? Last6MonthsReturn() {
        <span style="color:blue;">return </span>GetReturn(<span style="color:#2b91af;">DateTime</span>.Now.AddMonths(-<span style="color:brown;">6</span>), <span style="color:#2b91af;">DateTime</span>.Now);
    }
    <span style="color:blue;">internal double</span>? LastYearReturn() {
        <span style="color:blue;">return </span>GetReturn(<span style="color:#2b91af;">DateTime</span>.Now.AddYears(-<span style="color:brown;">1</span>), <span style="color:#2b91af;">DateTime</span>.Now);
    }
    <span style="color:blue;">internal double</span>? StdDev() {
        <span style="color:blue;">var </span>now = <span style="color:#2b91af;">DateTime</span>.Now;
        now = <span style="color:blue;">new </span><span style="color:#2b91af;">DateTime</span>(now.Year, now.Month, now.Day);
        <span style="color:blue;">var </span>limit = now.AddYears(-<span style="color:brown;">3</span>);
        <span style="color:blue;">var </span>rets = <span style="color:blue;">new </span><span style="color:#2b91af;">List</span>&lt;<span style="color:blue;">double</span>&gt;();
        <span style="color:blue;">while </span>(now &gt;= _start.AddDays(<span style="color:brown;">12</span>) && now &gt;= limit) {
            <span style="color:blue;">var </span>ret = GetReturn(now.AddDays(-<span style="color:brown;">7</span>), now);
            rets.Add(ret.Value);
            now = now.AddDays(-<span style="color:brown;">7</span>);
        }
        <span style="color:blue;">var </span>mean = rets.Average();
        <span style="color:blue;">var </span>variance = rets.Select(r =&gt; <span style="color:#2b91af;">Math</span>.Pow(r - mean, <span style="color:brown;">2</span>)).Sum();
        <span style="color:blue;">var </span>weeklyStdDev = <span style="color:#2b91af;">Math</span>.Sqrt(variance / rets.Count);
        <span style="color:blue;">return </span>weeklyStdDev * <span style="color:#2b91af;">Math</span>.Sqrt(<span style="color:brown;">40</span>);
    }
    <span style="color:blue;">internal double</span>? MAV200() {
        <span style="color:blue;">return </span>_adjDictionary<br />               .ToList()<br />               .OrderByDescending(k =&gt; k.Key)<br />               .Take(<span style="color:brown;">200)<br />               </span>.Average(k =&gt; k.Value);
    }
    <span style="color:blue;">internal double </span>TodayPrice() {
        <span style="color:blue;">var </span>price = <span style="color:brown;">0.0</span>;
        <span style="color:blue;">var </span>shift = <span style="color:brown;">0.0</span>;
        GetPrice(<span style="color:#2b91af;">DateTime</span>.Now, <span style="color:blue;">out </span>price, <span style="color:blue;">out </span>shift);
        <span style="color:blue;">return </span>price;
    }
    <span style="color:blue;">internal </span><span style="color:#2b91af;">Summary </span>GetSummary() {
        <span style="color:blue;">return new </span><span style="color:#2b91af;">Summary</span>(Ticker, _name, _assetClass, _assetSubClass, <br />                           LastWeekReturn(), Last4WeeksReturn(), Last3MonthsReturn(),<br />                           Last6MonthsReturn(), LastYearReturn(), StdDev(), TodayPrice(),<br />                           MAV200());
    }
}</pre>

Nothing particularly interesting in this code. Just a bunch of calculations. The _MAV200_ is the 200 days moving average of closing prices. It shows a more functional way of doing things. The _StdDev_ function is instead very imperative.

We now can work on downloading the prices. This is how you construct the right URL:

<pre class="code"><span style="color:blue;">static string </span>CreateUrl(<span style="color:blue;">string </span>ticker, <span style="color:#2b91af;">DateTime </span>start, <span style="color:#2b91af;">DateTime </span>end) {
    <span style="color:blue;">return </span><span style="color:#a31515;">@"http://ichart.finance.yahoo.com/table.csv?s=" </span>+ ticker + <span style="color:#a31515;">"&a="<br />            </span>+ (start.Month - <span style="color:brown;">1</span>).ToString() + <span style="color:#a31515;">"&b=" </span>+ start.Day.ToString() + <span style="color:#a31515;">"&c="<br />            </span>+ start.Year.ToString() + <span style="color:#a31515;">"&d=" </span>+ (end.Month - <span style="color:brown;">1</span>).ToString() + <span style="color:#a31515;">"&e="<br />            </span>+ end.Day.ToString() + <span style="color:#a31515;">"&f=" </span>+ end.Year.ToString() + <span style="color:#a31515;">"&g=d&ignore=.csv"</span>;
}</pre>

&nbsp;

And let’s set how many concurrent connections we are going to use …

<pre class="code"><span style="color:#2b91af;">ServicePointManager</span>.DefaultConnectionLimit = <span style="color:brown;">10</span>;</pre>

On my machine, setting this number too high causes errors to be returned. I’m not sure on which side of the connection the problem lies.

We can then load all the tickers we want to load from a file. One of the files has Leveraged ETFs, which I want to filter out because they tend to pop up always at the top.

<pre class="code"><span style="color:blue;">var </span>tickers =
    <span style="color:green;">//File.ReadAllLines("ETFs.csv")
    //File.ReadAllLines("ETFTest.csv")
    </span><span style="color:#2b91af;">File</span>.ReadAllLines(<span style="color:#a31515;">"AssetClasses.csv"</span>)
    .Skip(<span style="color:brown;">1</span>)
    .Select(l =&gt; l.Split(<span style="color:blue;">new</span>[] { <span style="color:#a31515;">',' </span>}))
    .Where(v =&gt; v[<span style="color:brown;">2</span>] != <span style="color:#a31515;">"Leveraged"</span>)
    .Select(values =&gt; <span style="color:#2b91af;">Tuple</span>.Create(values[<span style="color:brown;"></span>], values[<span style="color:brown;">1</span>], values[<span style="color:brown;">2</span>], values[<span style="color:brown;">3</span>]))
    .ToArray();
<span style="color:blue;">var </span>len = tickers.Length;
<span style="color:blue;">var </span>start = <span style="color:#2b91af;">DateTime</span>.Now.AddYears(-<span style="color:brown;">2</span>);
<span style="color:blue;">var </span>end = <span style="color:#2b91af;">DateTime</span>.Now;
<span style="color:blue;">var </span>cevent = <span style="color:blue;">new </span><span style="color:#2b91af;">CountdownEvent</span>(len);
<span style="color:blue;">var </span>summaries = <span style="color:blue;">new </span><span style="color:#2b91af;">Summary</span>[len];</pre>

And then load all of them, making sure to make an asynchronous call so not to keep the thread busy.

<pre class="code"><span style="color:#2b91af;">for(var i = </span><span style="color:brown;">0;</span> i &lt; len; i++)  {
    <span style="color:blue;">var </span>t = tickers[i];
    <span style="color:blue;">var </span>url = CreateUrl(t.Item1, start, end);
    <span style="color:blue;">using </span>(<span style="color:blue;">var </span>webClient = <span style="color:blue;">new </span><span style="color:#2b91af;">WebClient</span>()) {
        webClient.DownloadStringCompleted +=<br />                          <span style="color:blue;">new </span><span style="color:#2b91af;">DownloadStringCompletedEventHandler</span>(downloadStringCompleted);
        webClient.DownloadStringAsync(<span style="color:blue;">new </span><span style="color:#2b91af;">Uri</span>(url), <span style="color:#2b91af;">Tuple</span>.Create(t, cevent, summaries, i));
    }
}
cevent.Wait();</pre>

&nbsp;

Notice the use of a Countdown event to wait for all the thread to complete before printing out the results. Also notice the new _Tuple<T>_ class used to package things to send around.

We can then print out the top and bottom 15%:

<pre class="code"><span style="color:blue;">var </span>top15perc =
        summaries
        .Where(s =&gt; s.LRS.HasValue)
        .OrderByDescending(s =&gt; s.LRS)
        .Take((<span style="color:blue;">int</span>)(len * <span style="color:brown;">0.15</span>));
<span style="color:blue;">var </span>bottom15perc =
        summaries
        .Where(s =&gt; s.LRS.HasValue)
        .OrderBy(s =&gt; s.LRS)
        .Take((<span style="color:blue;">int</span>)(len * <span style="color:brown;">0.15</span>));
<span style="color:#2b91af;">Console</span>.WriteLine();
<span style="color:#2b91af;">Summary</span>.Banner();
<span style="color:#2b91af;">Console</span>.WriteLine(<span style="color:#a31515;">"TOP 15%"</span>);
<span style="color:blue;">foreach</span>(<span style="color:blue;">var </span>s <span style="color:blue;">in </span>top15perc)
    s.Print();
<span style="color:#2b91af;">Console</span>.WriteLine();
<span style="color:#2b91af;">Console</span>.WriteLine(<span style="color:#a31515;">"Bottom 15%"</span>);
<span style="color:blue;">foreach </span>(<span style="color:blue;">var </span>s <span style="color:blue;">in </span>bottom15perc)
    s.Print();</pre>

&nbsp;

Here is what we do when a request comes back with data:

<pre class="code"><span style="color:blue;">static void </span>downloadStringCompleted(<span style="color:blue;">object </span>sender, <span style="color:#2b91af;">DownloadStringCompletedEventArgs </span>e) {
    <span style="color:blue;">var </span>bigTuple =<br />             (<span style="color:#2b91af;">Tuple</span>&lt;<span style="color:#2b91af;">Tuple</span>&lt;<span style="color:blue;">string</span>, <span style="color:blue;">string</span>, <span style="color:blue;">string</span>, <span style="color:blue;">string</span>&gt;, <span style="color:#2b91af;">CountdownEvent</span>, <span style="color:#2b91af;">Summary</span>[], <span style="color:blue;">int</span>&gt;)<br />              e.UserState;
    <span style="color:blue;">var </span>tuple = bigTuple.Item1;
    <span style="color:blue;">var </span>cevent = bigTuple.Item2;
    <span style="color:blue;">var </span>summaries = bigTuple.Item3;
    <span style="color:blue;">var </span>i = bigTuple.Item4;
    <span style="color:blue;">var </span>ticker = tuple.Item1;
    <span style="color:blue;">var </span>name = tuple.Item2;
    <span style="color:blue;">var </span>asset = tuple.Item3;
    <span style="color:blue;">var </span>subAsset = tuple.Item4;
    <span style="color:blue;">if </span>(e.Error == <span style="color:blue;">null</span>) {
        <span style="color:blue;">var </span>adjustedPrices =
                e.Result
                .Split(<span style="color:blue;">new</span>[] { <span style="color:#a31515;">'n' </span>})
                .Skip(<span style="color:brown;">1</span>)
                .Select(l =&gt; l.Split(<span style="color:blue;">new</span>[] { <span style="color:#a31515;">',' </span>}))
                .Where(l =&gt; l.Length == <span style="color:brown;">7</span>)
                .Select(v =&gt; <span style="color:blue;">new </span><span style="color:#2b91af;">Event</span>(<span style="color:#2b91af;">DateTime</span>.Parse(v[<span style="color:brown;"></span>]), <span style="color:#2b91af;">Double</span>.Parse(v[<span style="color:brown;">6</span>])));
        <span style="color:blue;">var </span>timeSeries = <span style="color:blue;">new </span><span style="color:#2b91af;">TimeSeries</span>(ticker, name, asset, subAsset, adjustedPrices);
        summaries[i] = timeSeries.GetSummary();
        cevent.Signal();
        <span style="color:#2b91af;">Console</span>.Write(<span style="color:#a31515;">"{0} "</span>, ticker);
    }
    <span style="color:blue;">else </span>{
        <span style="color:#2b91af;">Console</span>.WriteLine(<span style="color:#a31515;">"[{0} ERROR] "</span>, ticker);
        <span style="color:green;">//Console.WriteLine(e.Error);
        </span>summaries[i] = <span style="color:blue;">new </span><span style="color:#2b91af;">Summary</span>(ticker, name, <span style="color:#a31515;">"ERROR"</span>, <span style="color:#a31515;">"ERROR"</span>, <span style="color:brown;"></span>, <span style="color:brown;"></span>, <span style="color:brown;"></span>, <span style="color:brown;"></span>, <span style="color:brown;"></span>, <span style="color:brown;"></span>,<span style="color:brown;"></span>,<span style="color:brown;"></span>);
        cevent.Signal();
    }
}</pre>

We first unpack the _Tuple_ we sent out originally, we then extract the Date and Price, create a _Summary_ object and store it in the _summaries_ array. It’s important to remember to _Signal_ to the _cevent_ in the error case as well because we want to print out the results even if some downloading failed.

And here is what you get for your effort:

[<img style="display:inline;border-width:0;" title="image" border="0" alt="image" src="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/BecomingreallyrichwithC_C128/image_thumb.png" width="743" height="506" />](https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/BecomingreallyrichwithC_C128/image_2.png)

[SystemCodeAndData.zip](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/09/89/69/82/SystemCodeAndData.zip)