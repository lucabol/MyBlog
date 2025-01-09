---
id: 623
title: 'Instead of a simple switch statement'
date: 2007-08-31T16:54:15+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/08/31/instead-of-a-simple-switch-statement/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/08/31/instead-of-a-simple-switch-statement.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "4675574"
orig_parent_id:
  - "4675574"
orig_thread_id:
  - "532927"
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
  - http://blogs.msdn.com/b/lucabol/archive/2007/08/31/instead-of-a-simple-switch-statement.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Instead of a simple switch statement" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/08/31/instead-of-a-simple-switch-statement/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="This&nbsp;is Luke&#8216;s kind of code. I might be catching the virus abstract class QIFParserBase { public enum LoadOptions { All, Prices, Securities, Transactions } static readonly Dictionary&lt;LoadOptions, Action&lt;QIFParserBase, string[]&gt;&gt; parseFuncs = new Dictionary&lt;LoadOptions, Action&lt;QIFParserBase, string[]&gt;&gt; { {LoadOptions.All, (q,c) =&gt; q.ParseAll(c)}, {LoadOptions.Prices, (q,c) =&gt; q.ParsePricesBlocks(c)}, {LoadOptions.Securities, (q,c) =&gt; q.ParseSecurityBlocks(c)}, {LoadOptions.Transactions, (q,c) =&gt; q.ParseTransactionBlocks(c)} }; public..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Instead of a simple switch statement" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/08/31/instead-of-a-simple-switch-statement/" />
    <meta name="twitter:description" content="This&nbsp;is Luke&#8216;s kind of code. I might be catching the virus abstract class QIFParserBase { public enum LoadOptions { All, Prices, Securities, Transactions } static readonly Dictionary&lt;LoadOptions, Action&lt;QIFParserBase, string[]&gt;&gt; parseFuncs = new Dictionary&lt;LoadOptions, Action&lt;QIFParserBase, string[]&gt;&gt; { {LoadOptions.All, (q,c) =&gt; q.ParseAll(c)}, {LoadOptions.Prices, (q,c) =&gt; q.ParsePricesBlocks(c)}, {LoadOptions.Securities, (q,c) =&gt; q.ParseSecurityBlocks(c)}, {LoadOptions.Transactions, (q,c) =&gt; q.ParseTransactionBlocks(c)} }; public..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - csharp
---
This&nbsp;is [Luke](http://blogs.msdn.com/lukeh/default.aspx)&#8216;s kind of code. I might be catching the virus

```csharp
abstract class QIFParserBase {
    public enum LoadOptions {
        All,
        Prices,
        Securities,
        Transactions
    }
    static readonly Dictionary<LoadOptions, Action<QIFParserBase, string[]>> parseFuncs =
                                        new Dictionary<LoadOptions, Action<QIFParserBase, string[]>> {
        {LoadOptions.All, (q,c) => q.ParseAll(c)},
        {LoadOptions.Prices, (q,c) => q.ParsePricesBlocks(c)},
        {LoadOptions.Securities, (q,c) => q.ParseSecurityBlocks(c)},
        {LoadOptions.Transactions, (q,c) => q.ParseTransactionBlocks(c)}
    };
    public QIFParserBase(string fileName, LoadOptions opt) {
        string content = File.ReadAllText(fileName);
        string[] blocks = content.Split(new string[] { "!Type:", "!Option:" },
                                                        StringSplitOptions.RemoveEmptyEntries);
        parseFuncs[opt](this,blocks);
    }
