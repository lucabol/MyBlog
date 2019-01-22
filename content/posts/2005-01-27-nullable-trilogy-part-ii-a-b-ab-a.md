---
id: 913
title: 'Nullable trilogy part II: a == b -&gt; a&gt;=b &amp;&amp; a'
date: 2005-01-27T07:54:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2005/01/27/nullable-trilogy-part-ii-a-b-ab-a/
permalink: /2005/01/27/nullable-trilogy-part-ii-a-b-ab-a/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2005/01/27/361636.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "361636"
orig_parent_id:
  - "361636"
orig_thread_id:
  - "361636"
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
  - http://blogs.msdn.com/b/lucabol/archive/2005/01/27/nullable-trilogy-part-ii-a-b-ab-a.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Nullable trilogy part II: a == b -&gt; a&gt;=b &amp;&amp; a &lt;=b ?" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2005/01/27/nullable-trilogy-part-ii-a-b-ab-a/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="A&nbsp;question that often comes up when we discuss Nullable&lt;T&gt;&nbsp;&nbsp;is about&nbsp;the anti-symmetric property. This property states that if a==b then a&gt;=b and a&lt;=b. If a and b are null then this property is not satisfied in the current design as the result of &gt;= and &lt;= is always false when one of the parameters is null...." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Nullable trilogy part II: a == b -&gt; a&gt;=b &amp;&amp; a &lt;=b ?" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2005/01/27/nullable-trilogy-part-ii-a-b-ab-a/" />
    <meta name="twitter:description" content="A&nbsp;question that often comes up when we discuss Nullable&lt;T&gt;&nbsp;&nbsp;is about&nbsp;the anti-symmetric property. This property states that if a==b then a&gt;=b and a&lt;=b. If a and b are null then this property is not satisfied in the current design as the result of &gt;= and &lt;= is always false when one of the parameters is null...." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - 'C# Programming'
---
A&nbsp;question that often comes up when we discuss Nullable<T>&nbsp;&nbsp;is about&nbsp;the anti-symmetric property. This property states that if a==b then a>=b and a<=b. If a and b are null then this property is not satisfied in the current design as the result of >= and <= is always false when one of the parameters is null. This may seems surprising, but it can be easily understood when considering if null can be ordered.

We decided that null being less of (or more of) all the other elements in the domain would be an arbitrary decision and as such null cannot be ordered. If it cannot be ordered then the result of the relational operators for null is false as these operators can be defined as:

<font face="Arial" size="2"></font> <font face="Courier New"></p> 

<p>
  a<b -> ordered(a,b) && a<b
</p>

<p>
  a<=b -> ordered(a,b) && (a<b || a==b)
</p>

<p>
  </font><font face="Arial" size="2"></font>
</p>

<p>
  It might be argued that for practical reasons it is convenient to have the <= and >= operators return true in case null is on both sides, but this choice has some practical drawbacks. Consider the following code:
</p>

<p>
  <font face="Courier New"> </p> 
  
  <p>
    void ProcessTransactions(int?[] transactions, int? maxValue) {
  </p>
  
  <p>
    foreach(int? t in transactions)
  </p>
  
  <p>
    if(t < maxValue) ProcessTransaction(t);
  </p>
  
  <p>
    }
  </p>
  
  <p>
    </font><font face="Arial" size="2"></font>
  </p>
  
  <p>
    This code does what the programmer expects, even when maxValue is null (in which case it won’t process any element). Now let’s suppose that the programmer changes his mind and wants to include maxValue in the processing. He will then change the ‘<’ operator to be ‘<=’.
  </p>
  
  <p>
    Under the current design he will obtain what he expects, even in the case maxValue is null. By considering null >= null as true, this function would suddenly start processing all the null transactions, which is not what the programmer intended. The problem here is that people tend to think about the ‘>=’ and ‘<=’ operators as a way to include the limit value in the set of things to be processed. Very rarely, they intend to process the null value as well. Another way to think about it is that: deciding that null cannot be ordered implies that >= has to return false to be conceptually consistent and to prevent these quite subtle bugs to occur.
  </p>