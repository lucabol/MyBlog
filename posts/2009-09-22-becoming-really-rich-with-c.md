---
id: 1083
title: 'Becoming really rich with C#'
date: 2009-09-22T19:40:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/09/22/becoming-really-rich-with-c/
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
  - csharp
  - Financial
---
Or maybe not, please do not hold me responsible if you lose money following this system. Having said that, it is my opinion that there are very few concepts that are important in investing. Three big ones are value, diversification and momentum. This post is about the latter two and how to use C# to create a simple trading system that uses both.

Diversification is 'not put all your eggs in one basket' (contrary to 'put all of them in one basket and watch that basket'). I don't believe you can 'watch' very much in financial markets, so I tend to prefer diversification.

Momentum is a mysterious tendency of financial prices that have risen the most in the recent past, to continue outperforming in the close future. In essence, buying the top stocks/sectors/asset classes tends to outperform buying the bottom ones over horizons from three months to one year.

The idea then is to rank some assets (i.e. ETFs) by how fast they have risen in the past, go long the top ones and short the bottom ones. There are hundreds of variations of this basic strategy, we'll add the rule that we won't buy assets that are below their 200 days moving average or sell short assets that are above it.

I'm writing this code with VS 2010 Beta 2 (which hasn't shipped yet). It should be trivial to modify it to run on B1 (or maybe it does run on it already). I attach the code and data files to this post.

```csharp
struct Event {
    internal Event(DateTime date, double price) { Date = date; Price = price; }
    internal readonly DateTime Date;
    internal readonly double Price;
}
```

We'll use this simple structure to load the closing price for a particular date. My use of internal is kind of bizarre. Actually the whole code might look strange. It is an interesting (maybe un-elegant) mix of object orientation and functional programming.

```csharp
class Summary {
    internal Summary(string ticker, string name, string assetClass,
                    string assetSubClass, double? weekly, double? fourWeeks,
                    double? threeMonths, double? sixMonths, double? oneYear,
                    double? stdDev, double price, double? mav200) {
        Ticker = ticker;
        Name = name;
        AssetClass = assetClass;
        AssetSubClass = assetSubClass;
        // Abracadabra ...
        LRS = (fourWeeks + threeMonths + sixMonths + oneYear) / 4;
        Weekly = weekly;
        FourWeeks = fourWeeks;
        ThreeMonths = threeMonths;
        SixMonths = sixMonths;
        OneYear = oneYear;
        StdDev = stdDev;
        Mav200 = mav200;
        Price = price;
    }
    internal readonly string Ticker;
    internal readonly string Name;
    internal readonly string AssetClass;
    internal readonly string AssetSubClass;
    internal readonly double? LRS;
    internal readonly double? Weekly;
    internal readonly double? FourWeeks;
    internal readonly double? ThreeMonths;
    internal readonly double? SixMonths;
    internal readonly double? OneYear;
    internal readonly double? StdDev;
    internal readonly double? Mav200;
    internal double Price;
    internal static void Banner() {
        Console.Write("{0,-6}", "Ticker");
        Console.Write("{0,-50}", "Name");
        Console.Write("{0,-12}", "Asset Class");
        //Console.Write("{0,-30}t", "Asset SubClass";
        Console.Write("{0,4}", "RS");
        Console.Write("{0,4}", "1Wk");
        Console.Write("{0,4}", "4Wk");
        Console.Write("{0,4}", "3Ms");
        Console.Write("{0,4}", "6Ms");
        Console.Write("{0,4}", "1Yr");
        Console.Write("{0,6}", "Vol");
        Console.WriteLine("{0,2}", "Mv");
        //Console.Write("{0,6}", "Pr");
        //Console.WriteLine("{0,6}", "M200");
    }
    internal void Print() {
        Console.Write("{0,-6}", Ticker);
        Console.Write("{0,-50}", new String(Name.Take(48).ToArray()));
        Console.Write("{0,-12}", new String(AssetClass.Take(10).ToArray()));
        //Console.Write("{0,-30}t", new String(AssetSubClass.Take(28).ToArray()));
        Console.Write("{0,4:N0}", LRS * 100);
        Console.Write("{0,4:N0}", Weekly * 100);
        Console.Write("{0,4:N0}", FourWeeks * 100);
        Console.Write("{0,4:N0}", ThreeMonths * 100);
        Console.Write("{0,4:N0}", SixMonths * 100);
        Console.Write("{0,4:N0}", OneYear * 100);
        Console.Write("{0,6:N0}", StdDev * 100);
        if (Price <= Mav200)
            Console.WriteLine("{0,2}", "X");
        else
            Console.WriteLine();
        //Console.Write("{0,6:N2}", Price);
        //Console.WriteLine("{0,6:N2}", Mav200);
    }
}
```

The class Summary above is how I want to present my results. A few comments on the code. I use _Nullable<T>_ because some of this values can be null (i.e. not enough history), but I still don't want to worry about it. It ends up working rather neatly.

