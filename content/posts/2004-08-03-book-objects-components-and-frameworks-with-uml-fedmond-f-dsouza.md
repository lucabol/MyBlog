---
id: 993
title: 'Book: Objects, Components, and Frameworks with UML, Fedmond F. D`Souza'
date: 2004-08-03T13:13:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2004/08/03/book-objects-components-and-frameworks-with-uml-fedmond-f-dsouza/
permalink: /2004/08/03/book-objects-components-and-frameworks-with-uml-fedmond-f-dsouza/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2004/08/03/207281.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "207281"
orig_parent_id:
  - "207281"
orig_thread_id:
  - "207281"
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
  - http://blogs.msdn.com/b/lucabol/archive/2004/08/03/book-objects-components-and-frameworks-with-uml-fedmond-f-dsouza.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Book: Objects, Components, and Frameworks with UML, Fedmond F. D`Souza" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2004/08/03/book-objects-components-and-frameworks-with-uml-fedmond-f-dsouza/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="This is a book about Catalysis, an OO methodology. I read this book some time ago (like years). It is a quite complex book. If you don't like methodologists, it will easily put you to sleep. But if you stay awake, it is worth it. It is strange how this book crystallized one concept for..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Book: Objects, Components, and Frameworks with UML, Fedmond F. D`Souza" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2004/08/03/book-objects-components-and-frameworks-with-uml-fedmond-f-dsouza/" />
    <meta name="twitter:description" content="This is a book about Catalysis, an OO methodology. I read this book some time ago (like years). It is a quite complex book. If you don't like methodologists, it will easily put you to sleep. But if you stay awake, it is worth it. It is strange how this book crystallized one concept for..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - Books
  - Object Orientation
---
This is a [book](http://www.amazon.com/exec/obidos/tg/detail/-/0201310120/qid=1091563751/sr=8-2/ref=sr_8_xs_ap_i2_xgl14/002-4177789-5140026?v=glance&s=books&n=507846) about Catalysis, an OO methodology. I read this book some time ago (like years). It is a quite complex book. If you don't like methodologists, it will easily put you to sleep. But if you stay awake, it is worth it.

It is strange how this book crystallized one concept for me:&nbsp;the definition of an interface. An interface is not just the sum of the signatures of the methods. It is a conceptual framework. The only way to fully describe it is to describe in a formal way this conceptual framework. For example without further specification it is impossible to know how to use this interface:

interface IBook() {

&nbsp; void AddPage(IPage p);

}

What happens when you add a page? Will it add it at the end of the book? At the start? What happens if you call the method twice? Will the pages be in order? Will they be in the same section? Is there a concept of a section?

There are ways to&nbsp;make explicit&nbsp;the implicit model beyond an interface: the one that&nbsp;I've commonly seen being used is documentation.&nbsp;The book argues for&nbsp;formal contracts (preconditions, postconditions, invariants). The latter is certainly more formal, but to use it you need to describe formally what is the state beyond the interface and how the different methods affect this state. It is a lot of work.

Is it worth the effort? I guess it depends on a zillion things like: the type of project, the people involved,&nbsp;I don't think anybody is actually doing it, but it is still a good conceptual framework to keep in mind when you define your interfaces: it is not enough to write down the signature methods, you have somehow to expose the conceptual framework (where somehow means more or less formally).