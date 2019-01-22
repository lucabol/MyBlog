---
id: 33
title: 'Tracking spread trades in F# (and WPF MVVM) – Part II'
date: 2010-03-19T23:33:00+00:00
author: lucabol
layout: post
guid: http://lucabolognese.wordpress.com/2010/03/19/tracking-spread-trades-in-f-and-wpf-mvvm-part-ii/
permalink: /2010/03/19/tracking-spread-trades-in-f-and-wpf-mvvm-part-ii/
categories:
  - 'F#'
---
I wanted to experiment with MVVM and WPF in F#, so I decided to create a little graphical interface for the csv file that drives the spread tracking application. When I started I thought I needed some kind of a grid with Submit/Cancel buttons, but the more I thought about it, the more I realized that I wouldn’t need them.

See, I’ve always be one to complain about our current paradigm of Open File / Close File / Save File arguing that the user shouldn’t know about an entity called ‘file’. He shouldn’t be exposed to the fact that the application is just an in-memory copy of an hard disk artifact. His mental model should simply be: I open a document, I work on it, I close it, if needed I can make a copy; if I have problems I can revert to a previous version of the same document; If I make an error I can use ‘undo’ to revert it. There are no files/save/submit/cancel in such paradigm. There is no file system.

On the technical side I wanted to experiment with MVVM, even if in this case, the paradigm is overkilled (can really use this word?), given the simplicity of the application.

In any case, the ViewModel is in F#. It uses two utility classes:

<pre class="code"><span style="color:green;">// TODO: refactor to remove code repetition below
</span>[&lt;AbstractClass&gt;]
<span style="color:blue;">type </span>ViewModelBase () =
    <span style="color:blue;">let </span>propertyChanged = <span style="color:blue;">new </span>Event&lt;PropertyChangedEventHandler, PropertyChangedEventArgs&gt;()
    <span style="color:blue;">interface </span>INotifyPropertyChanged <span style="color:blue;">with
        </span>[&lt;CLIEvent&gt;]
        <span style="color:blue;">member </span>this.PropertyChanged = propertyChanged.Publish
    <span style="color:blue;">member internal </span>this.RaisePropertyChangedEvent(propertyName:string) =
        <span style="color:blue;">if </span>not(propertyName = <span style="color:blue;">null</span>) <span style="color:blue;">then
            let </span>e = <span style="color:blue;">new </span>PropertyChangedEventArgs(propertyName)
            <span style="color:blue;">let </span>i = this :&gt; INotifyPropertyChanged
            propertyChanged.Trigger(this, e)
<span style="color:blue;">type </span>ObservableCollectionWithChanges&lt;'a <span style="color:blue;">when </span>'a :&gt; INotifyPropertyChanged&gt; () =
    <span style="color:blue;">inherit </span>ObservableCollection&lt;'a&gt; ()
    <span style="color:blue;">let </span>propertyChanged = <span style="color:blue;">new </span>Event&lt;PropertyChangedEventHandler, PropertyChangedEventArgs&gt;()
    <span style="color:blue;">member </span>c.PropertyChanged = propertyChanged.Publish
    <span style="color:blue;">member private </span>c.RaisePropertyChangedEvent(propertyName:string) =
        <span style="color:blue;">if </span>not(propertyName = <span style="color:blue;">null</span>) <span style="color:blue;">then
            let </span>e = <span style="color:blue;">new </span>PropertyChangedEventArgs(propertyName)
            <span style="color:blue;">let </span>i = c :&gt; INotifyPropertyChanged
            propertyChanged.Trigger(c, e)
    <span style="color:blue;">member </span>c.Add(o) =
        <span style="color:blue;">base</span>.Add(o)
        o.PropertyChanged.Add(<span style="color:blue;">fun </span>x <span style="color:blue;">-&gt; </span>c.RaisePropertyChangedEvent(<span style="color:maroon;">""</span>))</pre>

The first one is used as a base for all the viewmodel entities in the application, the second one serves as the base for all the collections. They both define the customary _PropertyChanged_ event. The latter adds itself as an observer to each object added to the collection so that, whenever one changes, it gets notified and can notify its own observers. Look at the _c.Add_ method. A lot of repetitive code here, I would heed the advice of the comment on top if this were production code.

