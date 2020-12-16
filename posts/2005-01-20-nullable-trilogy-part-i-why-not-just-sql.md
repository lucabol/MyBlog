---
id: 933
title: 'Nullable trilogy Part I: why not just SQL?'
date: 2005-01-20T09:41:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2005/01/20/nullable-trilogy-part-i-why-not-just-sql/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2005/01/20/357353.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "357353"
orig_parent_id:
  - "357353"
orig_thread_id:
  - "357353"
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
  - http://blogs.msdn.com/b/lucabol/archive/2005/01/20/nullable-trilogy-part-i-why-not-just-sql.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Nullable&lt;T&gt; trilogy Part I: why not just SQL?" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2005/01/20/nullable-trilogy-part-i-why-not-just-sql/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="This is the first of a weekly three part serie of posts about Nullable&lt;T&gt;. In these posts I want to describe the reasons behind three design choices:1. Why not just use SQL semantics for null?2. Why null == null doesn't imply null &gt;= null and null &lt;= null?3. Why inside a generic class with a..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Nullable&lt;T&gt; trilogy Part I: why not just SQL?" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2005/01/20/nullable-trilogy-part-i-why-not-just-sql/" />
    <meta name="twitter:description" content="This is the first of a weekly three part serie of posts about Nullable&lt;T&gt;. In these posts I want to describe the reasons behind three design choices:1. Why not just use SQL semantics for null?2. Why null == null doesn't imply null &gt;= null and null &lt;= null?3. Why inside a generic class with a..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - csharp
---
This is the first of a weekly three part serie of posts about Nullable<T>. In these posts I want to describe the reasons behind three design choices:  
1. Why not just use SQL semantics for null?  
2. Why null == null doesn't imply null >= null and null <= null?  
3. Why inside a generic class with a type parameter t the expression t == null will return false, when t is a nullable type and the value of it is null.

Let's start from the first question as the answer is shorter. We'll get to the other two in the coming weeks.

The first question relates to the reason not to have the same semantics as SQL for relational operators. The SQL semantics have been commonly referred to as three-value logic where null == null returns null. Introducing such logic in the C# language would be problematic. The main reason is that the language already contains the concept of null for reference types and it does have the programming languages traditional two-value logic where null == null returns true.

Granted that we cannot change this definition, then the addition of three-value logic just for some types would be confusing. We would need, for example, to create a new NullableString class to be able to apply three-value logic operators to it. More generally, the presence in the same code of two value logic and three value logic operators would make the code quite difficult to write, read and maintain.

&nbsp;