---
id: 353
title: 'Bayesian inference in F#  - Part I - Background'
date: 2008-11-07T11:48:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/11/07/bayesian-inference-in-f-part-i-background/
permalink: /2008/11/07/bayesian-inference-in-f-part-i-background/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/11/07/bayesian-inference-in-f-part-i-background.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9052523"
orig_parent_id:
  - "9052523"
orig_thread_id:
  - "617448"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/11/07/bayesian-inference-in-f-part-i-background.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Bayesian inference in F#  - Part I  - Background" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/11/07/bayesian-inference-in-f-part-i-background/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts: Part IIa  - A simple example  - modeling Maia Part IIb  - Finding Maia underlying attitude My interest in Bayesian inference comes from my dissatisfaction with &#8216;classical' statistics. Whenever I want to know something, for example the probability that an unknown parameter is between two values, &#8216;classical' statistics seems to answer a different..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Bayesian inference in F#  - Part I  - Background" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/11/07/bayesian-inference-in-f-part-i-background/" />
    <meta name="twitter:description" content="Other posts: Part IIa  - A simple example  - modeling Maia Part IIb  - Finding Maia underlying attitude My interest in Bayesian inference comes from my dissatisfaction with &#8216;classical' statistics. Whenever I want to know something, for example the probability that an unknown parameter is between two values, &#8216;classical' statistics seems to answer a different..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - fsharp
  - Statistics
---
Other posts:

  * <div>
      <a href="http://blogs.msdn.com/lucabol/archive/2008/11/26/bayesian-inference-in-f-part-iia-a-simple-example-modeling-maia.aspx">Part IIa  - A simple example  - modeling Maia</a>
    </div>

  * <div>
      <a href="http://blogs.msdn.com/lucabol/archive/2009/01/19/bayesian-inference-in-f-part-iib-finding-maia-underlying-attitude.aspx">Part IIb  - Finding Maia underlying attitude</a>
    </div>

My interest in Bayesian inference comes from my dissatisfaction with &#8216;classical' statistics. Whenever I want to know something, for example the probability that an unknown parameter is between two values, &#8216;classical' statistics seems to answer a different and more convoluted question.

Try asking someone what the 95% confidence interval for X is (x1, x2) means. Very likely he will tell you that it means that there is a 95% probability that X lies between x1 and x2. That is not the case in classical statistics. It is the case in Bayesian statistics. Also all the funny business of defining a Null hypothesis for the sake of proving its falseness always made my head spin. You don't need any of that in Bayesian statistics. More recently, my discovery that statistical significance is an harmful concept, instead of the bedrock of knowledge I always thought it to be, shook my confidence in &#8216;classical' statistics even more.

Admittedly, I'm not that smart. If I have an hard time getting an intuitive understanding of something, it tends to go away from my mind after a couple of days I've learned it. This happens all the time with &#8216;classical' statistics. I feel like I have learned the thing ten times, because I continuously forget it. This doesn't happen with Bayesian statistics. It just makes intuitive sense.

At this point you might be wandering what &#8216;classical' statistics is. I use the term classical, but I really shouldn't. Classical statistics is normally just called &#8216;statistics' and it is all you learn if you pick up whatever book on the topic (for example the otherwise excellent [Introduction to the Practice of Statistics](http://www.amazon.com/Introduction-Practice-Statistics-w-CD-ROM/dp/0716764008/ref=sr_1_1?ie=UTF8&s=books&qid=1225747881&sr=1-1)). Bayesian statistics is just a footnote in such books. This is a shame.

Bayesian statistics provides a much clearer and elegant framework for understanding the process of inferring knowledge from data. The underlying question that it answers is: If I hold an opinion about something and I receive additional data on it, how should I rationally change my opinion?. This question of how to update your knowledge is at the very foundation of human learning and progress in general (for example the scientific method is based on it). We better be sure that the way we answer it is sound.

You might wander how it is possible to go against something that is so widely accepted and taught everywhere as &#8216;classical' statistics is. Well, very many things that most people believe are wrong. I always like to cite [old Ben](http://en.wikipedia.org/wiki/Benjamin_Graham) on this: The fact that other people agree or disagree with you makes you neither right nor wrong. You will be right if your facts and your reasoning are correct.. This little rule always served me well.

In this series of posts I will give examples of Bayesian statistics in F#. I am not a statistician, which makes me part of the very dangerous category of &#8216;people who are not statisticians but talk about statistics. To try to mitigate the problem I enlisted the help of [Ralf Herbrich](http://research.microsoft.com/~rherb/), who is a statistician and can catch my most blatant errors. Obviously I'll manage to hide my errors so cleverly that not even Ralf would spot them. In which case the fault is just mine.

In the next post we'll look at some F# code to model the Bayesian inference process.