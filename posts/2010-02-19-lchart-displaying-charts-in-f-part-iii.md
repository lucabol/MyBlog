---
id: 26
title: 'LChart: displaying charts in F# – Part III'
date: 2010-02-19T18:03:00+00:00
author: lucabol
layout: post
guid: http://lucabolognese.wordpress.com/2010/02/19/lchart-displaying-charts-in-f-part-iii/
tags:
  - fsharp
---
The last post is [here](/2010/02/17/lchart-displaying-charts-in-f-part-ii/). In this post we'll look at how things work under the cover and to why I came to believe that they shouldn't work this way.

First of all each one of the functions to create charts looks something like this:

```fsharp
static member bar (?y,?x, ?isValueShownAsLabel, ?markerSize, ?markerStyle, ?color, ?xname, ?yname, ?seriesName, ?title, ?drawingStyle) =
    let c = Create (SeriesChartType.Bar, x, y, isValueShownAsLabel, markerSize, markerStyle, color, xname, yname, seriesName, title)
    c.Series.[0].["DrawingStyle"] <- defaultArg drawingStyle (c.Series.[0].["DrawingStyle"])
    c
```

This returns an object of type _lc_ (this is the type of '_c'_). But _lc_ inherits from _Chart_ which is the main class in the Microsoft Chart Controls.

```fsharp
type lc() =
    inherit Chart()
```

I should have said at the start that you need to reference such controls.

```fsharp
#r "System.Windows.Forms.DataVisualization.dll"
open System.Collections
open System.Drawing
open System.IO
open System.Windows.Forms
open System.Windows.Forms.DataVisualization.Charting
open System.Windows.Forms.DataVisualization.Charting.Utilities
open System
```

It is convenient that the return value of each function is a subtype of _Chart_. You can then go and customize this object as you like (i.e. changing graphical appearance) before calling _display_. Given the _Chart_ inherits from _Control_ you can code the display method as follows:

```fsharp
let display (c:lc) =
    let copy () =
        let stream = new MemoryStream()
        c.SaveImage(stream, Imaging.ImageFormat.Bmp)
        let bmp = new Bitmap(stream)
        Clipboard.SetDataObject(bmp)
    c.KeyDown.Add(fun e -> if e.Control = true && e.KeyCode = Keys.C then copy ())
    let pressToCopy = "(press CTRL+C to copy)"
    let name = if c.Titles.Count = 0 then sprintf "%s %s " "lc" pressToCopy else sprintf "%s %s " c.Titles.[0].Text  pressToCopy
    let f = new Form(Text = name, Size = new Size(800,600), TopMost = true)
    c.Dock <- DockStyle.Fill
    f.Controls.Add(c)
    f.Show()
    c
```

Apart from a bit of convolutions to implement a Copy function, this just put the _Chart_ control on a newly created _Form_. The _Create_ method called inside _bar_ looks like the following.

```fsharp
static let Create (chartType, x, y, isValueShownAsLabel, markerSize, markerStyle, color, xname, yname, seriesName, title) =
    let c = new lc()
    let a = new ChartArea()
    let s = new Series()
    s.ChartType <- chartType
    c.ChartAreas.Add(a)
    c.Series.Add(s)
    match x, y with
        | Some(x), None     -> failwith "You cannot pass only x to a chart drawing function"
        | Some(x), Some(y)  -> s.Points.DataBindXY(x, [|y|])
        | None, Some(y)     -> s.Points.DataBindY([|y|])
        | None, None        -> ()
    s.IsValueShownAsLabel <- defaultArg isValueShownAsLabel s.IsValueShownAsLabel
    s.MarkerSize <- defaultArg markerSize s.MarkerSize
    s.MarkerStyle <- defaultArg markerStyle s.MarkerStyle
    s.Color <- defaultArg color s.Color
    a.AxisX.MajorGrid.Enabled <- false
    a.AxisY.MajorGrid.Enabled <- false
    match xname with
    | Some(xname) ->
        a.AxisX.Title <- xname
        a.AxisX.TitleFont <- axisFont
        a.AxisX.TitleForeColor <- axisColor
    | _ -> ()
    match yname with
    | Some(yname) ->
        a.AxisY.Title <- yname
        a.AxisY.TitleFont <- axisFont
        a.AxisY.TitleForeColor <- axisColor
    | _ -> ()
    match seriesName with
    | Some(seriesName) -> s.Name <- seriesName
    | _ -> ()
    match title with
    | Some(title) ->
        let t = c.Titles.Add(title: string)
        t.Font <- titleFont
        t.ForeColor <- titleColor
    | _ -> ()
    c
```

Pretty standard imperative code here. Creating a chart and assigning its properties. Read the documentation for the Chart Control to understand what I'm doing here. I'm not even sure I remember what I'm doing. Given that we have our own _lc_ class (which is a type of _Chart_) we can then override the '+' operator and '++' operator to do what is needed.

```fsharp
static member (+) (c1:lc, c2:lc) =
    let c = copyChart(c1)
    c1.ChartAreas |> Seq.iter (fun a -> addAreaAndSeries c a c1.Series)
    let lastArea = c.ChartAreas |> Seq.nth ((c.ChartAreas |> Seq.length) - 1)
    c2.Series |> Seq.iter(fun s -> c.Series.Add(copySeries s c lastArea.Name))
    let l = c.Legends.Add("")
    l.Font <- legendFont
    c
static member (++) (c1:lc, c2:lc) =
    let c = copyChart(c1)
    c1.ChartAreas |> Seq.iter (fun a -> addAreaAndSeries c a c1.Series)
    let lastArea = c.ChartAreas |> Seq.nth ((c.ChartAreas |> Seq.length) - 1)
    addAreaAndSeries c c2.ChartAreas.[0] c2.Series
    let firstArea = c.ChartAreas |> Seq.nth ((c.ChartAreas |> Seq.length) - 1)
    c2.ChartAreas |> Seq.skip 1 |> Seq.iter (fun a -> addAreaAndSeries c a c2.Series)
    c    
```

Apart from some other utility functions, this is how it all works. Why do I say that it is wrong? It is my opinion that the right way to do it would be to use _'+_', '_++_' and all the _lc.XXX_ functions to create an object model that is completely independent from the Microsoft Chart controls. The display method would then translate it to the appropriate displayable Chart. It would work like a compiler translating to IL and then a Jitter producing native code. This would:

  * Make possible to do more interesting compositions of graphs. Now I'm very constrained in what I can do by the fact that I'm working directly with Chart objects
  * Make possible to change the backend. Using something different than Microsoft Chart controls to draw the chart

Why I have not done it? I didn't know that was the right design until I used the wrong one. Now that I know, I have no time to do it.
