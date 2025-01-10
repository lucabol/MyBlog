---
id: 33
title: 'Tracking spread trades in F# (and WPF MVVM) – Part II'
date: 2010-03-19T23:33:00+00:00
author: lucabol
layout: post
guid: http://lucabolognese.wordpress.com/2010/03/19/tracking-spread-trades-in-f-and-wpf-mvvm-part-ii/
categories:
  - fsharp
tags:
  - fsharp
  - Financial
---
I wanted to experiment with MVVM and WPF in F#, so I decided to create a little graphical interface for the csv file that drives the spread tracking application. When I started I thought I needed some kind of a grid with Submit/Cancel buttons, but the more I thought about it, the more I realized that I wouldn't need them.

See, I've always be one to complain about our current paradigm of Open File / Close File / Save File arguing that the user shouldn't know about an entity called 'file'. He shouldn't be exposed to the fact that the application is just an in-memory copy of an hard disk artifact. His mental model should simply be: I open a document, I work on it, I close it, if needed I can make a copy; if I have problems I can revert to a previous version of the same document; If I make an error I can use 'undo' to revert it. There are no files/save/submit/cancel in such paradigm. There is no file system.

On the technical side I wanted to experiment with MVVM, even if in this case, the paradigm is overkilled (can really use this word?), given the simplicity of the application.

In any case, the ViewModel is in F#. It uses two utility classes:

```fsharp
// TODO: refactor to remove code repetition below
[<AbstractClass>]
type ViewModelBase () =
    let propertyChanged = new Event<PropertyChangedEventHandler, PropertyChangedEventArgs>()
    interface INotifyPropertyChanged with
        [<CLIEvent>]
        member this.PropertyChanged = propertyChanged.Publish
    member internal this.RaisePropertyChangedEvent(propertyName:string) =
        if not(propertyName = null) then
            let e = new PropertyChangedEventArgs(propertyName)
            let i = this :> INotifyPropertyChanged
            propertyChanged.Trigger(this, e)
type ObservableCollectionWithChanges<'a when 'a :> INotifyPropertyChanged> () =
    inherit ObservableCollection<'a> ()
    let propertyChanged = new Event<PropertyChangedEventHandler, PropertyChangedEventArgs>()
    member c.PropertyChanged = propertyChanged.Publish
    member private c.RaisePropertyChangedEvent(propertyName:string) =
        if not(propertyName = null) then
            let e = new PropertyChangedEventArgs(propertyName)
            let i = c :> INotifyPropertyChanged
            propertyChanged.Trigger(c, e)
    member c.Add(o) =
        base.Add(o)
        o.PropertyChanged.Add(fun x -> c.RaisePropertyChangedEvent(""))
```

The first one is used as a base for all the viewmodel entities in the application, the second one serves as the base for all the collections. They both define the customary _PropertyChanged_ event. The latter adds itself as an observer to each object added to the collection so that, whenever one changes, it gets notified and can notify its own observers. Look at the _c.Add_ method. A lot of repetitive code here, I would heed the advice of the comment on top if this were production code.

Each line in the csv file is represented as a ResultViewModel, hence the following:

```fsharp
type ResultViewModel (d:DateTime, sLong, sShort, tStop) =
    inherit ViewModelBase ()
    let mutable date = d
    let mutable stockLong = sLong
    let mutable stockShort = sShort
    let mutable trailingStop = tStop
    new () = new ResultViewModel(DateTime.Today, "", "", 0)
    member r.Date with get() = date
                       and set newValue =
                            date <- newValue
                            base.RaisePropertyChangedEvent("Date")
    member r.StockLong with get() = stockLong
                       and set newValue =
                            stockLong <- newValue
                            base.RaisePropertyChangedEvent("StockLong")
    member r.StockShort with get() = stockShort
                        and set newValue =
                            stockShort <- newValue
                            base.RaisePropertyChangedEvent("StockShort")
    member r.TrailingStop with get() =
                                trailingStop
                          and set newValue =
                                trailingStop <- newValue
                                base.RaisePropertyChangedEvent("TrailingStop")
    member r.IsThereAnError = r.TrailingStop < 0 || r.TrailingStop > 100
```

I need the empty constructor to be able to hook up to the DataGrid add-new capability. There might be an event I could use instead, but this is simple enough (even if a bit goofy).

The main view model class then looks like the following:

```fsharp
type MainViewModel (fileName:string) as self =
    inherit ViewModelBase ()
    let mutable results = new ObservableCollectionWithChanges<ResultViewModel>()
    let loadResults () =
        parseFile fileName
        |> Array.iter (fun (d,sl, ss, ts) ->
                        results.Add(new ResultViewModel(d, sl, ss, ts)))
    do
        loadResults ()
        results.CollectionChanged.Add(fun e -> self.WriteResults())
        results.PropertyChanged.Add(fun e -> self.WriteResults())
    member m.Results with get() = results
                     and set newValue =
                        results <- newValue
                        base.RaisePropertyChangedEvent("Results")
    member m.WriteResults () =
        let rs = results
                 |> Seq.map (fun r -> r.Date, r.StockLong, r.StockShort, r.TrailingStop)
        let thereAreErrors = results |> Seq.exists (fun r -> r.IsThereAnError)
        if not thereAreErrors then
            writeFile fileName rs
```

