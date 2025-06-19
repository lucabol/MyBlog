---
title: "JediMaster: LLM assigns issues to Coding Agent"
date: 2025-06-19
author: lucabol
tags: [Python, AI]
description: "A Python package that uses an LLM to automatically assign GitHub issues to a coding agent."
---
I have been working on JediMaster: a Python package that uses an LLM to assign issues to the GitHub coding agent.

The idea is to use the LLM to analyze the issue and determine if it is suitable for the coding agent to work on. If it is, the LLM will assign the issue to the coding agent (or just label it).

You can use it either as a script, as a library, or as a set of Azure Functions (i.e., to automatically assign the issues on a timer).

The code is available on GitHub: [JediMaster](https://github.com/lucabol/JediMaster).
