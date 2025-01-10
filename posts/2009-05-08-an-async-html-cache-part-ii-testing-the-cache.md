---
id: 1069
title: An Async Html cache – part II – Testing the cache
date: 2009-05-08T11:34:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/05/08/an-async-html-cache-part-ii-testing-the-cache/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/05/08/an-async-html-cache-part-ii-testing-the-cache.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9589057"
orig_parent_id:
  - "9589057"
orig_thread_id:
  - "652766"
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
  - http://blogs.msdn.com/b/lucabol/archive/2009/05/08/an-async-html-cache-part-ii-testing-the-cache.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="An Async Html cache &ndash; part II &ndash; Testing the cache" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/05/08/an-async-html-cache-part-ii-testing-the-cache/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts: Part I – Writing the cache Let's try out our little cache. First I want to write a synchronous version of it as a baseline. Private Shared Sub TestSync(ByVal sites() As String, ByVal sitesToDownload As Integer, ByVal howLong As Integer) Dim syncCache As New Dictionary(Of String, String) Dim count = sites.Count() Dim url1..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="An Async Html cache &ndash; part II &ndash; Testing the cache" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/05/08/an-async-html-cache-part-ii-testing-the-cache/" />
    <meta name="twitter:description" content="Other posts: Part I – Writing the cache Let's try out our little cache. First I want to write a synchronous version of it as a baseline. Private Shared Sub TestSync(ByVal sites() As String, ByVal sitesToDownload As Integer, ByVal howLong As Integer) Dim syncCache As New Dictionary(Of String, String) Dim count = sites.Count() Dim url1..." />
    
restapi_import_id:
  - 5c011e0505e67
original_post_id:
  - "253"
categories:
  - Uncategorized
tags:
  - VB
---
Other posts:

  * [Part I – Writing the cache](http://blogs.msdn.com/lucabol/archive/2009/04/27/an-async-html-cache-part-i.aspx) 

Let's try out our little cache. First I want to write a synchronous version of it as a baseline.

```vbnet
Private Shared Sub TestSync(ByVal sites() As String, ByVal sitesToDownload As Integer, ByVal howLong As Integer)
    Dim syncCache As New Dictionary(Of String, String)
    Dim count = sites.Count()
    Dim url1 = "http://moneycentral.msn.com/investor/invsub/results/statemnt.aspx?Symbol="
    For i = 0 To sitesToDownload - 1
        Dim html As String = ""
        Dim url = url1 & sites(i Mod count)
        If Not syncCache.TryGetValue(url, html) Then
            html = LoadWebPage(url)
            syncCache(url) = html
        End If
        DoWork(html, howLong)
    Next
End Sub
```

This is a loop that loads webpages in the cache if they are not already there. _sites_ is a list of tickers used to compose the urls; _sitesToDownload_ is the total number of sites to download, so that a single url can be loaded multiple times; _howLong_ represents the work to be done on each loaded page.

In this version the cache is simply a _Dictionary_ and there is no parallelism. The two bold lines is where the cache is managed.

_DoWork_ is this.

```vbnet
Public Shared Sub DoWork(ByVal html As String, ByVal howLong As Integer)
    Thread.Sleep(howLong)
End Sub
```

Let's take a look at the asynchronous version.

```vbnet
Private Shared Sub TestAsync(ByVal sites() As String, ByVal sitesToDownload As Integer, ByVal howLong As Integer)
    Dim htmlCache As New HtmlCache
    Dim count = sites.Count()
    Dim url = "http://moneycentral.msn.com/investor/invsub/results/statemnt.aspx?Symbol="
    Using ce = New CountdownEvent(sitesToDownload)
        For i = 1 To sitesToDownload
            htmlCache.GetHtmlAsync(
                url & sites(i Mod count),
                Sub(s)
                    DoWork(s, howLong)
                    ce.Signal()
                End Sub)
        Next
        ce.Wait()
    End Using
```

There are several points worth making on this:

  * The lambda used as second parameter for _GetHtmlAsync_ is invoked on a different thread whenever the html has been retrieved (which could be immediately if the cache has downloaded the url before) 
  * _CountDownEvent_ allows a thread to wait for a certain number of signals to be sent. The waiting happens on the main thread in the _ce.Wait()_ instruction. The triggering of the event happens in the lambda described in the point above (the _ce.Signal()_ instruction) 

This is the driver for the overall testing.

```vbnet
Private Shared Sub TestPerf(ByVal s As String, ByVal a As Action, ByVal iterations As Integer)
    Dim clock As New Stopwatch
    clock.Start()
    For i = 1 To iterations
        a()
    Next
    clock.Stop()
    Dim ts = clock.Elapsed
    Dim elapsedTime = String.Format(s & ": {0:00}:{1:00}:{2:00}.{3:00}", ts.Hours, ts.Minutes, ts.Seconds, ts.Milliseconds / 10)
    Console.WriteLine(elapsedTime, "RunTime")
End Sub
```

There is not much to say about it. Start the clock, perform a bunch of iterations of the passed lambda, stop the clock, print out performance.

And finally the main method. Note that all the adjustable parameters are factored out before the calls to _TestPerf_.

```vbnet
Public Shared Sub Main()
    Dim tickers = New String() {"mmm", "aos", "shlm", "cas", "abt", "anf", "abm", "akr", "acet", "afl", "agl", "adc", "apd",
                               "ayr", "alsk", "ain", "axb", "are", "ale", "ab", "all"}
    Dim sitesToDownload = 50
    Dim workToDoOnEachUrlInMilliSec = 20
    Dim perfIterations = 5
    TestPerf("Async", Sub() TestAsync(tickers, sitesToDownload, workToDoOnEachUrlInMilliSec), perfIterations)
    TestPerf("Sync", Sub() TestSync(tickers, sitesToDownload, workToDoOnEachUrlInMilliSec), perfIterations)
End Sub
```

Feel free to change (_tickers_, _sitesToDownload_, _workToDoOnEachUrlInMilliSec_, _perfIterations_). Depending on the ratios between these parameters and the number of cores on your machine, you're going to see different results. Which highlights the fact that parallelizing your algorithms can yield performance gains or not depending on both software and hardware considerations. I get ~3X improvement on my box. I attached the full source file for your amusement. 

[AsyncCache.vb](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/09/58/90/57/AsyncCache.vb)
