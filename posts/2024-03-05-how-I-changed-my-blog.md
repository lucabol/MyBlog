---
title: How I changed my blog
date: 2024-03-03
author: lucabol
layout: post
tags:
  - Miscellanea
  - typography
---
My blog has been going for more than 20 years. In this timespan there has been just one
change in architecture: going from `WordPress` to `Eleventy + Netlify`.

At the time, I was looking for the simplest possible solution. I didn't go far enough.

For a technical blog like mine, you don't need a static generator like `Eleventy`. A `bash` or
`Python` script is enough - so you are not forced to re-learn the static generator every time you pick up
the blog again.

Also, you don't need a web provider that knows about your static generator, like `Netlify` and compiles
your code. You can compile it on your laptop and ftp the `html` to wherever.

Also, the `html` and `css` I was generating was too complex.
* Too many `div` tags to obtain pixel perfect display.
* Server side syntax highlighting creating a tangle mess of tags in the `<code>` tag.
* Frivoulous eye candies like TOC, time of reading, web-mentions, ...
* Too many `css` variables and indirection for the sake of modularization.

The last point is interesting. In my `css`, you could change a few typographic variables
(i.e., font-size, measure, ...) and the whole site would changes. That sounds fantastic, except
that it isn't. I am not Microsoft/Google/Netflix/...

When I pick up the blog again after a few months, I forget how it all works
and end up spending hours figuring it out again. Fixing issues means wading through bogs of
indirection: is it a browser bug? My framework? ...

This is a lesson I had to learn many times, and I am still learning:
radical simplicity means you don't create a framework. You just code the damn thing.

You can see how it used to look by doing a `View source`
on [this](https://march2024--lucabol.netlify.app/posts/2022-03-07-implementing-forth-dotnet/).

The new website is still `Eleventy + Netlify`, but I fixed the `HTML + CSS` to be radically simple.
* Not a single `div` tag: just semantic tags (`article`, `main`, ...).
* No syntax highlighting. Do you really need it for small code snippets?
* No eye candies at all. Just text all the way.
* No `css` variables. Just a trivial stylesheet for the typography.

You can see the difference in the source code [here](https://www.lucabol.com/posts/2022-03-07-implementing-forth-dotnet/).

A few simplification came about as a bonus. When you radically simplify things, you often get to their hidden core.

I used to have different 'templates' for different categories of pages (i.e., post, list of posts, home page, ...).
I now have just one template. The content in the middle of the page is the only thing that changes.

One thing I have not removed is a processing pass that insert typographic niceties (like Hanging Punctuation).
You can see an example on the line that says: "I want a piece ..." [here](https://www.lucabol.com/posts/2022-03-09-horchata/).

This is frivolous, but for someone who is into typography like me
(I have created [my own font](https://www.lucabol.com/posts/2021-06-23-i-have-created-a-font-italiko/) after all),
it does matter.

The old website was already at 100% in all google `lighthouse` categories. The new one is even faster.
Not that it matters, but you know ...

The next step is to remove the dependency from the static site generator and provider. Just a simple script
that iterates over all the posts and generates the `Notes`, `Tags`, `Code` pages should be about it. Next time.

Oh, and I also need to re-introduce a way to comment on the posts. I am thinking some kind of public email box with
one thread for each post, but I have not investigated further.
