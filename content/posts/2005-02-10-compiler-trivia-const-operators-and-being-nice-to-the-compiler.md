---
id: 893
title: 'Compiler trivia: const, operators and being nice to the compiler'
date: 2005-02-10T10:32:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2005/02/10/compiler-trivia-const-operators-and-being-nice-to-the-compiler/
permalink: /2005/02/10/compiler-trivia-const-operators-and-being-nice-to-the-compiler/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2005/02/10/370556.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "370556"
orig_parent_id:
  - "370556"
orig_thread_id:
  - "370556"
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
  - http://blogs.msdn.com/b/lucabol/archive/2005/02/10/compiler-trivia-const-operators-and-being-nice-to-the-compiler.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Compiler trivia: const, operators and being nice to the compiler" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2005/02/10/compiler-trivia-const-operators-and-being-nice-to-the-compiler/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="This is a question that came up on our internal alias. I thought it might be generally interesting to illustrate how the compiler picks operators. Here is the original issue. This code compiles fine: UInt64 vUInt641 = UInt64.MaxValue;const int&nbsp; vInt2 = 1432765098;int res = (int)(vUInt641  - vInt2); But this code generates a compile error: UInt64..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Compiler trivia: const, operators and being nice to the compiler" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2005/02/10/compiler-trivia-const-operators-and-being-nice-to-the-compiler/" />
    <meta name="twitter:description" content="This is a question that came up on our internal alias. I thought it might be generally interesting to illustrate how the compiler picks operators. Here is the original issue. This code compiles fine: UInt64 vUInt641 = UInt64.MaxValue;const int&nbsp; vInt2 = 1432765098;int res = (int)(vUInt641  - vInt2); But this code generates a compile error: UInt64..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - 'C# Programming'
---
This is a question that came up on our internal alias. I thought it might be generally interesting to illustrate how the compiler picks operators.

Here is the original issue. This code compiles fine:

UInt64 vUInt641 = UInt64.MaxValue;  
**const** int&nbsp; vInt2 = 1432765098;  
int res = (int)(vUInt641  - vInt2);

But this code generates a compile error:

UInt64 vUInt641 = UInt64.MaxValue;  
int&nbsp; vInt2 = 1432765098;  
int res = (int)(vUInt641  - vInt2);

(line 3): error CS0019: Operator &#8216;-&#8216; cannot be applied to operands of type &#8216;ulong' and &#8216;int'

&nbsp;The only difference between the two pieces of code is the presence of the **const** keyword in the first one. Let's first analyze the second case. The reason an error is generated is that there is no &#8216;-&#8216; operator&nbsp;defined between an ulong and an int. There is also no implicit conversion between int and and ulong or the other way around. The compiler has to give up and to produce an error.

In the first case the variable is marked as const, which&nbsp;means that the compiler knows its value at compile time. It realizes that the value is positive and can safely been converted to an ulong.&nbsp;The compiler&nbsp;converts it and then invokes the -(ulong, ulong) operator.

A bizarre way to think of it is this.&nbsp;As you have been nice to the compiler by telling him that you are not going to modify this value, the compiler then is nice to you by making use of the info to help you out in this case

Remember, always be nice to the compiler, the more you tell him, the more he tells you