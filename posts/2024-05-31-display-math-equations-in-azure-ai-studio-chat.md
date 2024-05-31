---
title: Display math equations in Azure AI Studio Chat
date: 2024-05-31
author: lucabol
layout: post
tags:
  - AI
---
Your mileage might vary. This is a dirty trick, likely to break the internet, but it kind of works.

Mathematical equations are displayed in LaTex format, basically unreadable.

I have tried to make GPT-4o
to format them in a human readable way in the Azure AI Studio Chat Playground, but failed.

So it is like this:

````latex
$$
P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}
$$
````

You instead might want something like this:

![equation](/img/Bayes.png)

The trick is to inject Javascript code that executes on a timer and uses MathJax to transform the Latex code
to an image.

There are probably better ways to do it. Here is what I did:

1. Install [Tampermonkey](https://www.tampermonkey.net/)
2. Click on the extension and pick `Create a new script`
3. Paste the script below (modified from [this thread](https://www.reddit.com/r/ChatGPT/comments/11uc9x4/just_found_this_out_today_you_can_get_chatgpt_to/))

````javascript
// ==UserScript==
// @name         ChatGPT LaTeX Display
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://chat.openai.com/*
// @match        https://ai.azure.com/playground/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=openai.com
// @grant        GM_setValue
// @run-at       document-start
// ==/UserScript==


//Prompt should end with>>> Please format any equations in LaTeX.
//TODO: Intercept WebSocket messages and re-typeset every second until the chatbot is done talking.


(function() {
    'use strict';

    console.log("Getting ready to set up MathJax");



    let tmpMathJax = {
        tex: {
            inlineMath: [['$', '$'], ['\\(', '\\)']],
            displayMath: [ ['$$','$$'], ['\[','\]'] ]
        }
    };

    var prescript = document.createElement('script');
    prescript.type = 'text/javascript';
    prescript.innerText = `
    MathJax = {
        tex: {
            inlineMath: [['$', '$'], ['\\(', '\\)']],
            displayMath: [ ['$$','$$'], ['\[','\]'] ]
        }
    };`;
    prescript.onload = function() {
        console.log("MathJax customizations loaded");
    }
    document.getElementsByTagName('head')[0].appendChild(prescript);



    console.log("Setting up MathJax");

    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.async = true;
    script.onload = function() {
        console.log("MathJax loaded!!");

        setInterval(function() {
            console.log("Re-typesetting...");
            MathJax.typeset();
        },5000);
    }
    script.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js";
    document.getElementsByTagName('head')[0].appendChild(script);

})();
````

Caveats:
1. Running something on a timer is ugly. In this case you have to wait 5 seconds to see the nice formulas.
2. It doesn't work correctly for some inline formulas.

All in all, it is a dirty hack. Perhaps it could be made 'more working', but maybe there is a better way altogheter.
