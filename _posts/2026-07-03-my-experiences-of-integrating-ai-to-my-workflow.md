---
layout: post
title:  "Two Months in the Trenches: How Deeply Integrating AI Redefined My Engineering Workflow"
date:   2026-07-02 14:38:00
categories: Dev Documentation
tags:
    - Development
    - Documentation
---

The narrative around AI in software engineering usually oscillates between two
extremes: it’s either a magic wand that replaces developers or a glorified
autocomplete that generates bugs.

After spending the last two months deeply embedding AI into my daily
engineering workflow, I’ve realized the truth is far more nuanced. It is an
incredible force multiplier, but it comes with hidden costs—both financial and
cognitive.

Here is what I learned shifting from a traditional coding workflow to an
AI-accelerated one, building full-stack feature implementations using
**Golang** for the backend and **Flutter** for the frontend.

## The Tech Stack & Tooling Shift

My experiment was split into two distinct phases over the span of 60 days. In
both scenarios, the technical execution was surprisingly smooth, but the UX
completely changed how I interacted with the machine.

* **Month 1 (The Editor Extension):** I started with **GitHub Copilot**
  integrated directly into Visual Studio Code. This felt like a natural
  extension of traditional development—inline suggestions, quick chat sidebars,
  and a relatively low friction point.
* **Month 2 (The Terminal Takeover):** I switched gears to **Claude Code**,
  using their CLI tool. Moving the AI interface into the terminal shifted my
  workflow from *accepting suggestions* to *giving high-level directives*.

As the weeks went by, my velocity skyrocketed. The more I used these tools, the
faster features went from ideation to production. But the real breakthrough
wasn't just using AI—it was learning *how* to talk to it.

## From "Blind Prompting" to Context-Driven Directives

In the beginning, I asked the AI questions from a user-perspective or in
high-level language. That was a mistake.

I quickly discovered that **targeting specific files yields vastly superior and
faster results** than letting the AI guess the context. Instead of asking
*"Implement a user blocking feature,"* I learned to say *"Modify
`user_repository.go`, `user_handler.go`, and `profile_screen.dart` to support a
blocking mechanism."* By feeding it the exact boundaries of the task, the
accuracy of the output reached near-perfection.

### Shifting to Holistic Feature Development

Traditionally, I would build the backend endpoint in Go, test it, and then
switch context to Flutter to consume it. AI changed my mental model.

Instead of treating frontend and backend as separate silos, I began instructing
the AI to **implement the feature as a whole ecosystem**. I’d ask it to write
the Go endpoint and the Flutter UI implementation in a single breath.

**The Catch? Token Costs.** Flutter and frontend code in general inherently
consume significantly more tokens than concise backend Go code. Feeding UI
layouts, state management, and widgets into the context window gets expensive
quickly. While the holistic approach saved me massive amounts of
context-switching time, it definitely hit the wallet harder.

## The Cognitive Trade-Offs: Atrophy of the Mind

While my output speed has never been higher, I began noticing unsettling shifts
in my own engineering skills.

### 1. Forgetting the Syntax

Slowly but surely, I am forgetting how to code without an assistant. When the
AI handles the boilerplate, the syntax, and the typing, your muscle memory
begins to fade.

### 2. Outsourcing Investigation

I’ve noticed a decline in my urge to dive deep into debugging. Instead of
reading through tracebacks or manually analyzing database states, my first
instinct now is to dump raw logs, database query results, and error outputs
directly into the AI and ask it to investigate. It’s highly efficient, but it
feels like outsourcing the "soul" of engineering.

### 3. Losing Touch with Implementation Details

I find myself caring less and less about the granular implementation details of
the code itself. As long as the integration tests pass and the feature works
smoothly, I move on. As a craftsman, this is a compromise I don't entirely
love.

> **Keeping the Mind Sharp Outside of Work**
> To combat this cognitive decline, I’ve had to *consciously* schedule
> intentional training sessions outside of work hours. I force myself to do
> manual programming, practice data structures, and work through algorithms
> without any AI assistance. Paradoxically, using AI to save time at work has
> made my personal schedule much busier, just to maintain my mental edge.

## Guardrails & The Reality of the "AI Myth"

Despite using these tools heavily, I maintain a strict boundaries policy: **I
do not give AI access to everything.** Total autonomy is a security and
operational risk I am not willing to take. Man-in-the-middle verification is
still a mandatory part of my workflow.

Furthermore, the industry hype has created an **"AI Myth"** among clients.

Clients now expect complex features to be completed in a matter of minutes
because they believe the AI does all the work. I find myself spending more time
and effort managing expectations, educating clients, and explaining the
realities of software architecture than I used to.

## The Verdict: The Widening Gap in Software Engineering

Ultimately, these past two months have proven to me that **AI is not a
replacement for software engineers—it is a tool you must master to stay
competitive.** AI is not going to replace the profession anytime soon because
software engineering is about so much more than just churning out lines of
code; it's about systems thinking, security, compliance, and understanding
human needs.

However, AI *will* drastically widen the gap between two types of developers:

1. **The Code Workers:** Those who rely on AI solely to churn out repetitive,
   templated tasks (like standard CRUD applications).
2. **The Systems Architects:** Those who use AI to blast through the
   boilerplate so they can focus their human intelligence on system
   architecture, deep technical design, and high-level problem-solving.

AI won't take your job, but an engineer leveraging AI to think at a higher
architectural level just might. The future belongs to those who know how to
direct the machine, not just those who write the code.
