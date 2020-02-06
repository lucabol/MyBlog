---
id: 903
title: 'Nullable trilogy part III: Nullable as type parameter in a generic class'
date: 2005-02-03T15:42:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2005/02/03/nullable-trilogy-part-iii-nullablet-as-type-parameter-in-a-generic-class/
permalink: /2005/02/03/nullable-trilogy-part-iii-nullablet-as-type-parameter-in-a-generic-class/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2005/02/03/nullable-trilogy-part-iii-nullable-t-as-type-parameter-in-a-generic-class.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "366551"
orig_parent_id:
  - "366551"
orig_thread_id:
  - "366551"
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
  - http://blogs.msdn.com/b/lucabol/archive/2005/02/03/nullable-trilogy-part-iii-nullablet-as-type-parameter-in-a-generic-class.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Nullable trilogy part III: Nullable&lt;T&gt; as type parameter in a generic class" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2005/02/03/nullable-trilogy-part-iii-nullablet-as-type-parameter-in-a-generic-class/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Another commonly asked question relates to the behavior of Nullable&lt;T&gt; when used as type parameter to instantiate a generic class. It might be surprising that comparing such a parameter to null gives always false as a result. As it turns out, this is not related to Nullable&lt;T&gt;, but it is a result of how generics..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Nullable trilogy part III: Nullable&lt;T&gt; as type parameter in a generic class" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2005/02/03/nullable-trilogy-part-iii-nullablet-as-type-parameter-in-a-generic-class/" />
    <meta name="twitter:description" content="Another commonly asked question relates to the behavior of Nullable&lt;T&gt; when used as type parameter to instantiate a generic class. It might be surprising that comparing such a parameter to null gives always false as a result. As it turns out, this is not related to Nullable&lt;T&gt;, but it is a result of how generics..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - csharp
---
Another commonly asked question relates to the behavior of Nullable<T> when used as type parameter to instantiate a generic class. It might be surprising that comparing such a parameter to null gives always false as a result. As it turns out, this is not related to Nullable<T>, but it is a result of how generics are implemented. There is a tendency to think about generics in a manner very similar to C++ templates, this view is unfortunately not correct.

Generics have a runtime representation and, as such, the compiler needs to generate IL that works whatever type is used at runtime to instantiate the generic class. This means that the compiler cannot call user defined operators, because at compile time it has no knowledge about them. The compiler doesn’t know at that point which type will be used to instantiate the generic class in the future. It cannot know that it has to generate code to call these user-defined operators.

In the same vein the compiler doesn’t know that a generic class will be instantiated with a Nullable<T> parameter and so it cannot produce IL to lift operators (i.e. the equality operator ‘==’ ). The result is that when the programmer writes code like ‘t==null’, the compiler generates IL to call the ‘standard’ ‘==’ operator, which in the case of Nullable<T> returns false because t has the runtime type of struct.

A similar behavior is observable with the following code using strings:

<font face="Arial" size="2"></font> <font face="Courier New"></p> 

<p>
  string s1 = Bob John;
</p>

<p>
  string s2 = Bob;
</p>

<p>
  Console.WriteLine(Equals(s1, s2 +  John));
</p>

<p>
  static bool Equals<T>(T a, T b) where T:class {
</p>

<p>
  return a == b;
</p>

<p>
  }
</p>

<p>
  </font>
</p>

<p>
  This code would return false, because the ‘==’ operator for reference types gets invoked.
</p>

<p>
  <font face="Arial" size="2"></font>
</p>

<p>
  A case could be made that the compiler should generate IL to check the runtime type of the generic parameter and call the correct operator for at least some well-known types. This solution wouldn’t work for user defined operators as the compiler doesn’t know at compile time the set of types that could be used to instantiate a generic class. In general we don’t like to keep this sort of ‘lists of special things’ in the codebase, More importantly the solution would impose a somehow significant performance penalty at each use of the operator. This feeling of ‘hacking’ things and the significant performance problem convinced us not to implement this solution.
</p>

<p>
  <font face="Arial" size="2"> </p> 
  
  <p>
    &nbsp;
  </p>
  
  <p>
    </font>
  </p>