I also print the results out to _Console,_ which is crazy. I really should be using WPF/Silverlight as the presentation layer. Also the _{0,4:N0}_ notation might be unfamiliar to some of you, but this is how mad _Console_ guys like myself avoid using real UI frameworks. Sometimes we print things in color too.

The real meat is in the following line:

```csharp
LRS = (fourWeeks + threeMonths + sixMonths + oneYear) / 4;
```

That is our highway to richness. It's a very elaborated quant formula, never before shown, that calculate a magick relative strength (aka momentum) factor as the average of the performance of four weeks, three months, six months and one year.

```csharp
class TimeSeries {
    internal readonly string Ticker;
    readonly DateTime _start;
    readonly Dictionary<DateTime, double> _adjDictionary;
    readonly string _name;
    readonly string _assetClass;
    readonly string _assetSubClass;
    internal TimeSeries(string ticker, string name, string assetClass, string assetSubClass, 
                                                                IEnumerable<Event> events) {
        Ticker = ticker;
        _name = name;
        _assetClass = assetClass;
        _assetSubClass = assetSubClass;
        _start = events.Last().Date;
        _adjDictionary = events.ToDictionary(e => e.Date, e => e.Price);
    }
```

I then built myself a little TimeSeries class that represents a series of (date, price). I choose a dictionary to store it because of my assumption that I will be accessing it by date a lot. In retrospect, I was kind of right and kind of wrong. It doesn't really matter much.

```csharp
bool GetPrice(DateTime when, out double price, out double shift) {
    // To nullify the effect of hours/min/sec/millisec being different from 0
    when = new DateTime(when.Year, when.Month, when.Day);
    var found = false;
    shift = 1;
    double aPrice = 0;
    while (when >= _start && !found) {
        if (_adjDictionary.TryGetValue(when, out aPrice)) {
            found = true;
        }
        when = when.AddDays(-1);
        shift -= 1;
    }
    price = aPrice;
    return found;
}
```

A TimeSeries can give you back the price at a particular date. This looks bizarre and complex, but there is a reason for it. I might ask for a date that doesn't have a price associated with it (i.e. holidays, week-ends). In such cases I want to return the previous price which could be N days in the past.

I also want to return how many days in the past I had to go, so that other calculations (i.e. _Return_) can modify their end date by the same amount. Also I might not find such a price at all, in which case I don't want to throw an exception, but instead notify the caller. In retrospect, I should have used _double?_ to signify 'price not found'.

```csharp
double? GetReturn(DateTime start, DateTime end) {
    var startPrice = 0.0;
    var endPrice = 0.0;
    var shift = 0.0;
    var foundEnd = GetPrice(end, out endPrice, out shift);
    var foundStart = GetPrice(start.AddDays(shift), out startPrice, out shift);
    if (!foundStart || !foundEnd)
        return null;
    else
        return endPrice / startPrice - 1;
}
```

We can now go and calculate the return between two dates. Also the _TimeSeries_ object needs to perform a little more calculations.

```csharp
internal double? LastWeekReturn() {
        return GetReturn(DateTime.Now.AddDays(-7), DateTime.Now);
    }
    internal double? Last4WeeksReturn() {
        return GetReturn(DateTime.Now.AddDays(-28), DateTime.Now);
    }
    internal double? Last3MonthsReturn() {
        return GetReturn(DateTime.Now.AddMonths(-3), DateTime.Now);
    }
    internal double? Last6MonthsReturn() {
        return GetReturn(DateTime.Now.AddMonths(-6), DateTime.Now);
    }
    internal double? LastYearReturn() {
        return GetReturn(DateTime.Now.AddYears(-1), DateTime.Now);
    }
    internal double? StdDev() {
        var now = DateTime.Now;
        now = new DateTime(now.Year, now.Month, now.Day);
        var limit = now.AddYears(-3);
        var rets = new List<double>();
        while (now >= _start.AddDays(12) && now >= limit) {
            var ret = GetReturn(now.AddDays(-7), now);
            rets.Add(ret.Value);
            now = now.AddDays(-7);
        }
        var mean = rets.Average();
        var variance = rets.Select(r => Math.Pow(r - mean, 2)).Sum();
        var weeklyStdDev = Math.Sqrt(variance / rets.Count);
        return weeklyStdDev * Math.Sqrt(40);
    }
    internal double? MAV200() {
        return _adjDictionary
               .ToList()
               .OrderByDescending(k => k.Key)
               .Take(200)
               .Average(k => k.Value);
    }
    internal double TodayPrice() {
        var price = 0.0;
        var shift = 0.0;
        GetPrice(DateTime.Now, out price, out shift);
        return price;
    }
    internal Summary GetSummary() {
        return new Summary(Ticker, _name, _assetClass, _assetSubClass, 
                           LastWeekReturn(), Last4WeeksReturn(), Last3MonthsReturn(),
                           Last6MonthsReturn(), LastYearReturn(), StdDev(), TodayPrice(),
                           MAV200());
    }
```

