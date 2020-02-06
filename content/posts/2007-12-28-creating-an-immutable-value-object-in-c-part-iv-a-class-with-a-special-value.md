---
id: 553
title: 'Creating an immutable value object in C# - Part IV - A class with a special value'
date: 2007-12-28T18:45:32+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/12/28/creating-an-immutable-value-object-in-c-part-iv-a-class-with-a-special-value/
permalink: /2007/12/28/creating-an-immutable-value-object-in-c-part-iv-a-class-with-a-special-value/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/12/28/creating-an-immutable-value-object-in-c-part-iv-a-class-with-a-special-value.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "6889957"
orig_parent_id:
  - "6889957"
orig_thread_id:
  - "555073"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/12/28/creating-an-immutable-value-object-in-c-part-iv-a-class-with-a-special-value.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Creating an immutable value object in C#  - Part IV  - A class with a special value" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/12/28/creating-an-immutable-value-object-in-c-part-iv-a-class-with-a-special-value/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Other posts: Part I  - Using a class Part II  - Making the class better Part III  - Using a struct In the last post we looked at structs as ways to implement immutable value objects and we discovered that they have several issues. A good thing about the struct implementation was the introduction of..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Creating an immutable value object in C#  - Part IV  - A class with a special value" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/12/28/creating-an-immutable-value-object-in-c-part-iv-a-class-with-a-special-value/" />
    <meta name="twitter:description" content="Other posts: Part I  - Using a class Part II  - Making the class better Part III  - Using a struct In the last post we looked at structs as ways to implement immutable value objects and we discovered that they have several issues. A good thing about the struct implementation was the introduction of..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - csharp
---
Other posts:

  * [Part I  - Using a class](http://blogs.msdn.com/lucabol/archive/2007/12/03/creating-an-immutable-value-object-in-c-part-i-using-a-class.aspx) 
      * [Part II  - Making the class better](http://blogs.msdn.com/lucabol/archive/2007/12/06/creating-an-immutable-value-object-in-c-part-ii-making-the-class-better.aspx)
      * <a href="http://blogs.msdn.com/lucabol/archive/2007/12/24/creating-an-immutable-value-object-in-c-part-iii-using-a-struct.aspx" target="_blank">Part III  - Using a struct</a>
    In the last post we looked at structs as ways to implement immutable value objects and we discovered that they have several issues. 
    
    A good thing about the struct implementation was the introduction of an explicit &#8216;special value' instead of &#8216;null'. I personally like doing that because it forces me to think about what are the special values in my domain instead of blindly rely on null and its semantics. Plus, it also works where null breaks down, when there are multiple special values.
    
    Having explicit special values is obviously not related to structs in any way. You can use the same pattern with classes as well, but you have to manage &#8216;null' values that can enter your API. Here is how I did it for the DateSpan class.
    
    First I defined an utility function to manage null values:
    
    <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(0,0,255);">void</span> CheckNull&lt;T&gt;(T t) {
        <span style="color:rgb(0,0,255);">if</span> (t == <span style="color:rgb(0,0,255);">null</span>)
            <span style="color:rgb(0,0,255);">throw</span> <span style="color:rgb(0,0,255);">new</span> <span style="color:rgb(43,145,175);">ArgumentNullException</span>();
    }</pre>
    
    Then I had to check my null precondition for each parameter of my API. I.E.
    
    <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(43,145,175);">DateSpan</span> Intersect(<span style="color:rgb(43,145,175);">DateSpan</span> other) {
        Utils.CheckNull(other);
        ...
    }</pre>
    
    Most importantly I now have to check for null in &#8216;Equals' and &#8216;==':
    
    <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">override</span> <span style="color:rgb(0,0,255);">bool</span> Equals(<span style="color:rgb(0,0,255);">object</span> obj) {
        <span style="color:rgb(0,128,0);">// Interesting choice, null is not valid in this domain
</span>        <span style="color:rgb(43,145,175);">Utils</span>.CheckNull(obj);
        <span style="color:rgb(0,0,255);">if</span> (<span style="color:rgb(0,0,255);">this</span>.GetType() != obj.GetType()) <span style="color:rgb(0,0,255);">return</span> <span style="color:rgb(0,0,255);">false</span>;
        <span style="color:rgb(43,145,175);">DateSpan</span> other = obj <span style="color:rgb(0,0,255);">as</span> <span style="color:rgb(43,145,175);">DateSpan</span>;
        <span style="color:rgb(0,0,255);">return</span> other.End == End && other.Start == Start;
    }</pre>
    
    <pre class="code"><span style="color:rgb(0,0,255);">public</span> <span style="color:rgb(0,0,255);">static</span> <span style="color:rgb(43,145,175);">Boolean</span> <span style="color:rgb(0,0,255);">operator</span> ==(<span style="color:rgb(43,145,175);">DateSpan</span> v1, <span style="color:rgb(43,145,175);">DateSpan</span> v2) {
        <span style="color:rgb(43,145,175);">Utils</span>.CheckNull(v1);
        <span style="color:rgb(43,145,175);">Utils</span>.CheckNull(v2);
        <span style="color:rgb(0,0,255);">return</span> (v1.Equals(v2));
    }</pre>
    
    So now we have an immutable value object, represented as a class, with checks for nulls and a special value (not shown above because it is essentially the same as for structs). So, does this work?
    
    It does, but it is cumbersome to write. And if it is too cumbersome, I already know that I'm not going to use it. I might start doing it, but I would soon give up. Are there ways to ease the pain?
    
    One way would be to use snippets to help in writing the code. Snippets in this case have a couple of problems:
    
      * It is not easy to &#8216;snippify' the logic inside &#8216;Equals', &#8216;GetHashcode' and such
      * It makes easy to write the code, but still it is hard to read it and maintain it
    
    In the next post we'll look at a better solution.