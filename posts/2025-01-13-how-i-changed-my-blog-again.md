---
title: How I changed my blog (again)
date: 2025-01-13
author: lucabol
tags: [Myscellanea, typography]
description: "In a delightful dance with AI, I transformed my blog from an Eleventy-powered behemoth into a lean, mean, Python-generated machine. Along the way, I managed to resurrect ancient comments through Github issues (because who needs JavaScript?), and convinced my AI buddy to fix a cemetery of badly formatted posts from the coding stone age. All of this with just 232 lines of embarrassingly obvious Python code - take that, complexity!"
---
I wanted to try out [Cline](https://github.com/cline/cline) on a medium-sized project. For a long time I wanted to move away from a static generator like `Eleventy` to a simple `bash` or `Python` script that generates `html` and `css` that I can ftp to wherever.

I ended up doing much more than that. All in all I worked on it for a couple of days. Without Cline it would have taken me more than a week, I suspect.

## Creating the Python script
I didn't want to reuse my existing `Eleventy` partial html fragments and css, so I instructed AI to generate a static website starting from the list of posts in in the posts directory. I then showed AI a picture of my site and asked it to generate a similar one.

We then worked on the list of Code projects generated from the `projects.yaml` file (I should auto-generate this from specially marked projects on github ...). Also, we created the `Tags` page looking at the front matter of the posts.

After a few iterations, refactorings, and bug fixes, we had a working site similar to the one I had before.

[Old site](https://web.archive.org/web/20231003045700/https://www.lucabol.com/)

[New site](https://www.lucabol.com/)

The new one is slightly simpler graphically, not because I couldn't do it, but because I chose not to.

[This](https://github.com/lucabol/MyBlog/blob/master/src/generate_blog.py) is the 232 lines of Python code that generates the site. To my eyes, the situation is vastly simplified, as I don't need to understand the intricacies of `Eleventy` anymore. Everything has become embarrassingly obvious.

## Adding a commenting system
In my folly, I don't want any Javascript on my site.

In the past, I used `Disqus`, then `webmentions`, then nothing. But `nothing` is a bit on the harsh side of life.

I decided to use Github issues as database for the comments. I know about `utterances`, but I don't want to use it as it is Javascript based. So I came up with a super simple scheme, where each post has a link to a github query containing the post title. That brings up the correct issue for the post and you can add comments to that.

It is very primitive as you cannot create a comment from the site itself, you need a Github account, etc... etc... But it is simple and it works, no Javascript required.

I also had a bunch of json files with comments from the past. I instructed AI to create a script that automatically generates issues from the posts and comments from the json files. It created [another 300 lines of Python](https://github.com/lucabol/MyBlog/blob/master/src/bulk_create_many_issues.py) (mostly because of the bizarre rate limitations on the Github API).

I haven't even looked at the script. It is enough that it worked once (took it one night, who knows??).

So now I have imported all the comments from the past and have a working commenting system, for some definition of "working".

## Fixing badly formatted old posts
And now for something that I would have never done without AI. I had a bunch of very old posts that contained very badly formatted and broken code.

The system I used at the time embedded html tags in the markdown. Properly formatting them one by one would have taken a lot of time as there is no automatic way of doing it.

Most of those posts are obsolete, but still I didn't like them to be in such bad shape. It bugged me.

"AI, buddy, please fix them for me". And it did. It took a few hours, but it did it. I had to spend a few dollars on consumption, but it worked like a charm.

[old post](https://web.archive.org/web/20240720002637/https://www.lucabol.com/posts/2008-04-21-a-c-library-to-write-functional-code-part-iii-records/)

[new post](https://www.lucabol.com/posts/2008-04-21-a-c-library-to-write-functional-code-part-iii-records/)
