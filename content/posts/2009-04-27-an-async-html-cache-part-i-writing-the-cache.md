---
id: 1070
title: 'An Async Html cache – Part I - Writing the cache'
date: 2009-04-27T19:57:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2009/04/27/an-async-html-cache-part-i-writing-the-cache/
permalink: /2009/04/27/an-async-html-cache-part-i-writing-the-cache/
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
  - .NET Futures
  - VB
---
Other posts:

  * **<font color="#006bad"><a href="http://blogs.msdn.com/lucabol/">Part II  - Testing the cache</a></font>**

In the process of converting a financial VBA Excel Addin to .NET (more on that in later posts), I found myself in dire need of a HTML cache that can be called from multiple threads without blocking them. Visualize it as a glorified dictionary where each entry is (url, cachedHtml). The only difference is that when you get the page, you pass a callback to be invoked when the html has been loaded (which could be immediately if the html had already been retrieved by someone else).

In essence, I want this:

<pre class="code"><span style="background:white;">    </span><span style="background:white;color:blue;">Public Sub </span><span style="background:white;">GetHtmlAsync(</span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">url </span><span style="background:white;color:blue;">As String</span><span style="background:white;">, </span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">callback </span><span style="background:white;color:blue;">As </span><span style="background:white;color:#2b91af;">Action</span><span style="background:white;">(</span><span style="background:white;color:blue;">Of String</span><span style="background:white;">))</span></pre>