Each line in the csv file is represented as a ResultViewModel, hence the following:

<pre class="code"><span style="color:blue;">type </span>ResultViewModel (d:DateTime, sLong, sShort, tStop) =
    <span style="color:blue;">inherit </span>ViewModelBase ()
    <span style="color:blue;">let mutable </span>date = d
    <span style="color:blue;">let mutable </span>stockLong = sLong
    <span style="color:blue;">let mutable </span>stockShort = sShort
    <span style="color:blue;">let mutable </span>trailingStop = tStop
    <span style="color:blue;">new </span>() = <span style="color:blue;">new </span>ResultViewModel(DateTime.Today, <span style="color:maroon;">""</span>, <span style="color:maroon;">""</span>, 0)
    <span style="color:blue;">member </span>r.Date <span style="color:blue;">with </span>get() = date
                       <span style="color:blue;">and </span>set newValue =
                            date &lt;- newValue
                            <span style="color:blue;">base</span>.RaisePropertyChangedEvent(<span style="color:maroon;">"Date"</span>)
    <span style="color:blue;">member </span>r.StockLong <span style="color:blue;">with </span>get() = stockLong
                       <span style="color:blue;">and </span>set newValue =
                            stockLong &lt;- newValue
                            <span style="color:blue;">base</span>.RaisePropertyChangedEvent(<span style="color:maroon;">"StockLong"</span>)
    <span style="color:blue;">member </span>r.StockShort <span style="color:blue;">with </span>get() = stockShort
                        <span style="color:blue;">and </span>set newValue =
                            stockShort &lt;- newValue
                            <span style="color:blue;">base</span>.RaisePropertyChangedEvent(<span style="color:maroon;">"StockShort"</span>)
    <span style="color:blue;">member </span>r.TrailingStop <span style="color:blue;">with </span>get() =
                                trailingStop
                          <span style="color:blue;">and </span>set newValue =
                                trailingStop &lt;- newValue
                                <span style="color:blue;">base</span>.RaisePropertyChangedEvent(<span style="color:maroon;">"TrailingStop"</span>)
    <span style="color:blue;">member </span>r.IsThereAnError = r.TrailingStop &lt; 0 || r.TrailingStop &gt; 100</pre>

I need the empty constructor to be able to hook up to the DataGrid add-new capability. There might be an event I could use instead, but this is simple enough (even if a bit goofy).

The main view model class then looks like the following:

<pre class="code"><span style="color:blue;">type </span>MainViewModel (fileName:string) <span style="color:blue;">as </span>self =
    <span style="color:blue;">inherit </span>ViewModelBase ()
    <span style="color:blue;">let mutable </span>results = <span style="color:blue;">new </span>ObservableCollectionWithChanges&lt;ResultViewModel&gt;()
    <span style="color:blue;">let </span>loadResults () =
        parseFile fileName
        |&gt; Array.iter (<span style="color:blue;">fun </span>(d,sl, ss, ts) <span style="color:blue;">-&gt;
                        </span>results.Add(<span style="color:blue;">new </span>ResultViewModel(d, sl, ss, ts)))
    <span style="color:blue;">do
        </span>loadResults ()
        results.CollectionChanged.Add(<span style="color:blue;">fun </span>e <span style="color:blue;">-&gt; </span>self.WriteResults())
        results.PropertyChanged.Add(<span style="color:blue;">fun </span>e <span style="color:blue;">-&gt; </span>self.WriteResults())
    <span style="color:blue;">member </span>m.Results <span style="color:blue;">with </span>get() = results
                     <span style="color:blue;">and </span>set newValue =
                        results &lt;- newValue
                        <span style="color:blue;">base</span>.RaisePropertyChangedEvent(<span style="color:maroon;">"Results"</span>)
    <span style="color:blue;">member </span>m.WriteResults () =
        <span style="color:blue;">let </span>rs = results
                 |&gt; Seq.map (<span style="color:blue;">fun </span>r <span style="color:blue;">-&gt; </span>r.Date, r.StockLong, r.StockShort, r.TrailingStop)
        <span style="color:blue;">let </span>thereAreErrors = results |&gt; Seq.exists (<span style="color:blue;">fun </span>r <span style="color:blue;">-&gt; </span>r.IsThereAnError)
        <span style="color:blue;">if </span>not thereAreErrors <span style="color:blue;">then
            </span>writeFile fileName rs</pre>

