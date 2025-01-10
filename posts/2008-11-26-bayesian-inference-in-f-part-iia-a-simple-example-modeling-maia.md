---
id: 333
title: 'Bayesian inference in F# - Part IIa - A simple example - modeling Maia'
date: 2008-11-26T15:41:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/11/26/bayesian-inference-in-f-part-iia-a-simple-example-modeling-maia/
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

Let's start with a simple example: inferring the underlying attitude of a small baby by observing her actions. Let's call this particular small baby Maia. People always asks her father if she is a 'good' baby or not. Her father started to wonder how he can possibly know that. Being 'good' is not very clear, so he chooses to answer the related question if her attitude is generally happy, unhappy or simply quiet (a kind of middle ground).

```fsharp
/// Underlying unobservable, but assumed stationary, state of the process (baby). Theta.
type Attitude =
    | Happy
    | UnHappy
    | Quiet
```

Her poor father doesn't have much to go with. He can just observe what she does. He decides, for the sake of simplifying things, to categorize her state at each particular moment as smiling, crying or looking silly (a kind of middle ground).

```fsharp
/// Observable data. y.
type Action =
    | Smile
    | Cry
    | LookSilly
```

The father now has to decide what does it mean for Maia to be of an happy attitude. Lacking an universal definition of happiness in terms of these actions, he makes one up. Maia would be considered happy if she smiles 60% of the times, she cries 20% of the times and looks silly the remaining 20% of the times. He might as well have experimented with clearly happy/unhappy babies to come up with those numbers.

```fsharp
/// Data to model the underlying process (baby)
let happyActions = [ Smile, 0.6; Cry, 0.2; LookSilly, 0.2]
let unHappyActions = [Smile, 0.2; Cry, 0.6; LookSilly, 0.2]
let quietActions = [Smile, 0.4; Cry, 0.3; LookSilly, 0.3]
```

What does it mean exactly? Well, this father would call his wife at random times during the day and ask her if Maia is smiling, crying or looking silly. He would then keep track of the numbers and then somehow decide what her attitude is. The general idea is simple, the somehow part is not.

```fsharp
/// Generates a new uniformly distributed number between 0 and 1
let random =
    let rnd = new System.Random()
    rnd.NextDouble
```

We can now model Maia. We want our model to return a particular action depending on which attitude we assume Maia is in mostly. For example, if we assume she is an happy baby, we want our model to return Smile about 60% of the times. In essence, we want to model what happens when the (poor) father calls his (even poorer) wife. What would his wife tell him (assuming a particular attitude)? The general idea is expressed by the following:

```fsharp
/// Process (baby) modeling. How she acts if she is fundamentally happy, unhappy or quiet
let MaiaSampleDistribution attitude =
    match attitude with
    | Happy     -> pickOne happyActions
    | UnHappy   -> pickOne unHappyActions
    | Quiet     -> pickOne quietActions
```

The 'pickOne' function simply picks an action depending on the probability of it being picked. The name sample distribution is statistic-lingo to mean 'what you observe' and indeed you just can observe Maia's actions, not her underlying attitude.

The implementation of pickOne gets technical. You don't need to understand it to understand the rest of this post. This is the beauty of encapsulation. You can start reading from after the next code snippet if you want to.

'pickOne' works by constructing the inverse cumulative distribution function for the probability distribution described by the Happy/UnHappy/Quiet/Actions lists. There is an [entry on wikipedia](http://en.wikipedia.org/wiki/Inverse_transform_sampling) that describes how this works and I don't wish to say more here except presenting the code.

```fsharp
/// Find the first value more or equal to a key in a seq<'a * 'b>.
/// The seq is assumed to be sorted
let findByKey key aSeq =
    aSeq |> Seq.find (fun (k, _) -> k >= key) |> snd
/// Simulate an inverse CDF given values and probabilities
let buildInvCdf valueProbs =
    let cdfValues =
        valueProbs
        |> Seq.scan (fun cd (_, p) -> cd + p) 0.
        |> Seq.skip 1
    let cdf =
        valueProbs
        |> Seq.map fst
        |> Seq.zip cdfValues
        |> Seq.cache
    fun x -> cdf |> findByKey x
/// Picks an 'a in a seq<'a * float> using float as the probability to pick a particular 'a
let pickOne probs =
    let rnd = random ()
    let picker = buildInvCdf probs
    picker rnd
```

Another way to describe Maia is more mathematically convenient and will be used in the rest of the post. This second model answers the question: what is the probability of observing an action assuming a particular attitude? The distribution of both actions and attitudes (observable variable and parameter) is called joint probability.

```fsharp
/// Another, mathematically more convenient, way to model the process (baby)
let MaiaJointProb attitude action =
    match attitude with
    | Happy     -> happyActions |> List.assoc action
    | UnHappy   -> unHappyActions |> List.assoc action
    | Quiet     -> quietActions |> List.assoc action
```

List.assoc returns the value associated with a key in a list containing (key, value) pairs. Notice that in general, if you are observing a process, you don't know what its joint distribution is. But you can approximate it by running the MaiaSampleDistribution function on known babies many times and keeping track of the result. So, in theory, if you have a way to experiment with many babies with known attitudes, you can create such a joint distribution.

We now have modeled our problem, this is the creative part. From now on, it is just execution. We'll get to that.