Nothing particularly interesting in this code. Just a bunch of calculations. The _MAV200_ is the 200 days moving average of closing prices. It shows a more functional way of doing things. The _StdDev_ function is instead very imperative.

We now can work on downloading the prices. This is how you construct the right URL:

```csharp
static string CreateUrl(string ticker, DateTime start, DateTime end) {
    return @"http://ichart.finance.yahoo.com/table.csv?s=" + ticker + "&a="
            + (start.Month - 1).ToString() + "&b=" + start.Day.ToString() + "&c="
            + start.Year.ToString() + "&d=" + (end.Month - 1).ToString() + "&e="
            + end.Day.ToString() + "&f=" + end.Year.ToString() + "&g=d&ignore=.csv";
}
```

And let's set how many concurrent connections we are going to use …

```csharp
ServicePointManager.DefaultConnectionLimit = 10;
```

On my machine, setting this number too high causes errors to be returned. I'm not sure on which side of the connection the problem lies.

We can then load all the tickers we want to load from a file. One of the files has Leveraged ETFs, which I want to filter out because they tend to pop up always at the top.

```csharp
var tickers =
    //File.ReadAllLines("ETFs.csv")
    //File.ReadAllLines("ETFTest.csv")
    File.ReadAllLines("AssetClasses.csv")
    .Skip(1)
    .Select(l => l.Split(new[] { ',' }))
    .Where(v => v[2] != "Leveraged")
    .Select(values => Tuple.Create(values[0], values[1], values[2], values[3]))
    .ToArray();
var len = tickers.Length;
var start = DateTime.Now.AddYears(-2);
var end = DateTime.Now;
var cevent = new CountdownEvent(len);
var summaries = new Summary[len];
```

And then load all of them, making sure to make an asynchronous call so not to keep the thread busy.

```csharp
for(var i = 0; i < len; i++)  {
    var t = tickers[i];
    var url = CreateUrl(t.Item1, start, end);
    using (var webClient = new WebClient()) {
        webClient.DownloadStringCompleted +=
                          new DownloadStringCompletedEventHandler(downloadStringCompleted);
        webClient.DownloadStringAsync(new Uri(url), Tuple.Create(t, cevent, summaries, i));
    }
}
cevent.Wait();
```

Notice the use of a Countdown event to wait for all the thread to complete before printing out the results. Also notice the new _Tuple<T>_ class used to package things to send around.

We can then print out the top and bottom 15%:

```csharp
var top15perc =
        summaries
        .Where(s => s.LRS.HasValue)
        .OrderByDescending(s => s.LRS)
        .Take((int)(len * 0.15));
var bottom15perc =
        summaries
        .Where(s => s.LRS.HasValue)
        .OrderBy(s => s.LRS)
        .Take((int)(len * 0.15));
Console.WriteLine();
Summary.Banner();
Console.WriteLine("TOP 15%");
foreach(var s in top15perc)
    s.Print();
Console.WriteLine();
Console.WriteLine("Bottom 15%");
foreach (var s in bottom15perc)
    s.Print();
```

Here is what we do when a request comes back with data:

```csharp
static void downloadStringCompleted(object sender, DownloadStringCompletedEventArgs e) {
    var bigTuple =
             (Tuple<Tuple<string, string, string, string>, CountdownEvent, Summary[], int>)
              e.UserState;
    var tuple = bigTuple.Item1;
    var cevent = bigTuple.Item2;
    var summaries = bigTuple.Item3;
    var i = bigTuple.Item4;
    var ticker = tuple.Item1;
    var name = tuple.Item2;
    var asset = tuple.Item3;
    var subAsset = tuple.Item4;
    if (e.Error == null) {
        var adjustedPrices =
                e.Result
                .Split(new[] { 'n' })
                .Skip(1)
                .Select(l => l.Split(new[] { ',' }))
                .Where(l => l.Length == 7)
                .Select(v => new Event(DateTime.Parse(v[0]), Double.Parse(v[6])));
        var timeSeries = new TimeSeries(ticker, name, asset, subAsset, adjustedPrices);
        summaries[i] = timeSeries.GetSummary();
        cevent.Signal();
        Console.Write("{0} ", ticker);
    }
    else {
        Console.WriteLine("[{0} ERROR] ", ticker);
        //Console.WriteLine(e.Error);
        summaries[i] = new Summary(ticker, name, "ERROR", "ERROR", 0, 0, 0, 0, 0, 0,0,0);
        cevent.Signal();
    }
}
```

We first unpack the _Tuple_ we sent out originally, we then extract the Date and Price, create a _Summary_ object and store it in the _summaries_ array. It's important to remember to _Signal_ to the _cevent_ in the error case as well because we want to print out the results even if some downloading failed.

And here is what you get for your effort:

[<img style="display:inline;border-width:0;" title="image" border="0" alt="image" src="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/BecomingreallyrichwithC_C128/image_thumb.png" width="743" height="506" />](https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/BecomingreallyrichwithC_C128/image_2.png)

[SystemCodeAndData.zip](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/09/89/69/82/SystemCodeAndData.zip)