Things here are more interesting. First of all, in the constructor I load the results calling my model (which I created in [Part I](http://lucabolognese.wordpress.com/2010/03/13/tracking-spread-trades-in-f-and-hooking-up-xunit-and-fscheck-part-1/) of this series). I then subscribe to both the events fired by the collection of results. The former is triggered when an object is added/removed, the latter is triggered when an object changes one of its properties. When one of them fires, I simply write the new state back to the file. This allows me to get rid of Submit/Cancel buttons. What the user sees on the screen is synchronized with the disk at all times. The user doesn’t need to know about the file system.

If this were real, I would also implement an undo/redo mechanism. In such case, my reliance on object events might be unwise. I would probably route all the user changes through a command mechanism, so that they can be undo more easily.

That’s it for the modelview. The View itself is as follows:

<pre class="code"><span style="color:blue;">&lt;</span><span style="color:#a31515;">Window </span><span style="color:red;">x</span><span style="color:blue;">:</span><span style="color:red;">Class</span><span style="color:blue;">="SpreadTradingWPF.MainWindow"
        </span><span style="color:red;">xmlns</span><span style="color:blue;">="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        </span><span style="color:red;">xmlns</span><span style="color:blue;">:</span><span style="color:red;">x</span><span style="color:blue;">="http://schemas.microsoft.com/winfx/2006/xaml"
        </span><span style="color:red;">xmlns</span><span style="color:blue;">:</span><span style="color:red;">spreadTrading</span><span style="color:blue;">="clr-namespace:SpreadTradingWPF"
        </span><span style="color:red;">Title</span><span style="color:blue;">="Spread Trading" </span><span style="color:red;">Height</span><span style="color:blue;">="350" </span><span style="color:red;">Width</span><span style="color:blue;">="525" </span><span style="color:red;">SizeToContent</span><span style="color:blue;">="WidthAndHeight"&gt;
        &lt;</span><span style="color:#a31515;">Window.Resources</span><span style="color:blue;">&gt;
            &lt;</span><span style="color:#a31515;">spreadTrading</span><span style="color:blue;">:</span><span style="color:#a31515;">DateToShortStringConverter </span><span style="color:red;">x</span><span style="color:blue;">:</span><span style="color:red;">Key</span><span style="color:blue;">="DateToShortStringC" /&gt;
            &lt;</span><span style="color:#a31515;">LinearGradientBrush </span><span style="color:red;">x</span><span style="color:blue;">:</span><span style="color:red;">Key</span><span style="color:blue;">="BlueLightGradientBrush" </span><span style="color:red;">StartPoint</span><span style="color:blue;">="0,0" </span><span style="color:red;">EndPoint</span><span style="color:blue;">="0,1"&gt;
                    &lt;</span><span style="color:#a31515;">GradientStop </span><span style="color:red;">Offset</span><span style="color:blue;">="0" </span><span style="color:red;">Color</span><span style="color:blue;">="#FFEAF3FF"/&gt;
                    &lt;</span><span style="color:#a31515;">GradientStop </span><span style="color:red;">Offset</span><span style="color:blue;">="0.654" </span><span style="color:red;">Color</span><span style="color:blue;">="#FFC0DEFF"/&gt;
                    &lt;</span><span style="color:#a31515;">GradientStop </span><span style="color:red;">Offset</span><span style="color:blue;">="1" </span><span style="color:red;">Color</span><span style="color:blue;">="#FFC0D9FB"/&gt;
            &lt;/</span><span style="color:#a31515;">LinearGradientBrush</span><span style="color:blue;">&gt;
            &lt;</span><span style="color:#a31515;">Style </span><span style="color:red;">TargetType</span><span style="color:blue;">="{</span><span style="color:#a31515;">x</span><span style="color:blue;">:</span><span style="color:#a31515;">Type </span><span style="color:red;">DataGrid</span><span style="color:blue;">}"&gt;
                &lt;</span><span style="color:#a31515;">Setter </span><span style="color:red;">Property</span><span style="color:blue;">="Margin" </span><span style="color:red;">Value</span><span style="color:blue;">="5" /&gt;
                &lt;</span><span style="color:#a31515;">Setter </span><span style="color:red;">Property</span><span style="color:blue;">="Background" </span><span style="color:red;">Value</span><span style="color:blue;">="{</span><span style="color:#a31515;">StaticResource </span><span style="color:red;">BlueLightGradientBrush</span><span style="color:blue;">}" /&gt;
                &lt;</span><span style="color:#a31515;">Setter </span><span style="color:red;">Property</span><span style="color:blue;">="BorderBrush" </span><span style="color:red;">Value</span><span style="color:blue;">="#FFA6CCF2" /&gt;
                &lt;</span><span style="color:#a31515;">Setter </span><span style="color:red;">Property</span><span style="color:blue;">="RowBackground" </span><span style="color:red;">Value</span><span style="color:blue;">="White" /&gt;
                &lt;</span><span style="color:#a31515;">Setter </span><span style="color:red;">Property</span><span style="color:blue;">="AlternatingRowBackground" </span><span style="color:red;">Value</span><span style="color:blue;">="#FDFFD0" /&gt;
                &lt;</span><span style="color:#a31515;">Setter </span><span style="color:red;">Property</span><span style="color:blue;">="HorizontalGridLinesBrush" </span><span style="color:red;">Value</span><span style="color:blue;">="Transparent" /&gt;
                &lt;</span><span style="color:#a31515;">Setter </span><span style="color:red;">Property</span><span style="color:blue;">="VerticalGridLinesBrush" </span><span style="color:red;">Value</span><span style="color:blue;">="#FFD3D0" /&gt;
                &lt;</span><span style="color:#a31515;">Setter </span><span style="color:red;">Property</span><span style="color:blue;">="RowHeaderWidth" </span><span style="color:red;">Value</span><span style="color:blue;">="20" /&gt;
            &lt;/</span><span style="color:#a31515;">Style</span><span style="color:blue;">&gt;
    &lt;/</span><span style="color:#a31515;">Window.Resources</span><span style="color:blue;">&gt;
        &lt;</span><span style="color:#a31515;">StackPanel </span><span style="color:red;">HorizontalAlignment</span><span style="color:blue;">="Center" </span><span style="color:red;">Name</span><span style="color:blue;">="stackPanel1" </span><span style="color:red;">VerticalAlignment</span><span style="color:blue;">="Top" </span><span style="color:red;">Margin</span><span style="color:blue;">="20"&gt;
            &lt;</span><span style="color:#a31515;">TextBlock </span><span style="color:red;">Text</span><span style="color:blue;">="Spread Trading" </span><span style="color:red;">Width</span><span style="color:blue;">="135" </span><span style="color:red;">HorizontalAlignment</span><span style="color:blue;">="Center" </span><span style="color:red;">FontSize</span><span style="color:blue;">="18" </span><span style="color:red;">FontWeight</span><span style="color:blue;">="Bold" </span><span style="color:red;">FontStretch</span><span style="color:blue;">="ExtraExpanded" /&gt;
            &lt;</span><span style="color:#a31515;">DataGrid </span><span style="color:red;">Height</span><span style="color:blue;">="Auto" </span><span style="color:red;">Width</span><span style="color:blue;">="Auto" </span><span style="color:red;">Margin</span><span style="color:blue;">="5" </span><span style="color:red;">ItemsSource</span><span style="color:blue;">="{</span><span style="color:#a31515;">Binding </span><span style="color:red;">Results</span><span style="color:blue;">}" </span><span style="color:red;">CanUserAddRows </span><span style="color:blue;">="True" </span><span style="color:red;">CanUserDeleteRows</span><span style="color:blue;">="True" </span><span style="color:red;">AutoGenerateColumns</span><span style="color:blue;">="False"&gt;
                &lt;</span><span style="color:#a31515;">DataGrid.RowValidationRules</span><span style="color:blue;">&gt;
                    &lt;</span><span style="color:#a31515;">spreadTrading</span><span style="color:blue;">:</span><span style="color:#a31515;">ResultValidationRule </span><span style="color:red;">ValidationStep</span><span style="color:blue;">="UpdatedValue"/&gt;
                &lt;/</span><span style="color:#a31515;">DataGrid.RowValidationRules</span><span style="color:blue;">&gt;
                &lt;</span><span style="color:#a31515;">DataGrid.RowValidationErrorTemplate</span><span style="color:blue;">&gt;
                    &lt;</span><span style="color:#a31515;">ControlTemplate</span><span style="color:blue;">&gt;
                        &lt;</span><span style="color:#a31515;">Grid </span><span style="color:red;">Margin</span><span style="color:blue;">="0,-2,0,-2"
                              </span><span style="color:red;">ToolTip</span><span style="color:blue;">="{</span><span style="color:#a31515;">Binding </span><span style="color:red;">RelativeSource</span><span style="color:blue;">={</span><span style="color:#a31515;">RelativeSource
                              </span><span style="color:red;">FindAncestor</span><span style="color:blue;">, </span><span style="color:red;">AncestorType</span><span style="color:blue;">={</span><span style="color:#a31515;">x</span><span style="color:blue;">:</span><span style="color:#a31515;">Type </span><span style="color:red;">DataGridRow</span><span style="color:blue;">}},
                              </span><span style="color:red;">Path</span><span style="color:blue;">=(Validation.Errors)[</span><span style="color:blue;">].ErrorContent}"&gt;
                            &lt;</span><span style="color:#a31515;">Ellipse </span><span style="color:red;">StrokeThickness</span><span style="color:blue;">="0" </span><span style="color:red;">Fill</span><span style="color:blue;">="Red"
                                </span><span style="color:red;">Width</span><span style="color:blue;">="{</span><span style="color:#a31515;">TemplateBinding </span><span style="color:red;">FontSize</span><span style="color:blue;">}"
                                </span><span style="color:red;">Height</span><span style="color:blue;">="{</span><span style="color:#a31515;">TemplateBinding </span><span style="color:red;">FontSize</span><span style="color:blue;">}" /&gt;
                            &lt;</span><span style="color:#a31515;">TextBlock </span><span style="color:red;">Text</span><span style="color:blue;">="!" </span><span style="color:red;">FontSize</span><span style="color:blue;">="{</span><span style="color:#a31515;">TemplateBinding </span><span style="color:red;">FontSize</span><span style="color:blue;">}"
                                </span><span style="color:red;">FontWeight</span><span style="color:blue;">="Bold" </span><span style="color:red;">Foreground</span><span style="color:blue;">="White"
                                </span><span style="color:red;">HorizontalAlignment</span><span style="color:blue;">="Center"  /&gt;
                        &lt;/</span><span style="color:#a31515;">Grid</span><span style="color:blue;">&gt;
                    &lt;/</span><span style="color:#a31515;">ControlTemplate</span><span style="color:blue;">&gt;
                &lt;/</span><span style="color:#a31515;">DataGrid.RowValidationErrorTemplate</span><span style="color:blue;">&gt;
            &lt;</span><span style="color:#a31515;">DataGrid.Columns</span><span style="color:blue;">&gt;
                    &lt;</span><span style="color:#a31515;">DataGridTextColumn </span><span style="color:red;">Header</span><span style="color:blue;">="Date" </span><span style="color:red;">Binding</span><span style="color:blue;">="{</span><span style="color:#a31515;">Binding </span><span style="color:red;">Date</span><span style="color:blue;">, </span><span style="color:red;">Converter</span><span style="color:blue;">= {</span><span style="color:#a31515;">StaticResource </span><span style="color:red;">DateToShortStringC</span><span style="color:blue;">}}"  </span><span style="color:red;">IsReadOnly</span><span style="color:blue;">="false"/&gt;
                    &lt;</span><span style="color:#a31515;">DataGridTextColumn </span><span style="color:red;">Header</span><span style="color:blue;">="Long" </span><span style="color:red;">Binding</span><span style="color:blue;">="{</span><span style="color:#a31515;">Binding </span><span style="color:red;">StockLong</span><span style="color:blue;">}"/&gt;
                    &lt;</span><span style="color:#a31515;">DataGridTextColumn </span><span style="color:red;">Header</span><span style="color:blue;">="Short" </span><span style="color:red;">Binding</span><span style="color:blue;">="{</span><span style="color:#a31515;">Binding </span><span style="color:red;">StockShort</span><span style="color:blue;">}" /&gt;
                    &lt;</span><span style="color:#a31515;">DataGridTextColumn </span><span style="color:red;">Header</span><span style="color:blue;">="Stop" </span><span style="color:red;">Binding</span><span style="color:blue;">="{</span><span style="color:#a31515;">Binding </span><span style="color:red;">TrailingStop</span><span style="color:blue;">}" /&gt;
            &lt;/</span><span style="color:#a31515;">DataGrid.Columns</span><span style="color:blue;">&gt;
            &lt;/</span><span style="color:#a31515;">DataGrid</span><span style="color:blue;">&gt;
        &lt;/</span><span style="color:#a31515;">StackPanel</span><span style="color:blue;">&gt;
