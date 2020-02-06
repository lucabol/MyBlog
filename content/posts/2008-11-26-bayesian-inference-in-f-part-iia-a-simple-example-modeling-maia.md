---
id: 333
title: 'Bayesian inference in F# - Part IIa - A simple example - modeling Maia'
date: 2008-11-26T15:41:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/11/26/bayesian-inference-in-f-part-iia-a-simple-example-modeling-maia/
permalink: /2008/11/26/bayesian-inference-in-f-part-iia-a-simple-example-modeling-maia/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/11/26/bayesian-inference-in-f-part-iia-a-simple-example-modeling-maia.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9130414"
orig_parent_id:
  - "9130414"
orig_thread_id:
  - "620146"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/11/26/bayesian-inference-in-f-part-iia-a-simple-example-modeling-maia.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Bayesian inference in F#  - Part IIa  - A simple example  - modeling Maia" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/11/26/bayesian-inference-in-f-part-iia-a-simple-example-modeling-maia/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other parts: Part I  - Background Part IIb  - Finding Maia underlying attitude&nbsp; Let's start with a simple example: inferring the underlying attitude of a small baby by observing her actions. Let's call this particular small baby Maia. People always asks her father if she is a &#8216;good' baby or not. Her father started to..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Bayesian inference in F#  - Part IIa  - A simple example  - modeling Maia" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/11/26/bayesian-inference-in-f-part-iia-a-simple-example-modeling-maia/" />
    <meta name="twitter:description" content="Other parts: Part I  - Background Part IIb  - Finding Maia underlying attitude&nbsp; Let's start with a simple example: inferring the underlying attitude of a small baby by observing her actions. Let's call this particular small baby Maia. People always asks her father if she is a &#8216;good' baby or not. Her father started to..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - fsharp
  - Statistics
