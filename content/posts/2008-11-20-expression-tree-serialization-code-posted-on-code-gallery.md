---
id: 343
title: Expression tree serialization code posted on Code Gallery
date: 2008-11-20T15:39:20+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2008/11/20/expression-tree-serialization-code-posted-on-code-gallery/
permalink: /2008/11/20/expression-tree-serialization-code-posted-on-code-gallery/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2008/11/20/expression-tree-serialization-code-posted-on-code-gallery.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "9130403"
orig_parent_id:
  - "9130403"
orig_thread_id:
  - "620145"
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
  - http://blogs.msdn.com/b/lucabol/archive/2008/11/20/expression-tree-serialization-code-posted-on-code-gallery.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Expression tree serialization code posted on Code Gallery" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/11/20/expression-tree-serialization-code-posted-on-code-gallery/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Luke and I worked on this last year for one week doing pair programming. It is a good sample of how you can serialize LINQ expression trees to xml. The sample includes these components: An Expression Tree serialization API: A general purpose XML serialization of Expression Trees. This should work over any expression tree  -..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Expression tree serialization code posted on Code Gallery" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2008/11/20/expression-tree-serialization-code-posted-on-code-gallery/" />
    <meta name="twitter:description" content="Luke and I worked on this last year for one week doing pair programming. It is a good sample of how you can serialize LINQ expression trees to xml. The sample includes these components: An Expression Tree serialization API: A general purpose XML serialization of Expression Trees. This should work over any expression tree  -..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
---
[Luke](http://blogs.msdn.com/lukeh/default.aspx) and I worked on this last year for one week doing pair programming. It is a good sample of how you can serialize LINQ expression trees to xml. 

The sample includes these components:

  1. **An Expression Tree serialization API**: A general purpose XML serialization of Expression Trees. This should work over any expression tree  - though there are inevitably bugs. The serialization format is fairly crude, but has been expressive enough to support the variety of expression trees I've tried throwing at it. 
  2. **A wrapper for serializing/deserializing LINQ to SQL queries**: A wrapper around the expression serializer allows serializing LINQ to SQL queries and de-serializing into a query against a given DataContext. 
  3. **A WCF service which accepts serialized query expression trees and executes against a back-end LINQ to SQL**: To enable querying across tiers, a WCF service exposes service methods which execute serialized queries. The service implementation deserializes the queries against its LINQ to SQL connection. 
  4. **An IQueryable implementation wrapping the client side of the WCF service**: The client-side calling syntax is simplified by providing an IQueryable implementation. This implementation, RemoteTable, executes queries by serializing the query expression tree and calling the appropriate service. The object model that the service user is able to query against is imported by the WCF service reference per the DataContracts on the LINQ to SQL mapping on the server side

The [sample](http://code.msdn.microsoft.com/exprserialization) is here. Enjoy!