Things here are more interesting. First of all, in the constructor I load the results calling my model (which I created in [Part I](http://lucabolognese.wordpress.com/2010/03/13/tracking-spread-trades-in-f-and-hooking-up-xunit-and-fscheck-part-1/) of this series). I then subscribe to both the events fired by the collection of results. The former is triggered when an object is added/removed, the latter is triggered when an object changes one of its properties. When one of them fires, I simply write the new state back to the file. This allows me to get rid of Submit/Cancel buttons. What the user sees on the screen is synchronized with the disk at all times. The user doesn't need to know about the file system.

If this were real, I would also implement an undo/redo mechanism. In such case, my reliance on object events might be unwise. I would probably route all the user changes through a command mechanism, so that they can be undo more easily.

That's it for the modelview. The View itself is as follows:

```xml
<Window x:Class="SpreadTradingWPF.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:spreadTrading="clr-namespace:SpreadTradingWPF"
        Title="Spread Trading" Height="350" Width="525" SizeToContent="WidthAndHeight">
        <Window.Resources>
            <spreadTrading:DateToShortStringConverter x:Key="DateToShortStringC" />
            <LinearGradientBrush x:Key="BlueLightGradientBrush" StartPoint="0,0" EndPoint="0,1">
                    <GradientStop Offset="0" Color="#FFEAF3FF"/>
                    <GradientStop Offset="0.654" Color="#FFC0DEFF"/>
                    <GradientStop Offset="1" Color="#FFC0D9FB"/>
            </LinearGradientBrush>
            <Style TargetType="{x:Type DataGrid}">
                <Setter Property="Margin" Value="5" />
                <Setter Property="Background" Value="{StaticResource BlueLightGradientBrush}" />
                <Setter Property="BorderBrush" Value="#FFA6CCF2" />
                <Setter Property="RowBackground" Value="White" />
                <Setter Property="AlternatingRowBackground" Value="#FDFFD0" />
                <Setter Property="HorizontalGridLinesBrush" Value="Transparent" />
                <Setter Property="VerticalGridLinesBrush" Value="#FFD3D0" />
                <Setter Property="RowHeaderWidth" Value="20" />
            </Style>
    </Window.Resources>
        <StackPanel HorizontalAlignment="Center" Name="stackPanel1" VerticalAlignment="Top" Margin="20">
            <TextBlock Text="Spread Trading" Width="135" HorizontalAlignment="Center" FontSize="18" FontWeight="Bold" FontStretch="ExtraExpanded" />
            <DataGrid Height="Auto" Width="Auto" Margin="5" ItemsSource="{Binding Results}" CanUserAddRows ="True" CanUserDeleteRows="True" AutoGenerateColumns="False">
                <DataGrid.RowValidationRules>
                    <spreadTrading:ResultValidationRule ValidationStep="UpdatedValue"/>
                </DataGrid.RowValidationRules>
                <DataGrid.RowValidationErrorTemplate>
                    <ControlTemplate>
                        <Grid Margin="0,-2,0,-2"
                              ToolTip="{Binding RelativeSource={RelativeSource
                              FindAncestor, AncestorType={x:Type DataGridRow}},
                              Path=(Validation.Errors)[].ErrorContent}">
                            <Ellipse StrokeThickness="0" Fill="Red"
                                Width="{TemplateBinding FontSize}"
                                Height="{TemplateBinding FontSize}" />
                            <TextBlock Text="!" FontSize="{TemplateBinding FontSize}"
                                FontWeight="Bold" Foreground="White"
                                HorizontalAlignment="Center"  />
                        </Grid>
                    </ControlTemplate>
                </DataGrid.RowValidationErrorTemplate>
            <DataGrid.Columns>
                    <DataGridTextColumn Header="Date" Binding="{Binding Date, Converter= {StaticResource DateToShortStringC}}"  IsReadOnly="false"/>
                    <DataGridTextColumn Header="Long" Binding="{Binding StockLong}"/>
                    <DataGridTextColumn Header="Short" Binding="{Binding StockShort}" />
                    <DataGridTextColumn Header="Stop" Binding="{Binding TrailingStop}" />
            </DataGrid.Columns>
            </DataGrid>
        </StackPanel>
</Window>
```

Notice that I styled the grid and I used the right incantations to get validation errors and to bind things properly. The _DateToShortString_ converter used for the date field might be mildly interesting. It's in the _Utilities.cs_ file together with a validation rule that just delegates to the _IsThereAnError_ method on each entity. In a bigger application, you could write this code in a much more reusable way.

```csharp
[ValueConversion(typeof (DateTime), typeof (string))]
public class DateToShortStringConverter : IValueConverter
{
public Object Convert(
        Object value,
        Type targetType,
        Object parameter,
        CultureInfo culture)
{
    var date = (DateTime) value;
    return date.ToShortDateString();
}
public object ConvertBack(
    object value,
    Type targetType,
    object parameter,
    CultureInfo culture)
    {
        string strValue = value as string;
        DateTime resultDateTime;
        if (DateTime.TryParse(strValue, out resultDateTime))
        {
            return resultDateTime;
        }
        return DependencyProperty.UnsetValue;
    }
}
public class ResultValidationRule : ValidationRule
{
    public override ValidationResult Validate(object value, CultureInfo cultureInfo)
    {
        var result = (value as BindingGroup).Items[0] as ResultViewModel;
        if(result.IsThereAnError)
            return new ValidationResult(false, "TrailingStop must be between 0 and 100");
        else
            return ValidationResult.ValidResult;
    }
}
```

After all these niceties, this is what you get.

[<img style="border-bottom:0;border-left:0;display:inline;border-top:0;border-right:0;" title="image" border="0" alt="image" src="/img/spread-trades1.png" width="244" height="219" />](/img/spread-trades1.png)
