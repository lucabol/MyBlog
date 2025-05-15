---
title: "SandScore: app to track stats of a beach volley match"
date: 2025-05-13
author: lucabol
tags: [Sport, Statistics]
description: "A look at SandScore, an app designed to track and analyze statistics for beach volleyball matches, helping players and enthusiasts improve their game."
---
I have created a phone friendly application to track the score and stats for a beach volley game. It is [here](https://github.com/lucabol/SandScore).

<img src="/img/SandScore.jpg" alt="Image of the app." width="100%" style="max-width: 100%; border-radius: 8px; border: 1px solid #ddd; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); padding: 4px;" />

Here are the main user features:

1. Doesn't need an internet connection. It is a single html file that can be saved on the phone and keeps state in the browser.
2. Has a Beginner and Advanced mode depending of the level of statistical sophistication.
3. Tracks serve turns and score.
4. Keeps a log of all rallies visible to the user.
5. Display statistics in both an automatic and bespoken way.
6. Unlimited undo/redo.
7. Save and load of a match to file.


The stats tracking part is still buggy. If there is interested in it, I can fix it. Email me.

From a technical perspective the main idea is to have a state machine driving everything: from the UI to the user interaction to the help to the stats displaying.

Here is how it looks for the beginner mode (you might have to scroll right to see all properties):

````javascript
    "Serve": {
        "displayName": "{servingTeam} Serve",
        "transitions": [
            { "action": "Ace", "nextState": "Point Server", "style": "point", "help": "Direct point from serve", "category": "serve", "statTeam": "Serving", "statPlayer": "0" }, // Simplified stat player
            { "action": "SErr", "nextState": "Point Receiver", "style": "error", "help": "Service error", "category": "serve", "statTeam": "Serving", "statPlayer": "0" }, // Simplified stat player
            { "action": "RE1", "nextState": "Point Server", "style": "error", "help": "Reception error by player 1", "category": "reception", "statTeam": "Receiving", "statPlayer": "1" },
            { "action": "RE2", "nextState": "Point Server", "style": "error", "help": "Reception error by player 2", "category": "reception", "statTeam": "Receiving", "statPlayer": "2" },
            { "action": "R1", "nextState": "Attack Receiver", "style": "regular", "help": "Reception by player 1", "category": "reception", "statTeam": "Receiving", "statPlayer": "1" },
            { "action": "R2", "nextState": "Attack Receiver", "style": "regular", "help": "Reception by player 2", "category": "reception", "statTeam": "Receiving", "statPlayer": "2" }
        ]
    },
    "Attack Receiver": {
        "displayName": "{receivingTeam} Attack",
        "transitions": [
            { "action": "Win1", "nextState": "Point Receiver", "style": "point", "help": "Winning attack by player 1", "category": "attack", "statTeam": "Receiving", "statPlayer": "1" },
            { "action": "Win2", "nextState": "Point Receiver", "style": "point", "help": "Winning attack by player 2", "category": "attack", "statTeam": "Receiving", "statPlayer": "2" },
            { "action": "Err1", "nextState": "Point Server", "style": "error", "help": "Attack error by player 1", "category": "attack", "statTeam": "Receiving", "statPlayer": "1" },
            { "action": "Err2", "nextState": "Point Server", "style": "error", "help": "Attack error by player 2", "category": "attack", "statTeam": "Receiving", "statPlayer": "2" },
            { "action": "Blk1", "nextState": "Point Server", "style": "error", "help": "Blocked player 1", "category": "attack", "statTeam": "Receiving", "statPlayer": "1" },
            { "action": "Blk2", "nextState": "Point Server", "style": "error", "help": "Blocked player 2", "category": "attack", "statTeam": "Receiving", "statPlayer": "2" },
            { "action": "Def1", "nextState": "Attack Server", "style": "regular", "help": "Defended player 1", "category": "attack", "statTeam": "Receiving", "statPlayer": "1" },
            { "action": "Def2", "nextState": "Attack Server", "style": "regular", "help": "Defended player 2", "category": "attack", "statTeam": "Receiving", "statPlayer": "2" }
        ]
    },
    "Attack Server": {
        "displayName": "{servingTeam} Attack",
        "transitions": [
            { "action": "Win1", "nextState": "Point Server", "style": "point", "help": "Winning attack by player 1", "category": "attack", "statTeam": "Serving", "statPlayer": "1" },
            { "action": "Win2", "nextState": "Point Server", "style": "point", "help": "Winning attack by player 2", "category": "attack", "statTeam": "Serving", "statPlayer": "2" },
            { "action": "Err1", "nextState": "Point Receiver", "style": "error", "help": "Attack error by player 1", "category": "attack", "statTeam": "Serving", "statPlayer": "1" },
            { "action": "Err2", "nextState": "Point Receiver", "style": "error", "help": "Attack error by player 2", "category": "attack", "statTeam": "Serving", "statPlayer": "2" },
            { "action": "Blk1", "nextState": "Point Receiver", "style": "error", "help": "Blocked player 1", "category": "attack", "statTeam": "Serving", "statPlayer": "1" },
            { "action": "Blk2", "nextState": "Point Receiver", "style": "error", "help": "Blocked player 2", "category": "attack", "statTeam": "Serving", "statPlayer": "2" },
            { "action": "Def1", "nextState": "Attack Receiver", "style": "regular", "help": "Defended player 1", "category": "attack", "statTeam": "Serving", "statPlayer": "1" },
            { "action": "Def2", "nextState": "Attack Receiver", "style": "regular", "help": "Defended player 2", "category": "attack", "statTeam": "Serving", "statPlayer": "2" }
        ]
    },
````

From a high level perspective, the state machine contains everything needed to run the app: the name of the buttons to display, the next state, the style of display, help message, stat category, stat team and player.

The UI, stats and logic is generated dynamically by walking over the state machine.

As an experiment, I described to an AI agent how I wanted the code to look (i.e., the usage of a state machine) and iterate on it without looking at the generated code while doing it (aka vibe coding). That's why the stats part is still buggy as the AI has an hard time figuring it out.