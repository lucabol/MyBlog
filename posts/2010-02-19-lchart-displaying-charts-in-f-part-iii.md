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
The last post is [here](/2010/02/17/lchart-displaying-charts-in-f-part-ii/). In this post we’ll look at how things work under the cover and to why I came to believe that they shouldn’t work this way.

First of all each one of the functions to create charts looks something like this:

<pre class="code"><span style="color:blue;">static member </span>bar (?y,?x, ?isValueShownAsLabel, ?markerSize, ?markerStyle, ?color, ?xname, ?yname, ?seriesName, ?title, ?drawingStyle) =
    <span style="color:blue;">let </span>c = Create (SeriesChartType.Bar, x, y, isValueShownAsLabel, markerSize, markerStyle, color, xname, yname, seriesName, title)
    c.Series.[0].[<span style="color:maroon;">"DrawingStyle"</span>] &lt;- defaultArg drawingStyle (c.Series.[0].[<span style="color:maroon;">"DrawingStyle"</span>])
    c</pre>

This returns an object of type _lc_ (this is the type of ‘_c’_). But _lc_ inherits from _Chart_ which is the main class in the Microsoft Chart Controls.

<pre class="code"><span style="color:blue;">type </span>lc() =
    <span style="color:blue;">inherit </span>Chart()</pre>

I should have said at the start that you need to reference such controls.

<pre class="code"><span style="color:blue;">#r </span><span style="color:maroon;">"System.Windows.Forms.DataVisualization.dll"
</span><span style="color:blue;">open </span>System.Collections
<span style="color:blue;">open </span>System.Drawing
<span style="color:blue;">open </span>System.IO
<span style="color:blue;">open </span>System.Windows.Forms
<span style="color:blue;">open </span>System.Windows.Forms.DataVisualization.Charting
<span style="color:blue;">open </span>System.Windows.Forms.DataVisualization.Charting.Utilities
<span style="color:blue;">open </span>System</pre>

It is convenient that the return value of each function is a subtype of _Chart_. You can then go and customize this object as you like (i.e. changing graphical appearance) before calling _display_. Given the _Chart_ inherits from _Control_ you can code the display method as follows:

<pre class="code"><span style="color:blue;">let </span>display (c:lc) =
    <span style="color:blue;">let </span>copy () =
        <span style="color:blue;">let </span>stream = <span style="color:blue;">new </span>MemoryStream()
        c.SaveImage(stream, Imaging.ImageFormat.Bmp)
        <span style="color:blue;">let </span>bmp = <span style="color:blue;">new </span>Bitmap(stream)
        Clipboard.SetDataObject(bmp)
    c.KeyDown.Add(<span style="color:blue;">fun </span>e <span style="color:blue;">-&gt; if </span>e.Control = <span style="color:blue;">true </span>&& e.KeyCode = Keys.C <span style="color:blue;">then </span>copy ())
    <span style="color:blue;">let </span>pressToCopy = <span style="color:maroon;">"(press CTRL+C to copy)"
    </span><span style="color:blue;">let </span>name = <span style="color:blue;">if </span>c.Titles.Count = 0 <span style="color:blue;">then </span>sprintf <span style="color:maroon;">"%s %s " "lc" </span>pressToCopy <span style="color:blue;">else </span>sprintf <span style="color:maroon;">"%s %s " </span>c.Titles.[0].Text  pressToCopy
    <span style="color:blue;">let </span>f = <span style="color:blue;">new </span>Form(Text = name, Size = <span style="color:blue;">new </span>Size(800,600), TopMost = <span style="color:blue;">true</span>)
    c.Dock &lt;- DockStyle.Fill
    f.Controls.Add(c)
    f.Show()
    c</pre>



Apart from a bit of convolutions to implement a Copy function, this just put the _Chart_ control on a newly created _Form_. The _Create_ method called inside _bar_ looks like the following.

