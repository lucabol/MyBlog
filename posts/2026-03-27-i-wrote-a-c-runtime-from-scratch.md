---
title: "I wrote a C runtime from scratch"
date: 2026-03-27
author: lucabol
tags: [AI, C, programming]
description: "A small C runtime with no libc: syscalls, graphics, and UI in three header files — built to understand what really happens between code and hardware."
---

I wanted to understand what happens between my C code and the hardware. Not in theory — I've read the textbooks. I wanted to feel it: write the syscalls, handle the startup, own every byte in the binary.

So I wrote a small C runtime from scratch: [lucabol/laststanding](https://github.com/lucabol/laststanding).

It's three header files. `l_os.h` gives you the basics — strings, memory, file I/O, processes, pipes, terminal control. All implemented with direct syscall wrappers, no libc anywhere. `l_gfx.h` adds pixel graphics — drawing primitives, a bitmap font, keyboard and mouse input. `l_ui.h` builds on that with immediate-mode UI widgets: buttons, sliders, checkboxes, text inputs.

It runs on Linux (x86_64, ARM, AArch64) and Windows. Binaries are statically linked, stripped, and typically 2–10 KB. A hello world on ARM compiles to 676 bytes.

The repo includes a dozen small Unix-style utilities (grep, sort, wc, ls), a Vim-style text editor, a shell that can run itself, a snake game, a Mandelbrot renderer, and several graphical demos — plasma, starfield, Doom-style fire, Conway's Life, an analog clock. Plus a couple of UI demos showing forms and sliders. Everything compiles with `-ffreestanding -nostdlib` and nothing links to libc.

The whole thing is built around static inline functions, so you only pay for what you use. On Linux, syscalls go through inline assembly. On Windows, it calls Win32 APIs directly with UTF-8 to UTF-16 conversion at the boundary. The graphics layer writes to the Linux framebuffer or opens a native GDI window. The UI is immediate-mode: no heap, no widget tree, just declare your widgets every frame.

AI helped enormously. I used it to scaffold the initial code, write tests across four architectures, debug platform differences, and iterate on the API design. What would have taken weeks of manual cross-platform plumbing happened in days. The CI runs 22 targets — Windows, Linux, ARM32, AArch64, each with gcc and clang — and AI helped get them all green.

It's not a production library. It's a learning project that got slightly out of hand. But there's something satisfying about a binary that contains nothing you didn't put there yourself.
