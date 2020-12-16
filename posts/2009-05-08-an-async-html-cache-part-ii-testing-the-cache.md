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
    <meta property="og:description" content="Other posts: Part I – Writing the cache Let’s try out our little cache. First I want to write a synchronous version of it as a baseline. Private Shared Sub TestSync(ByVal sites() As String, ByVal sitesToDownload As Integer, ByVal howLong As Integer) Dim syncCache As New Dictionary(Of String, String) Dim count = sites.Count() Dim url1..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="An Async Html cache &ndash; part II &ndash; Testing the cache" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2009/05/08/an-async-html-cache-part-ii-testing-the-cache/" />
    <meta name="twitter:description" content="Other posts: Part I – Writing the cache Let’s try out our little cache. First I want to write a synchronous version of it as a baseline. Private Shared Sub TestSync(ByVal sites() As String, ByVal sitesToDownload As Integer, ByVal howLong As Integer) Dim syncCache As New Dictionary(Of String, String) Dim count = sites.Count() Dim url1..." />
    
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

Let’s try out our little cache. First I want to write a synchronous version of it as a baseline.

<pre class="code"><span style="background:white;">    </span><span style="background:white;color:blue;">Private Shared Sub </span><span style="background:white;">TestSync(</span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">sites() </span><span style="background:white;color:blue;">As String</span><span style="background:white;">, </span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">sitesToDownload </span><span style="background:white;color:blue;">As Integer</span><span style="background:white;">, </span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">howLong </span><span style="background:white;color:blue;">As Integer</span><span style="background:white;">)
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">syncCache </span><span style="background:white;color:blue;">As New </span><span style="background:white;color:#2b91af;">Dictionary</span><span style="background:white;">(</span><span style="background:white;color:blue;">Of String</span><span style="background:white;">, </span><span style="background:white;color:blue;">String</span><span style="background:white;">)
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">count = sites.Count()
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">url1 = </span><span style="background:white;color:#a31515;">"http://moneycentral.msn.com/investor/invsub/results/statemnt.aspx?Symbol="
        </span><span style="background:white;color:blue;">For </span><span style="background:white;">i = 0 </span><span style="background:white;color:blue;">To </span><span style="background:white;">sitesToDownload - 1
            </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">html </span><span style="background:white;color:blue;">As String </span><span style="background:white;">= </span><span style="background:white;color:#a31515;">""
            </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">url = url1 & sites(i </span><span style="background:white;color:blue;">Mod </span><span style="background:white;">count)
            </span><span style="background:white;color:blue;">If Not </span><span style="background:white;"><strong>syncCache.TryGetValue(url, html)</strong> </span><span style="background:white;color:blue;">Then
                </span><span style="background:white;">html = LoadWebPage(url)
                <strong>syncCache(url) = html</strong>
            </span><span style="background:white;color:blue;">End If
            </span><span style="background:white;">DoWork(html, howLong)
        </span><span style="background:white;color:blue;">Next
    End Sub</span></pre>

This is a loop that loads webpages in the cache if they are not already there. _sites_ is a list of tickers used to compose the urls; _sitesToDownload_ is the total number of sites to download, so that a single url can be loaded multiple times; _howLong_ represents the work to be done on each loaded page.

In this version the cache is simply a _Dictionary_ and there is no parallelism. The two bold lines is where the cache is managed.

_DoWork_ is this.

<pre class="code"><span style="background:white;">    </span><span style="background:white;color:blue;">Public Shared Sub </span><span style="background:white;">DoWork(</span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">html </span><span style="background:white;color:blue;">As String</span><span style="background:white;">, </span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">howLong </span><span style="background:white;color:blue;">As Integer</span><span style="background:white;">)
        </span><span style="background:white;color:#2b91af;">Thread</span><span style="background:white;">.Sleep(howLong)
    </span><span style="background:white;color:blue;">End Sub</span></pre>

Let’s take a look at the asynchronous version.

<pre class="code"><span style="background:white;">    </span><span style="background:white;color:blue;">Private Shared Sub </span><span style="background:white;">TestAsync(</span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">sites() </span><span style="background:white;color:blue;">As String</span><span style="background:white;">, </span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">sitesToDownload </span><span style="background:white;color:blue;">As Integer</span><span style="background:white;">, </span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">howLong </span><span style="background:white;color:blue;">As Integer</span><span style="background:white;">)
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">htmlCache </span><span style="background:white;color:blue;">As New </span><span style="background:white;color:#2b91af;">HtmlCache
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">count = sites.Count()
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">url = </span><span style="background:white;color:#a31515;">"http://moneycentral.msn.com/investor/invsub/results/statemnt.aspx?Symbol="
        </span><span style="background:white;color:blue;">Using </span><span style="background:white;">ce = </span><span style="background:white;color:blue;">New </span><span style="background:white;color:#2b91af;">CountdownEvent</span><span style="background:white;">(sitesToDownload)
            </span><span style="background:white;color:blue;">For </span><span style="background:white;">i = 1 </span><span style="background:white;color:blue;">To </span><span style="background:white;">sitesToDownload
                </span><span style="background:white;color:#2b91af;">htmlCache</span><span style="background:white;">.GetHtmlAsync(
                    url & sites(i </span><span style="background:white;color:blue;">Mod </span><span style="background:white;">count),
                    </span><span style="background:white;color:blue;">Sub</span><span style="background:white;">(s)
                        DoWork(s, howLong)
                        ce.Signal()
                    </span><span style="background:white;color:blue;">End Sub</span><span style="background:white;">)
            </span><span style="background:white;color:blue;">Next
            </span><span style="background:white;">ce.Wait()
        </span><span style="background:white;color:blue;">End Using</span></pre>

There are several points worth making on this:

  * The lambda used as second parameter for _GetHtmlAsync_ is invoked on a different thread whenever the html has been retrieved (which could be immediately if the cache has downloaded the url before) 
  * _CountDownEvent_ allows a thread to wait for a certain number of signals to be sent. The waiting happens on the main thread in the _ce.Wait()_ instruction. The triggering of the event happens in the lambda described in the point above (the _ce.Signal()_ instruction) 

This is the driver for the overall testing.

<pre class="code"><span style="background:white;">    </span><span style="background:white;color:blue;">Private Shared Sub </span><span style="background:white;">TestPerf(</span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">s </span><span style="background:white;color:blue;">As String</span><span style="background:white;">, </span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">a </span><span style="background:white;color:blue;">As </span><span style="background:white;color:#2b91af;">Action</span><span style="background:white;">, </span><span style="background:white;color:blue;">ByVal </span><span style="background:white;">iterations </span><span style="background:white;color:blue;">As Integer</span><span style="background:white;">)
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">clock </span><span style="background:white;color:blue;">As New </span><span style="background:white;color:#2b91af;">Stopwatch
        </span><span style="background:white;">clock.Start()
        </span><span style="background:white;color:blue;">For </span><span style="background:white;">i = 1 </span><span style="background:white;color:blue;">To </span><span style="background:white;">iterations
            a()
        </span><span style="background:white;color:blue;">Next
        </span><span style="background:white;">clock.Stop()
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">ts = clock.Elapsed
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">elapsedTime = </span><span style="background:white;color:blue;">String</span><span style="background:white;">.Format(s & </span><span style="background:white;color:#a31515;">": {0:00}:{1:00}:{2:00}.{3:00}"</span><span style="background:white;">, ts.Hours, ts.Minutes, ts.Seconds, ts.Milliseconds / 10)
        </span><span style="background:white;color:#2b91af;">Console</span><span style="background:white;">.WriteLine(elapsedTime, </span><span style="background:white;color:#a31515;">"RunTime"</span><span style="background:white;">)
    </span><span style="background:white;color:blue;">End Sub</span></pre>



There is not much to say about it. Start the clock, perform a bunch of iterations of the passed lambda, stop the clock, print out performance.

And finally the main method. Note that all the adjustable parameters are factored out before the calls to _TestPerf_.

<pre class="code"><span style="background:white;">    </span><span style="background:white;color:blue;">Public Shared Sub </span><span style="background:white;">Main()
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">tickers = </span><span style="background:white;color:blue;">New String</span><span style="background:white;">() {</span><span style="background:white;color:#a31515;">"mmm"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"aos"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"shlm"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"cas"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"abt"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"anf"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"abm"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"akr"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"acet"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"afl"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"agl"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"adc"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"apd"</span><span style="background:white;">,<br />                                           </span><span style="background:white;color:#a31515;">"ayr"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"alsk"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"ain"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"axb"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"are"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"ale"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"ab"</span><span style="background:white;">, </span><span style="background:white;color:#a31515;">"all"</span><span style="background:white;">}
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">sitesToDownload = 50
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">workToDoOnEachUrlInMilliSec = 20
        </span><span style="background:white;color:blue;">Dim </span><span style="background:white;">perfIterations = 5
        TestPerf(</span><span style="background:white;color:#a31515;">"Async"</span><span style="background:white;">, </span><span style="background:white;color:blue;">Sub</span><span style="background:white;">() TestAsync(tickers, sitesToDownload, workToDoOnEachUrlInMilliSec), perfIterations)
        TestPerf(</span><span style="background:white;color:#a31515;">"Sync"</span><span style="background:white;">, </span><span style="background:white;color:blue;">Sub</span><span style="background:white;">() TestSync(tickers, sitesToDownload, workToDoOnEachUrlInMilliSec), perfIterations)
    </span><span style="background:white;color:blue;">End Sub</span></pre>

Feel free to change (_tickers_, _sitesToDownload_, _workToDoOnEachUrlInMilliSec_, _perfIterations_). Depending on the ratios between these parameters and the number of cores on your machine, you’re going to see different results. Which highlights the fact that parallelizing your algorithms can yield performance gains or not depending on both software and hardware considerations. I get ~3X improvement on my box. I attached the full source file for your amusement. 

[AsyncCache.vb](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/09/58/90/57/AsyncCache.vb)