<pre class="code"><span style="color:blue;">static let </span>Create (chartType, x, y, isValueShownAsLabel, markerSize, markerStyle, color, xname, yname, seriesName, title) =
    <span style="color:blue;">let </span>c = <span style="color:blue;">new </span>lc()
    <span style="color:blue;">let </span>a = <span style="color:blue;">new </span>ChartArea()
    <span style="color:blue;">let </span>s = <span style="color:blue;">new </span>Series()
    s.ChartType &lt;- chartType
    c.ChartAreas.Add(a)
    c.Series.Add(s)
    <span style="color:blue;">match </span>x, y <span style="color:blue;">with
        </span>| Some(x), None     <span style="color:blue;">-&gt; </span>failwith <span style="color:maroon;">"You cannot pass only x to a chart drawing function"
        </span>| Some(x), Some(y)  <span style="color:blue;">-&gt; </span>s.Points.DataBindXY(x, [|y|])
        | None, Some(y)     <span style="color:blue;">-&gt; </span>s.Points.DataBindY([|y|])
        | None, None        <span style="color:blue;">-&gt; </span>()
    s.IsValueShownAsLabel &lt;- defaultArg isValueShownAsLabel s.IsValueShownAsLabel
    s.MarkerSize &lt;- defaultArg markerSize s.MarkerSize
    s.MarkerStyle &lt;- defaultArg markerStyle s.MarkerStyle
    s.Color &lt;- defaultArg color s.Color
    a.AxisX.MajorGrid.Enabled &lt;- <span style="color:blue;">false
    </span>a.AxisY.MajorGrid.Enabled &lt;- <span style="color:blue;">false
    match </span>xname <span style="color:blue;">with
    </span>| Some(xname) <span style="color:blue;">-&gt;
        </span>a.AxisX.Title &lt;- xname
        a.AxisX.TitleFont &lt;- axisFont
        a.AxisX.TitleForeColor &lt;- axisColor
    | _ <span style="color:blue;">-&gt; </span>()
    <span style="color:blue;">match </span>yname <span style="color:blue;">with
    </span>| Some(yname) <span style="color:blue;">-&gt;
        </span>a.AxisY.Title &lt;- yname
        a.AxisY.TitleFont &lt;- axisFont
        a.AxisY.TitleForeColor &lt;- axisColor
    | _ <span style="color:blue;">-&gt; </span>()
    <span style="color:blue;">match </span>seriesName <span style="color:blue;">with
    </span>| Some(seriesName) <span style="color:blue;">-&gt; </span>s.Name &lt;- seriesName
    | _ <span style="color:blue;">-&gt; </span>()
    <span style="color:blue;">match </span>title <span style="color:blue;">with
    </span>| Some(title) <span style="color:blue;">-&gt;
        let </span>t = c.Titles.Add(title: string)
        t.Font &lt;- titleFont
        t.ForeColor &lt;- titleColor
    | _ <span style="color:blue;">-&gt; </span>()
    c</pre>

Pretty standard imperative code here. Creating a chart and assigning its properties. Read the documentation for the Chart Control to understand what I’m doing here. I’m not even sure I remember what I’m doing. Given that we have our own _lc_ class (which is a type of _Chart_) we can then override the ‘+’ operator and ‘++’ operator to do what is needed.

<pre class="code"><span style="color:blue;">static member </span>(+) (c1:lc, c2:lc) =
    <span style="color:blue;">let </span>c = copyChart(c1)
    c1.ChartAreas |&gt; Seq.iter (<span style="color:blue;">fun </span>a <span style="color:blue;">-&gt; </span>addAreaAndSeries c a c1.Series)
    <span style="color:blue;">let </span>lastArea = c.ChartAreas |&gt; Seq.nth ((c.ChartAreas |&gt; Seq.length) - 1)
    c2.Series |&gt; Seq.iter(<span style="color:blue;">fun </span>s <span style="color:blue;">-&gt; </span>c.Series.Add(copySeries s c lastArea.Name))
    <span style="color:blue;">let </span>l = c.Legends.Add(<span style="color:maroon;">""</span>)
    l.Font &lt;- legendFont
    c
<span style="color:blue;">static member </span>(++) (c1:lc, c2:lc) =
    <span style="color:blue;">let </span>c = copyChart(c1)
    c1.ChartAreas |&gt; Seq.iter (<span style="color:blue;">fun </span>a <span style="color:blue;">-&gt; </span>addAreaAndSeries c a c1.Series)
    <span style="color:blue;">let </span>lastArea = c.ChartAreas |&gt; Seq.nth ((c.ChartAreas |&gt; Seq.length) - 1)
    addAreaAndSeries c c2.ChartAreas.[0] c2.Series
    <span style="color:blue;">let </span>firstArea = c.ChartAreas |&gt; Seq.nth ((c.ChartAreas |&gt; Seq.length) - 1)
    c2.ChartAreas |&gt; Seq.skip 1 |&gt; Seq.iter (<span style="color:blue;">fun </span>a <span style="color:blue;">-&gt; </span>addAreaAndSeries c a c2.Series)
    c    </pre>

Apart from some other utility functions, this is how it all works. Why do I say that it is wrong? It is my opinion that the right way to do it would be to use _‘+_’, ‘_++_’ and all the _lc.XXX_ functions to create an object model that is completely independent from the Microsoft Chart controls. The display method would then translate it to the appropriate displayable Chart. It would work like a compiler translating to IL and then a Jitter producing native code. This would:

  * Make possible to do more interesting compositions of graphs. Now I’m very constrained in what I can do by the fact that I’m working directly with Chart objects
  * Make possible to change the backend. Using something different than Microsoft Chart controls to draw the chart

Why I have not done it? I didn’t know that was the right design until I used the wrong one. Now that I know, I have no time to do it.