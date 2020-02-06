---
id: 813
title: 'Is this functional code? Dr.T. Reply.'
date: 2007-01-31T12:34:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/01/31/is-this-functional-code-dr-t-reply/
permalink: /2007/01/31/is-this-functional-code-dr-t-reply/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/01/31/is-this-functional-code-dr-t-reply.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "1566373"
orig_parent_id:
  - "1566373"
orig_thread_id:
  - "493129"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/01/31/is-this-functional-code-dr-t-reply.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Is this functional code? Dr.T. Reply." />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/01/31/is-this-functional-code-dr-t-reply/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="&nbsp; This would be a functional approach: CountWithPrevious : [‘a] =&gt; (a =&gt; a =&gt; bool) =&gt; int // type of the functionCountWithPrevious [] _ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= 0CountWithPrevious [_] &nbsp;_ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= 0CountWithPrevious [prev, val | tail] pred = CountWithPrevious [val | tail] + (pred val prev ? 1 : 0) Some observations: _” is used as..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Is this functional code? Dr.T. Reply." />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/01/31/is-this-functional-code-dr-t-reply/" />
    <meta name="twitter:description" content="&nbsp; This would be a functional approach: CountWithPrevious : [‘a] =&gt; (a =&gt; a =&gt; bool) =&gt; int // type of the functionCountWithPrevious [] _ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= 0CountWithPrevious [_] &nbsp;_ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= 0CountWithPrevious [prev, val | tail] pred = CountWithPrevious [val | tail] + (pred val prev ? 1 : 0) Some observations: _” is used as..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - csharp
---

This would be a functional approach:
~~~csharp
CountWithPrevious : [‘a] => (a => a => bool) => int // type of the function
CountWithPrevious [] _                    = 0
CountWithPrevious [_]  _                  = 0
CountWithPrevious [prev, val | tail] pred = CountWithPrevious [val | tail] + (pred val prev ? 1 : 0)
~~~
Some observations:

_” is used as wildcard argument – matches any value that you don’t need a name for.
[ x,y,z | t ] are pattern matching over lists – here x,y and z get bound to the first elements and t is the rest of the list.
Both CountWithPrevious and the passed-in pred are curried – they take two arguments but one at a time.
The CountWithPrevious function is defined with pattern matching – at runtime it searches through the definitions until one matches.
The type declaration is optional – the compiler can figure out the type from the last case of the function.
In C# we don’t have pattern matching and currying, and so would probably need a helper function.
~~~csharp
public static int CountWithPrevious<T>(IEnumerable<T> en, PredWithPrevious pred) {
IEnumerator<T> rest = en.GetEnumerator();

if (rest.MoveNext()) return Helper(rest.Current,rest,pred);

else return 0;

}

private static int Helper<T>(T prev, IEnumerator<T> rest, PredWithPrevious pred) {

if (rest.MoveNext()) {

T val = rest.Current;

return Helper(val,rest,pred) + (pred(val,prev) ? 1 : 0);

} else return 0;

}

We could simulate local functions with lambdas so that we don’t need to pass pred, prev and T along:

public static int CountWithPrevious<T>(IEnumerable<T> en, PredWithPrevious pred) {
IEnumerator<T> rest = en.GetEnumerator();

Func<T,int> helper = prev => {

if (rest.MoveNext()) {

T val = rest.Current;

return Helper(val) + (pred(val,prev) ? 1 : 0);

} else return 0;

};

if (rest.MoveNext()) return Helper(rest.Current);

else return 0;

}
~~~