I’m not a big expert in the [.Net Parallel Extensions](http://msdn.microsoft.com/en-us/concurrency/default.aspx), but I’ve got [help](http://blogs.msdn.com/pfxteam). Stephen Toub helped so much with this that he could have blogged about it himself. And, by the way, this code runs on Visual Studio 2010, which we haven’t shipped yet. I believe with some modifications, it can be run in 2008 + .Net Parallel Extensions CTP, but you’ll have to change a bunch of names.

In any case, here it comes. First, let’s add some imports.

<pre class="code"><span style="background:white;">Imports </span><span style="background:white;color:black;">System.Collections.Concurrent
</span><span style="background:white;">Imports </span><span style="background:white;color:black;">System.Threading.Tasks
</span><span style="background:white;">Imports </span><span style="background:white;color:black;">System.Threading
</span><span style="background:white;">Imports </span><span style="background:white;color:black;">System.</span><span style="background:white;color:#0000a5;">Net</span></pre>

Then, let’s define an asynchronous cache.

<pre class="code"><span style="background:white;">Public Class </span><span style="background:white;color:#2b91af;">AsyncCache</span><span style="background:white;color:black;">(</span><span style="background:white;">Of </span><span style="background:white;color:black;">TKey, </span><span style="background:white;color:#0000a5;">TValue</span><span style="background:white;color:black;">)</span></pre>

This thing needs to store the (url, html) pairs somewhere and, luckily enough, there is an handy _ConcurrentDictionary_ that I can use. Also the cache needs to know how to load a _TValue_ given a _TKey_. In ‘programmingese’, that means.

<pre class="code"><span style="background:white;">    </span><span style="background:white;color:blue;">Private </span><span style="background:white;">_loader </span><span style="background:white;color:blue;">As </span><span style="background:white;color:#2b91af;">Func</span><span style="background:white;">(</span><span style="background:white;color:blue;">Of </span><span style="background:white;color:#2b91af;">TKey</span><span style="background:white;">, </span><span style="background:white;color:#2b91af;">TValue</span><span style="background:white;">)
    </span><span style="background:white;color:blue;">Private </span><span style="background:white;">_map </span><span style="background:white;color:blue;">As New </span><span style="background:white;color:#2b91af;">ConcurrentDictionary</span><span style="background:white;">(</span><span style="background:white;color:blue;">Of </span><span style="background:white;color:#2b91af;">TKey</span><span style="background:white;">, </span><span style="background:white;color:#2b91af;">Task</span><span style="background:white;">(</span><span style="background:white;color:blue;">Of </span><span style="background:white;color:#2b91af;">TValue</span><span style="background:white;">))</span></pre>

I’ll need a way to create it.

<pre class="code"><span style="background:white;">    </span><span style="background:white;color:blue;">Public Sub New</span><span style="background:white;">(</span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">l </span><span style="background:white;color:blue;">As </span><span style="background:white;color:#2b91af;">Func</span><span style="background:white;">(</span><span style="background:white;color:blue;">Of </span><span style="background:white;color:#2b91af;">TKey</span><span style="background:white;">, </span><span style="background:white;color:#2b91af;">TValue</span><span style="background:white;">))
        _loader = l
    </span><span style="background:white;color:blue;">End Sub</span></pre>

Notice in the above code the use of the _Task_ class for my dictionary instead of _TValue_. Task is a very good abstraction for “do some work asynchronously and call me when you are done”. It’s easy to initialize and it’s easy to attach callbacks to it. Indeed, this is what we’ll do next:

<pre class="code"><span style="background:white;">    </span><span style="background:white;color:blue;">Public Sub </span><span style="background:white;">GetValueAsync(</span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">key </span><span style="background:white;color:blue;">As </span><span style="background:white;color:#2b91af;">TKey</span><span style="background:white;">, </span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">callback </span><span style="background:white;color:blue;">As </span><span style="background:white;color:#2b91af;">Action</span><span style="background:white;">(</span><span style="background:white;color:blue;">Of </span><span style="background:white;color:#2b91af;">TValue</span><span style="background:white;">))
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">task </span><span style="background:white;color:blue;">As </span><span style="background:white;color:#2b91af;">Task</span><span style="background:white;">(</span><span style="background:white;color:blue;">Of </span><span style="background:white;color:#2b91af;">TValue</span><span style="background:white;">) = </span><span style="background:white;color:blue;">Nothing
        If Not </span><span style="background:white;">_map.TryGetValue(key, task) </span><span style="background:white;color:blue;">Then
            </span><span style="background:white;">task = </span><span style="background:white;color:blue;">New </span><span style="background:white;color:#2b91af;">Task</span><span style="background:white;">(</span><span style="background:white;color:blue;">Of </span><span style="background:white;color:#2b91af;">TValue</span><span style="background:white;">)(</span><span style="background:white;color:blue;">Function</span><span style="background:white;">() _loader(key), </span><span style="background:white;color:#2b91af;">TaskCreationOptions</span><span style="background:white;">.DetachedFromParent)
            </span><span style="background:white;color:blue;">If </span><span style="background:white;">_map.TryAdd(key, task) </span><span style="background:white;color:blue;">Then
                </span><span style="background:white;color:#2b91af;">task</span><span style="background:white;">.Start()
            </span><span style="background:white;color:blue;">Else
                </span><span style="background:white;color:#2b91af;">task</span><span style="background:white;">.Cancel()
                _map.TryGetValue(key, task)
            </span><span style="background:white;color:blue;">End If
        End If
        </span><span style="background:white;color:#2b91af;">task</span><span style="background:white;">.ContinueWith(</span><span style="background:white;color:blue;">Sub</span><span style="background:white;">(t) callback(t.Result))
    </span><span style="background:white;color:blue;">End Sub</span></pre>

Wow. Ok, let me explain. This method is divided in two parts. The first part is just a thread safe way to say “give me the task corresponding to this key or, if the task hasn’t been inserted in the cache yet, create it and insert it”. The second part just says “add callback to the list of functions to be called when the task has finished running”.

The first part needs some more explanation. What is <span style="background:white;color:#2b91af;">TaskCreationOptions</span><span style="background:white;">.DetachedFromParent? It essentially says that the created task is not going to prevent the parent task from terminating. In essence, the task that created the child task won’t wait for its conclusion. The rest is better explained in comments.</span>

<pre class="code"><span style="background:white;">        </span><span style="background:white;color:blue;">If Not </span><span style="background:white;">_map.TryGetValue(key, task) </span><span style="background:white;color:blue;">Then </span><span style="background:white;color:green;">' Is the task in the cache? (Loc. X)
            </span><span style="background:white;">task = </span><span style="background:white;color:blue;">New </span><span style="background:white;color:#2b91af;">Task</span><span style="background:white;">(</span><span style="background:white;color:blue;">Of </span><span style="background:white;color:#2b91af;">TValue</span><span style="background:white;">)(</span><span style="background:white;color:blue;">Function</span><span style="background:white;">() _loader(key), </span><span style="background:white;color:#2b91af;">TaskCreationOptions</span><span style="background:white;">.DetachedFromParent) </span><span style="background:white;color:green;">' No, create it
            </span><span style="background:white;color:blue;">If </span><span style="background:white;">_map.TryAdd(key, task) </span><span style="background:white;color:blue;">Then </span><span style="background:white;color:green;">' Try to add it
                </span><span style="background:white;color:#2b91af;">task</span><span style="background:white;">.Start() </span><span style="background:white;color:green;">' I succeeded. I’m the one who added this task. I can safely start it.
            </span><span style="background:white;color:blue;">Else
                </span><span style="background:white;color:#2b91af;">task</span><span style="background:white;">.Cancel() </span><span style="background:white;color:green;">' I failed, someone inserted the task after I checked in (Loc. X). Cancel it.
                </span><span style="background:white;">_map.TryGetValue(key, task) </span><span style="background:white;color:green;">' And get the one that someone inserted
            </span><span style="background:white;color:blue;">End If
        End If</span></pre>

Got it? Well, I admit I trust Stephen that this is what I should do …

I can then create my little HTML Cache by using the above class as in:

<pre class="code"><span style="background:white;">Public Class </span><span style="background:white;color:#2b91af;">HtmlCache
</span><span style="background:white;">
    Public Sub </span><span style="background:white;color:black;">GetHtmlAsync(</span><span style="background:white;">ByVal </span><span style="background:white;color:black;">url </span><span style="background:white;">As String</span><span style="background:white;color:black;">, </span><span style="background:white;">ByVal </span><span style="background:white;color:black;">callback </span><span style="background:white;">As </span><span style="background:white;color:#2b91af;">Action</span><span style="background:white;color:black;">(</span><span style="background:white;">Of String</span><span style="background:white;color:black;">))
        _asyncCache.GetValueAsync(url, callback)
    </span><span style="background:white;">End Sub
    Private Function </span><span style="background:white;color:black;">LoadWebPage(</span><span style="background:white;">ByVal </span><span style="background:white;color:black;">url </span><span style="background:white;">As String</span><span style="background:white;color:black;">) </span><span style="background:white;">As String
        Using </span><span style="background:white;color:black;">client </span><span style="background:white;">As New </span><span style="background:white;color:#2b91af;">WebClient</span><span style="background:white;color:black;">()
            </span><span style="background:white;color:green;">'Test.PrintThread("Downloading on thread {0} ...")
            </span><span style="background:white;">Return </span><span style="background:white;color:black;">client.DownloadString(url)
        </span><span style="background:white;">End Using
    End Function
    Private </span><span style="background:white;color:black;">_asyncCache </span><span style="background:white;">As New </span><span style="background:white;color:#2b91af;">AsyncCache</span><span style="background:white;color:black;">(</span><span style="background:white;">Of String</span><span style="background:white;color:black;">, </span><span style="background:white;">String</span><span style="background:white;color:black;">)(</span><span style="background:white;">AddressOf </span><span style="background:white;color:black;">LoadWebPage)
</span><span style="background:white;">End Class</span></pre>

I have no idea why coloring got disabled when I copy/paste. It doesn’t matter, this is trivial. I just create an _AsyncCache_ and initialize it with a method that knows how to load a web page. I then simply implement _GetHtmlAsync_ by delegating to the underlying _GetValueAsync_ on _AsyncCache_.

It is somehow bizarre to call _Webclient.DownloadString_, when the design could be revised to take advantage of its asynchronous version. Maybe I’ll do it in another post. Next time, I’ll write code to use this thing.