---
Other parts:

  * [Part I  - Background](http://blogs.msdn.com/lucabol/archive/2008/11/07/bayesian-inference-in-f-part-i-background.aspx)
  * [Part IIb  - Finding Maia underlying attitude](http://blogs.msdn.com/lucabol/archive/2009/01/19/bayesian-inference-in-f-part-iib-finding-maia-underlying-attitude.aspx)&nbsp;

Let's start with a simple example: inferring the underlying attitude of a small baby by observing her actions. Let's call this particular small baby Maia. People always asks her father if she is a &#8216;good' baby or not. Her father started to wonder how he can possibly know that. Being &#8216;good' is not very clear, so he chooses to answer the related question if her attitude is generally happy, unhappy or simply quiet (a kind of middle ground).

<pre class="code"><span style="color:green;">/// Underlying unobservable, but assumed stationary, state of the process (baby). Theta.
</span><span style="color:blue;">type </span>Attitude =
    | Happy
    | UnHappy
    | Quiet</pre>

Her poor father doesn't have much to go with. He can just observe what she does. He decides, for the sake of simplifying things, to categorize her state at each particular moment as smiling, crying or looking silly (a kind of middle ground).

<pre class="code"><span style="color:green;">/// Observable data. y.
</span><span style="color:blue;">type </span>Action =
    | Smile
    | Cry
    | LookSilly</pre>

&nbsp;

The father now has to decide what does it mean for Maia to be of an happy attitude. Lacking an universal definition of happiness in terms of these actions, he makes one up. Maia would be considered happy if she smiles 60% of the times, she cries 20% of the times and looks silly the remaining 20% of the times. He might as well have experimented with clearly happy/unhappy babies to come up with those numbers.

<pre class="code"><span style="color:green;">/// Data to model the underlying process (baby)
</span><span style="color:blue;">let </span>happyActions = [ Smile, 0.6; Cry, 0.2; LookSilly, 0.2]
<span style="color:blue;">let </span>unHappyActions = [Smile, 0.2; Cry, 0.6; LookSilly, 0.2]
<span style="color:blue;">let </span>quietActions = [Smile, 0.4; Cry, 0.3; LookSilly, 0.3]</pre>

What does it mean exactly? Well, this father would call his wife at random times during the day and ask her if Maia is smiling, crying or looking silly. He would then keep track of the numbers and then somehow decide what her attitude is. The general idea is simple, the somehow part is not.

<pre class="code"><span style="color:green;">/// Generates a new uniformly distributed number between 0 and 1
</span><span style="color:blue;">let </span>random =
    <span style="color:blue;">let </span>rnd = <span style="color:blue;">new </span>System.Random()
    rnd.NextDouble</pre>

We can now model Maia. We want our model to return a particular action depending on which attitude we assume Maia is in mostly. For example, if we assume she is an happy baby, we want our model to return Smile about 60% of the times. In essence, we want to model what happens when the (poor) father calls his (even poorer) wife. What would his wife tell him (assuming a particular attitude)? The general idea is expressed by the following:

<pre class="code"><span style="color:green;">/// Process (baby) modeling. How she acts if she is fundamentally happy, unhappy or quiet
</span><span style="color:blue;">let </span>MaiaSampleDistribution attitude =
    <span style="color:blue;">match </span>attitude <span style="color:blue;">with
    </span>| Happy     <span style="color:blue;">-&gt; </span>pickOne happyActions
    | UnHappy   <span style="color:blue;">-&gt; </span>pickOne unHappyActions
    | Quiet     <span style="color:blue;">-&gt; </span>pickOne quietActions</pre>

The &#8216;pickOne' function simply picks an action depending on the probability of it being picked. The name sample distribution is statistic-lingo to mean &#8216;what you observe' and indeed you just can observe Maia's actions, not her underlying attitude.

The implementation of pickOne gets technical. You don't need to understand it to understand the rest of this post. This is the beauty of encapsulation. You can start reading from after the next code snippet if you want to.

&#8216;pickOne' works by constructing the inverse cumulative distribution function for the probability distribution described by the Happy/UnHappy/Quiet/Actions lists. There is an [entry on wikipedia](http://en.wikipedia.org/wiki/Inverse_transform_sampling) that describes how this works and I don't wish to say more here except presenting the code.

<pre class="code"><span style="color:green;">/// Find the first value more or equal to a key in a seq&lt;'a * 'b&gt;.<br />/// The seq is assumed to be sorted
</span><span style="color:blue;">let </span>findByKey key aSeq =
    aSeq |&gt; Seq.find (<span style="color:blue;">fun </span>(k, _) <span style="color:blue;">-&gt; </span>k &gt;= key) |&gt; snd
<span style="color:green;">/// Simulate an inverse CDF given values and probabilities
</span><span style="color:blue;">let </span>buildInvCdf valueProbs =
    <span style="color:blue;">let </span>cdfValues =
        valueProbs
        |&gt; Seq.scan (<span style="color:blue;">fun </span>cd (_, p) <span style="color:blue;">-&gt; </span>cd + p) 0.
        |&gt; Seq.skip 1
    <span style="color:blue;">let </span>cdf =
        valueProbs
        |&gt; Seq.map fst
        |&gt; Seq.zip cdfValues
        |&gt; Seq.cache
    <span style="color:blue;">fun </span>x <span style="color:blue;">-&gt; </span>cdf |&gt; findByKey x
<span style="color:green;">/// Picks an 'a in a seq&lt;'a * float&gt; using float as the probability to pick a particular 'a
</span><span style="color:blue;">let </span>pickOne probs =
    <span style="color:blue;">let </span>rnd = random ()
    <span style="color:blue;">let </span>picker = buildInvCdf probs
    picker rnd</pre>

Another way to describe Maia is more mathematically convenient and will be used in the rest of the post. This second model answers the question: what is the probability of observing an action assuming a particular attitude? The distribution of both actions and attitudes (observable variable and parameter) is called joint probability.

<pre class="code"><span style="color:green;">/// Another, mathematically more convenient, way to model the process (baby)
</span><span style="color:blue;">let </span>MaiaJointProb attitude action =
    <span style="color:blue;">match </span>attitude <span style="color:blue;">with
    </span>| Happy     <span style="color:blue;">-&gt; </span>happyActions |&gt; List.assoc action
    | UnHappy   <span style="color:blue;">-&gt; </span>unHappyActions |&gt; List.assoc action
    | Quiet     <span style="color:blue;">-&gt; </span>quietActions |&gt; List.assoc action</pre>

List.assoc returns the value associated with a key in a list containing (key, value) pairs. Notice that in general, if you are observing a process, you don't know what its joint distribution is. But you can approximate it by running the MaiaSampleDistribution function on known babies many times and keeping track of the result. So, in theory, if you have a way to experiment with many babies with known attitudes, you can create such a joint distribution.

We now have modeled our problem, this is the creative part. From now on, it is just execution. We'll get to that.