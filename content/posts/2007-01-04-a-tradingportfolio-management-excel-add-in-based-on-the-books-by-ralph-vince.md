---
id: 843
title: A trading/portfolio management Excel Add-in based on the books by Ralph Vince
date: 2007-01-04T17:53:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/01/04/a-tradingportfolio-management-excel-add-in-based-on-the-books-by-ralph-vince/
permalink: /2007/01/04/a-tradingportfolio-management-excel-add-in-based-on-the-books-by-ralph-vince/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/01/04/a-trading-portfolio-management-excel-add-in-based-on-the-books-by-ralph-vince.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "1412946"
orig_parent_id:
  - "1412946"
orig_thread_id:
  - "488376"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/01/04/a-tradingportfolio-management-excel-add-in-based-on-the-books-by-ralph-vince.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="A trading/portfolio management Excel Add-in based on the books by Ralph Vince" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/01/04/a-tradingportfolio-management-excel-add-in-based-on-the-books-by-ralph-vince/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="I like to write code and I still manage to do it even now that it is not my primary job. I never post the things that I write because I don't want to maintain them.&nbsp;Lately Charlie&nbsp;convinced me that I don't have to do that. I can just throw the code out, without much preparation..." />
    <meta property="og:image" content="https://www.dotnetkicks.com/Services/Images/KickItImageGenerator.ashx?url=http://blogs.msdn.com/lucabol/archive/2007/01/04/a-trading-portfolio-management-excel-add-in-based-on-the-books-by-ralph-vince.aspx" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="A trading/portfolio management Excel Add-in based on the books by Ralph Vince" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/01/04/a-tradingportfolio-management-excel-add-in-based-on-the-books-by-ralph-vince/" />
    <meta name="twitter:description" content="I like to write code and I still manage to do it even now that it is not my primary job. I never post the things that I write because I don't want to maintain them.&nbsp;Lately Charlie&nbsp;convinced me that I don't have to do that. I can just throw the code out, without much preparation..." />
    <meta name="twitter:image" content="https://www.dotnetkicks.com/Services/Images/KickItImageGenerator.ashx?url=http://blogs.msdn.com/lucabol/archive/2007/01/04/a-trading-portfolio-management-excel-add-in-based-on-the-books-by-ralph-vince.aspx" />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - csharp
  - Financial
---
I like to write code and I still manage to do it even now that it is not my primary job. I never post the things that I write because I don't want to maintain them.&nbsp;Lately <a class="" href="http://blogs.msdn.com/charlie/" target="_blank">Charlie</a>&nbsp;convinced me that I don't have to do that. I can just throw the code out, without much preparation or implicit contract of perpetual maintenance.

This one is an Excel add-in that adds functions to Excel to analyze your trading and manage your portfolio. Notice that I'm not a professional trader or statistician, so the whole thing could be wrong, buggy or conceptually absurd. Probably it is all of the above.

I used the extremely good&nbsp;<a class="" href="http://exceldna.typepad.com/" target="_blank">ExcelDna</a> to write the add-in. You need to download it and follow the instructions in _HowToInstall.txt_ on the attached zip file to use it. I based the formulas mainly on the work of <a class="" href="http://www.amazon.com/s/103-4348138-5739032?ie=UTF8&index=books&rank=-relevance%2C%2Bavailability%2C-daterank&field-author-exact=Vince%2C%20Ralph" target="_blank">Ralph Vince</a>. Please buy and read his books on money management as they are wonderful.

On the statistics side: I made up the Downside correlation coefficient, I have no idea if it is statistically sound.  
On the technical side:

  1. I haven't optimized the algos at all. I.E. I'm sure there is a way to calculate the standard deviation without navigating the array twice, but I didn't bother to look. They end up being fast enough anyhow (apart from the Monte Carlo related functions that I should investigate).
  2. I haven't organized the code correctly. It needs to be rewritten now that I partially know what I'm doing.
  3. I haven't used LINQ. It will be a lot of fun for me to rewrite the code to be more OO and to use LINQ in the process.

I plan to implement OptimalF for a normal distribution and Efficient Frontier calculations in the future. I have no idea when.

I also have some other projects that might be interesting to share (I.E. a blackjack simulator that you can use to try the result of different strategies inspired by <a class="" href="http://www.amazon.com/Blackjack-Attack-Playing-Pros-Way/dp/0910575207/sr=8-1/qid=1167952522/ref=pd_bbs_sr_1/103-4348138-5739032?ie=UTF8&s=books" target="_blank">Blackjack Attack</a>).

This is the list of Excel functions that you get with this add-in. They ends up in a Trading category in the list of functions on the Insert Function Excel dialog:

<p class="MsoNormal" style="margin-left:.5in;">
  <font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">AnnualizeRet(double, double)<br /></span></font><font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">AnnualizeStdevp(double, double)<br /></span></font><font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">AnnualStdevpParam(double, double)<br /></span></font><font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">ArithMean(object[,], double, double, object, double, double)<br /></span></font><font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">AutoCorrel(object[,])<br /></span></font><font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">AvgLoss(object[,], double, double, object, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">AvgWin(object[,], double, double, object, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">Chebyshev(double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">Correlat(object[,], object[,])<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">Describe(object)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">DownCorrelat(object[,], object[,], double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">DownStdevp(object[,], double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">EGM(double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">EGM2(double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">GM(object[,], double, double, object, double, double)<br /></span></font><font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">Kelly(double, double) TradingLibrary.Losses(object[,])<br /></span></font><font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">MaxDD(object[,])<br /></span></font><font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">MaxDDFromEq(object[,])<br /></span></font><font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">MaxLoss(object[,])<br /></span></font><font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">MaxNegRun(object[,])<br /></span></font><font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">MaxWin(object[,])<br /></span></font><font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">MCMaxDD(object[,], double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">MCOptimalF(object[,], double, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">OptimalF(object[,], double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">OptimalFArray(object[,], double, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">OptimalPos(double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">PortAnnualGM(double, double, double, double, double, double, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">PortAnnualTaxGM(double, double, double, double, double, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">PortAnnualTaxGMGivenTrades(object[,], double, double, double, double, double, object, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">PortStdevp(double, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">PRR(object[,], double, double, object, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">PRRParam(double, double, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">RealReturn(double, double, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">RunTest(object[,])<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">SharpeRatio(double, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">SortinoRatio(double, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">Stdevp2(object[,], double, double, object, double, double)<br /></span></font><font face="Tahoma" size="2"><span lang="FR" style="font-size:10pt;font-family:Tahoma;">TWR(object[,], double, double, object, double, double)<br /></span></font><font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;">Wins(object[,])</span></font>
</p>

<p class="MsoNormal" style="margin-left:.5in;">
  <font face="Tahoma" size="2"><span style="font-size:10pt;font-family:Tahoma;"></span></font>&nbsp;
</p>

[<img alt="kick it on DotNetKicks.com" src="https://www.dotnetkicks.com/Services/Images/KickItImageGenerator.ashx?url=http://blogs.msdn.com/lucabol/archive/2007/01/04/a-trading-portfolio-management-excel-add-in-based-on-the-books-by-ralph-vince.aspx" border="0" />](https://www.dotnetkicks.com/kick/?url=http://blogs.msdn.com/lucabol/archive/2007/01/04/a-trading-portfolio-management-excel-add-in-based-on-the-books-by-ralph-vince.aspx)

[TradingLibrary.zip](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Components.PostAttachments/00/01/41/29/46/TradingLibrary.zip)