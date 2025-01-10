---
id: 1070
title: 'An Async Html cache – Part I - Writing the cache'
date: 2009-04-27T19:57:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/04/27/an-async-html-cache-part-i-writing-the-cache/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2009/04/27/an-async-html-cache-part-i.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9572478"
orig_parent_id:
  - "9572478"
orig_thread_id:
  - "651250"
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
  - "0"
orig_url_title:
  - http://blogs.msdn.com/b/lucabol/archive/2009/04/27/an-async-html-cache-part-i-writing-the-cache.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="An Async Html cache &ndash; Part I  - Writing the cache" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/04/27/an-async-html-cache-part-i-writing-the-cache/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts: Part II  - Testing the cache In the process of converting a financial VBA Excel Addin to .NET (more on that in later posts), I found myself in dire need of a HTML cache that can be called from multiple threads without blocking them. Visualize it as a glorified dictionary where each entry..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="An Async Html cache &ndash; Part I  - Writing the cache" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/04/27/an-async-html-cache-part-i-writing-the-cache/" />
    <meta name="twitter:description" content="Other posts: Part II  - Testing the cache In the process of converting a financial VBA Excel Addin to .NET (more on that in later posts), I found myself in dire need of a HTML cache that can be called from multiple threads without blocking them. Visualize it as a glorified dictionary where each entry..." />
    
restapi_import_id:
  - 5c011e0505e67
original_post_id:
  - "263"
categories:
  - Uncategorized
tags:
  - VB
---
Other posts:

  * **<font color="#006bad"><a href="http://blogs.msdn.com/lucabol/">Part II  - Testing the cache</a></font>**

In the process of converting a financial VBA Excel Addin to .NET (more on that in later posts), I found myself in dire need of a HTML cache that can be called from multiple threads without blocking them. Visualize it as a glorified dictionary where each entry is (url, cachedHtml). The only difference is that when you get the page, you pass a callback to be invoked when the html has been loaded (which could be immediately if the html had already been retrieved by someone else).

In essence, I want this:

```vbnet
Public Sub GetHtmlAsync(ByVal url As String, ByVal callback As Action(Of String))
```

I'm not a big expert in the [.Net Parallel Extensions](http://msdn.microsoft.com/en-us/concurrency/default.aspx), but I've got [help](http://blogs.msdn.com/pfxteam). Stephen Toub helped so much with this that he could have blogged about it himself. And, by the way, this code runs on Visual Studio 2010, which we haven't shipped yet. I believe with some modifications, it can be run in 2008 + .Net Parallel Extensions CTP, but you'll have to change a bunch of names.

In any case, here it comes. First, let's add some imports.

```vbnet
Imports System.Collections.Concurrent
Imports System.Threading.Tasks
Imports System.Threading
Imports System.Net
```

Then, let's define an asynchronous cache.

```vbnet
Public Class AsyncCache(Of TKey, TValue)
```

This thing needs to store the (url, html) pairs somewhere and, luckily enough, there is an handy _ConcurrentDictionary_ that I can use. Also the cache needs to know how to load a _TValue_ given a _TKey_. In 'programmingese', that means.

```vbnet
Private _loader As Func(Of TKey, TValue)
Private _map As New ConcurrentDictionary(Of TKey, Task(Of TValue))
```

I'll need a way to create it.

```vbnet
Public Sub New(ByVal l As Func(Of TKey, TValue))
    _loader = l
End Sub
```

Notice in the above code the use of the _Task_ class for my dictionary instead of _TValue_. Task is a very good abstraction for "do some work asynchronously and call me when you are done". It's easy to initialize and it's easy to attach callbacks to it. Indeed, this is what we'll do next:

```vbnet
Public Sub GetValueAsync(ByVal key As TKey, ByVal callback As Action(Of TValue))
    Dim task As Task(Of TValue) = Nothing
    If Not _map.TryGetValue(key, task) Then
        task = New Task(Of TValue)(Function() _loader(key), TaskCreationOptions.DetachedFromParent)
        If _map.TryAdd(key, task) Then
            task.Start()
        Else
            task.Cancel()
            _map.TryGetValue(key, task)
        End If
    End If
    task.ContinueWith(Sub(t) callback(t.Result))
End Sub
```

Wow. Ok, let me explain. This method is divided in two parts. The first part is just a thread safe way to say "give me the task corresponding to this key or, if the task hasn't been inserted in the cache yet, create it and insert it". The second part just says "add callback to the list of functions to be called when the task has finished running".

The first part needs some more explanation. What is TaskCreationOptions.DetachedFromParent? It essentially says that the created task is not going to prevent the parent task from terminating. In essence, the task that created the child task won't wait for its conclusion. The rest is better explained in comments.

```vbnet
If Not _map.TryGetValue(key, task) Then ' Is the task in the cache? (Loc. X)
    task = New Task(Of TValue)(Function() _loader(key), TaskCreationOptions.DetachedFromParent) ' No, create it
    If _map.TryAdd(key, task) Then ' Try to add it
        task.Start() ' I succeeded. I'm the one who added this task. I can safely start it.
    Else
        task.Cancel() ' I failed, someone inserted the task after I checked in (Loc. X). Cancel it.
        _map.TryGetValue(key, task) ' And get the one that someone inserted
    End If
End If
```

Got it? Well, I admit I trust Stephen that this is what I should do …

I can then create my little HTML Cache by using the above class as in:

```vbnet
Public Class HtmlCache
    Public Sub GetHtmlAsync(ByVal url As String, ByVal callback As Action(Of String))
        _asyncCache.GetValueAsync(url, callback)
    End Sub
    Private Function LoadWebPage(ByVal url As String) As String
        Using client As New WebClient()
            'Test.PrintThread("Downloading on thread {0} ...")
            Return client.DownloadString(url)
        End Using
    End Function
    Private _asyncCache As New AsyncCache(Of String, String)(AddressOf LoadWebPage)
End Class
```

I have no idea why coloring got disabled when I copy/paste. It doesn't matter, this is trivial. I just create an _AsyncCache_ and initialize it with a method that knows how to load a web page. I then simply implement _GetHtmlAsync_ by delegating to the underlying _GetValueAsync_ on _AsyncCache_.

It is somehow bizarre to call _Webclient.DownloadString_, when the design could be revised to take advantage of its asynchronous version. Maybe I'll do it in another post. Next time, I'll write code to use this thing.
