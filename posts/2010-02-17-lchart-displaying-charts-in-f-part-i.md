---
id: 1075
title: 'LChart: displaying charts in F# – Part I'
date: 2010-02-17T11:20:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2010/02/17/lchart-displaying-charts-in-f-part-i/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2010/02/17/lchart-displaying-charts-in-f-part-i.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9965255"
orig_parent_id:
  - "9965255"
orig_thread_id:
  - "701790"
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
  - http://blogs.msdn.com/b/lucabol/archive/2010/02/17/lchart-displaying-charts-in-f-part-i.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="LChart: displaying charts in F# &ndash; Part I" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2010/02/17/lchart-displaying-charts-in-f-part-i/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="I want to use F# as a exploratory data analysis language (like R). But I don't know how to get the same nice graphic capabilities. So I decided to create them. Here is a library to draw charts in F#. It steals ideas from this book and this R package. It is nothing more than..." />
    <meta property="og:image" content="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_thumb.png" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="LChart: displaying charts in F# &ndash; Part I" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2010/02/17/lchart-displaying-charts-in-f-part-i/" />
    <meta name="twitter:description" content="I want to use F# as a exploratory data analysis language (like R). But I don't know how to get the same nice graphic capabilities. So I decided to create them. Here is a library to draw charts in F#. It steals ideas from this book and this R package. It is nothing more than..." />
    <meta name="twitter:image" content="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_thumb.png" />
    
restapi_import_id:
  - 5c011e0505e67
original_post_id:
  - "33"
categories:
  - Uncategorized
tags:
  - fsharp
---
I want to use F# as a exploratory data analysis language (like [R](http://www.r-project.org/)). But I don't know how to get the same nice graphic capabilities. So I decided to create them. Here is a library to draw charts in F#. It steals ideas from [this book](http://www.amazon.com/Grammar-Graphics-Leland-Wilkinson/dp/0387987746) and [this R package](http://had.co.nz/ggplot2/book/). It is nothing more than a wrapper on top of the [Microsoft Chart Controls](http://www.microsoft.com/downloads/details.aspx?familyid=130F7986-BF49-4FE5-9CA8-910AE6EA442C&displaylang=en) to give it a more 'exploratory' one line calling syntax. It is also rough work in progress: I don't wrap all the chart types and there are bugs in the ones I wrap. Also the architecture is all wrong (more on this in another post). But it's a start and it kind of works. Attached the full code.

I will continue this series in my new blog at wordpress: [http://lucabolognese.wordpress.com/](http://lucabolognese.wordpress.com/ "http://lucabolognese.wordpress.com/"). The reason I need a new blog will be explained in an upcoming post.

Part II is now [here](http://lucabolognese.wordpress.com/2010/02/17/lchart-displaying-charts-in-f-part-ii/).

Ok, let's start. How do I draw a chart?

```fsharp
let x = [1.;2.5;3.1;4.;4.8;6.0;7.5;8.;9.1;15.]
let y = [1.6;2.1;1.4;4.;2.3;1.9;2.4;1.4;5.;2.9]
lc.scatter(x, y) |> display
```

X and Y are just some make up data. _lc_ is the name of a class (????) and _scatter_ is a static method on it. _scatter_ doesn't display the chart, it just produces a an object that represents the chart. _Display_ displays the chart. The reason for using the bizarre lc static class is that I want it to be short so that it is easy to type in the fsi.exe. At the same time it needs to support optional parameters (which are not supported on top level functions in F#).

You get a window with this chart on it. You can press CTRL+C to copy it (as I did to post it here).

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_thumb.png" width="382" height="295" />](https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_2.png) 

You might want to customize the chart a bit by passing some of these famous optional parameters:

```fsharp
lc.scatter(x = x, y = y, markerSize = 10, markerStyle = MarkerStyle.Diamond,
    xname = "Players", yname = "Ratings", title = "Players' Ratings")  |> display     
```

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_thumb_1.png" width="382" height="295" />](https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_4.png) 

Or you might want to print different types of charts:

```fsharp
lc.line(y = y, markerSize = 10, markerStyle = MarkerStyle.Diamond, xname = "Players", yname = "Ratings", title = "Players' Ratings", isValueShownAsLabel = true,
    color = Color.Red) |> display       
```

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_thumb_2.png" width="373" height="289" />](https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_6.png) 

```fsharp
lc.spline(x = x, y = y, markerSize = 10, markerStyle = MarkerStyle.Diamond, xname = "Players", yname = "Ratings",
    title = "Players' Ratings", isValueShownAsLabel = true, color = Color.Red) |> display 
```

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_thumb_3.png" width="371" height="287" />](https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_8.png) 

```fsharp
lc.stepline(x = x, y = y, markerSize = 10, markerStyle = MarkerStyle.Diamond, xname = "Players", yname = "Ratings",
    title = "Players' Ratings", isValueShownAsLabel = true, color = Color.Red) |> display
```

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_thumb_4.png" width="372" height="288" />](https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_10.png) 

```fsharp
lc.bar(y = y, xname = "Players", yname = "Ratings", title = "Players' Ratings", isValueShownAsLabel = true,
    drawingStyle = "Emboss") |> display      
```

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_thumb_5.png" width="351" height="265" />](https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_12.png) 

```fsharp
lc.column(y = y, xname = "Players", yname = "Ratings", title = "Players' Ratings",
    isValueShownAsLabel = true, drawingStyle = "Cylinder") |> display   
```

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_thumb_6.png" width="375" height="283" />](https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_14.png) 

```fsharp
lc.boxplot(y = y, xname = "Players", yname = "Ratings", title = "Players' Ratings", color = Color.Blue, whiskerPercentile = 5, percentile = 30,
    showAverage = false, showMedian = false, showUnusualValues = true) |> display    
```

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_thumb_7.png" width="408" height="317" />](https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_16.png) 

Ok, the last one is weird. You probably want more than one boxplot in a chart. I'll show you how to do that in the next post.

The next post will be on how to have more than one series on the same chart and more than one chart in the same windows. Something like the below:

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_thumb_8.png" width="445" height="342" />](https://msdnshared.blob.core.windows.net/media/TNBlogsFS/BlogFileStorage/blogs_msdn/lucabol/WindowsLiveWriter/LChartdisplayingchartsinFPartI_9F73/image_18.png)

[ChartPlotter.fsx](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/09/96/52/55/ChartPlotter.fsx)