&lt;/</span><span style="color:#a31515;">Window</span><span style="color:blue;">&gt;
</span></pre>

Notice that I styled the grid and I used the right incantations to get validation errors and to bind things properly. The _DateToShortString_ converter used for the date field might be mildly interesting. It’s in the _Utilities.cs_ file together with a validation rule that just delegates to the _IsThereAnError_ method on each entity. In a bigger application, you could write this code in a much more reusable way.

<pre class="code">[<span style="color:#2b91af;">ValueConversion</span>(<span style="color:blue;">typeof </span>(<span style="color:#2b91af;">DateTime</span>), <span style="color:blue;">typeof </span>(<span style="color:blue;">string</span>))]
<span style="color:blue;">public class </span><span style="color:#2b91af;">DateToShortStringConverter </span>: <span style="color:#2b91af;">IValueConverter
</span>{
<span style="color:blue;">public </span><span style="color:#2b91af;">Object </span>Convert(
        <span style="color:#2b91af;">Object </span>value,
        <span style="color:#2b91af;">Type </span>targetType,
        <span style="color:#2b91af;">Object </span>parameter,
        <span style="color:#2b91af;">CultureInfo </span>culture)
{
    <span style="color:blue;">var </span>date = (<span style="color:#2b91af;">DateTime</span>) value;
    <span style="color:blue;">return </span>date.ToShortDateString();
}
<span style="color:blue;">public object </span>ConvertBack(
    <span style="color:blue;">object </span>value,
    <span style="color:#2b91af;">Type </span>targetType,
    <span style="color:blue;">object </span>parameter,
    <span style="color:#2b91af;">CultureInfo </span>culture)
    {
        <span style="color:blue;">string </span>strValue = value <span style="color:blue;">as string</span>;
        <span style="color:#2b91af;">DateTime </span>resultDateTime;
        <span style="color:blue;">if </span>(<span style="color:#2b91af;">DateTime</span>.TryParse(strValue, <span style="color:blue;">out </span>resultDateTime))
        {
            <span style="color:blue;">return </span>resultDateTime;
        }
        <span style="color:blue;">return </span><span style="color:#2b91af;">DependencyProperty</span>.UnsetValue;
    }
}
<span style="color:blue;">public class </span><span style="color:#2b91af;">ResultValidationRule </span>: <span style="color:#2b91af;">ValidationRule
</span>{
    <span style="color:blue;">public override </span><span style="color:#2b91af;">ValidationResult </span>Validate(<span style="color:blue;">object </span>value, <span style="color:#2b91af;">CultureInfo </span>cultureInfo)
    {
        <span style="color:blue;">var </span>result = (value <span style="color:blue;">as </span><span style="color:#2b91af;">BindingGroup</span>).Items[0] <span style="color:blue;">as </span><span style="color:#2b91af;">ResultViewModel</span>;
        <span style="color:blue;">if</span>(result.IsThereAnError)
            <span style="color:blue;">return new </span><span style="color:#2b91af;">ValidationResult</span>(<span style="color:blue;">false</span>, <span style="color:#a31515;">"TrailingStop must be between 0 and 100"</span>);
        <span style="color:blue;">else
            return </span><span style="color:#2b91af;">ValidationResult</span>.ValidResult;
    }
}</pre>



After all these niceties, this is what you get.

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="/wp-content/uploads/2010/03/image_thumb.png" width="244" height="219" />](/wp-content/uploads/2010/03/image.png)