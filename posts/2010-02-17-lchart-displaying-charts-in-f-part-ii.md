---
id: 22
title: 'LChart: displaying charts in F# – Part II'
date: 2010-02-17T20:24:33+00:00
author: lucabol
layout: post
guid: http://lucabolognese.wordpress.com/2010/02/17/lchart-displaying-charts-in-f-part-ii/
categories:
  - fsharp
tags:
  - fsharp
---
In the [previous post](/2010/02/17/lchart-displaying-charts-in-f-part-i) on my old blog I showed how to display simple charts with LChart. In this one we'll talk about more complex charts. I wanted to define a little language for graphs for the sake of creating a more complex chart in a single line of code. Remember, the scenario here is: I got some data, I want to display it quickly in the fsi. The language has two operators: '+' and '++'.

'+' allows you to to superimpose things on a chart as in the following example.

```fsharp
lc.scatter(y) + lc.line(y) |> display
```

Notice how I can superimpose two graphs of a different type and display the result.

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="/wp-content/uploads/2010/02/image_thumb.png" width="417" height="303" />](/wp-content/uploads/2010/02/image.png) 

Notice on the upper right corner a bizarre (Series1, Series2) legend. What I wanted to do, but didn't get around to do, was to allow a syntax like

```fsharp
lc.scatter(y) + lc.line(y) + lc.legend("Players") |> display
```

It should be relatively trivial to add it to the code. Also notice that the 'y' parameter in the second chart is not needed. Data flows freely from left to right. So you can write the equivalent code below. This is a feature that caused all sort of grief. With hindsight it's not worth the hassle. That's why you always need to write your code at least twice to get it right.

```fsharp
lc.scatter(y) + lc.line() |> display 
```

Some other, more elaborate charts follows. Notice how data flows from left to right until I introduce a new variable (i.e. the two _lc.boxplot&#160;_ instructions plot different boxplots)

```fsharp
lc.scatter(y, markerSize = 10) + lc.column() + lc.boxplot() + lc.line()  + lc.column(x) + lc.boxplot()|> display
```

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="/wp-content/uploads/2010/02/image_thumb1.png" width="410" height="298" />](/wp-content/uploads/2010/02/image1.png) 

Things would be better with names for axis, titles and such. I'm not including them for the sake of simplicity.

```fsharp
lc.scatter(y, markerSize = 10) + lc.column() + (lc.line(x)  + lc.column()) + lc.scatter(markerSize = 20) |> display
```

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="/wp-content/uploads/2010/02/image_thumb2.png" width="396" height="288" />](/wp-content/uploads/2010/02/image2.png) 

If you remember the previous post, we talked about boxplots and how you generally want to have more than one on a graph. You can do that with the '+' operator and get this ugly chart. More work is needed here.

```fsharp
lc.boxplot(y = y, xname = "Players", yname = "Ratings", title = "Players' Ratings", color = Color.Blue, whiskerPercentile = 5, percentile = 30,
    showAverage = false, showMedian = false, showUnusualValues = true) +  lc.boxplot(y = x) |> display
```

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="/wp-content/uploads/2010/02/image_thumb4.png" width="399" height="290" />](/wp-content/uploads/2010/02/image4.png)

'++' allows you to create new charts below the chart you already have as in:

```fsharp
let h = [1.;2.5;3.1;4.;4.8;6.0;7.5;8.;9.1;15.]
let w = h |> List.map (fun h -> h * 1.2)
lc.line(h) + lc.column() ++ lc.line(w) ++ lc.bubble() |> display
```

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="/wp-content/uploads/2010/02/image_thumb3.png" width="396" height="288" />](/wp-content/uploads/2010/02/image3.png) 

Notice the left to right flowing of information here as well. In the next installment we'll take a look at how things are implemented and why it's all wrong.
