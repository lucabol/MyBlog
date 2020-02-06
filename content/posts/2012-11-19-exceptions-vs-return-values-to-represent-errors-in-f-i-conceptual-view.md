---
id: 102
title: 'Exceptions vs. Return Values to represent errors (in F#) – Conceptual view'
date: 2012-11-19T13:02:10+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=102
permalink: /2012/11/19/exceptions-vs-return-values-to-represent-errors-in-f-i-conceptual-view/
categories:
  - fsharp
tags:
  - fsharp
---
Recently I’ve been reading numerous articles on the age old question of exceptions vs. return values. There is a vast literature on the topic with very passionate opinions on one side or the other. Below is my view on it.

First of all, I’ll define my terms.

  * Success code path: chunk of code that is responsible to perform the main task of a function, without any regard for error conditions 
  * Contingency: an event that happens during the success code path execution that is of interest for the caller of the function. 
      * It happens rarely 
      * It can be described in terms that the caller understands, it doesn’t refer to the implementation of the function 
      * The caller stands a chance to recover from it 
  * Fault: an event that happens during the success code path execution that is not expected by the caller of the function. 
      * It happens rarely 
      * It cannot be described in terms that the caller understands, it requires reference to the implementation of the function 
      * The caller has no way to recover from it 

Examples of the above for a FetchUser(userName) function:

  * Success code path: the code that retrieves the user from the database 
  * Contingency: the fact that the requested user is not in the database 
  * Fault: userName = null, divide by zero, stack overflow, … 

The difference between Contingency and Fault is not sharp in practice and requires common sense, but it is useful none less. When in doubt, it would appear prudent to consider an event as a Contingency, so that the caller gets a chance to recover.

Ideally, you would like a Contingency to be part of the signature of a function, so that the caller knows about it. On the other end, a Fault shouldn’t be part of the signature of a function for two reasons:

  * The user cannot recover from it 
  * Being part of the signature would break encapsulation by exposing implementation details of the function 

The above seems to suggest that Contingencies should be represented as return values and Faults as exceptions. As an aside, in Java the former is represented as checked exceptions, which is part of the signature. We’ll tackle checked exceptions later on.

An important point that is often neglected in the discussions on this topic is that there are two categories of applications: applications that care about Contingencies (Critical apps) and applications that don’t (Normal apps). I am of the opinion that the latter category is the largest.

In many cases you can indeed write just the success code path and, if anything goes wrong, you just clean up after yourself and exit. That is a perfectly reasonable thing to do for very many applications. You are trading off speed of development with stability.&#160; Your application can be anywhere on that continuum.

Examples of Normal apps are: build scripts, utility applications, departmental applications where you can fix things quickly on the user machine, intranet web sites, internet web sites that are purely informative, etc …

Examples of Critical apps are: servers, databases, operating systems, web site that sell stuff,&#160; etc …

For Normal apps, treating Contingencies as Fault is the right thing to do. You just slap a try … catch around your event loop/ thread/ process and you do your best to get the developer to fix the problem quickly. I think a lot of the angst of the ‘return value crowd’ is predicated on not having this distinction in mind. They are making very valid point regarding Critical apps to a crowd that is thinking about Normal apps. So the two sides are cross-talking.

Also, in my opinion, the main problem with Java checked exceptions is that they make writing Normal apps as cumbersome as writing Critical apps. So, reasonably, people complain. 

The .NET framework decided to use Exceptions as the main way to convey both Faults and Contingencies. By doing so, it makes it easier to write Normal apps, but more difficult to write Critical apps.

For a Critical app or section of code, you’d want to:

  * Express contingencies in the function signature 
  * Force/Encourage people to take an explicit decision at the calling site on how they want to manage both Contingencies and Faults <u>for each function call</u> 

In the next post, let’s see how we can represent some of this in F#.