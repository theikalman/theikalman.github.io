---
layout: post
title:  "My Experience Integrating AI Into My Workflow for The Last Two Months"
date:   2026-07-02 14:38:00
categories: Dev Documentation
tags:
    - Development
    - Documentation
---

The narrative around AI in software engineering usually oscillates between two
extremes: it is either a magic wand that replaces developers or just-another
autocomplete that generates bugs.

After spending the last two months trying to embed AI into my daily
engineering workflow, I have realized the truth is far more nuanced. It is an
incredible force multiplier, but it comes with hidden costs, both financial and
cognitive.

For the background, here is the tech stack that I use on daily basis:
- I am developing CRUD app for multitenant aoutomotive workshop
- Golang on the backend
- Flutter on the frontend

### The Tech Stack & Tooling Shift

My experiment was split into two AI agent provider that I use.

* Month 1 (VSCode + Copilot): I started with GitHub Copilot, simply because
  it is cheap and also because my manager wanted to experiment with Copilot
  while he himself uses Claude Code from day 1. The Copilot integrated
  directly into Visual Studio Code. This felt like a natural extension of
  traditional development, giving inline suggestions, quick chat sidebars,
  and a relatively low friction point.
* I switched gears to Claude Code, mostly because GitHub changed its pricing
  to a usage-based model. Suddenly, my token usage went through the roof;
  I maxed out my allowance in just three days, whereas I used to only hit
  the 50% mark (granted, I used to use it less). It was a pretty steep pricing
  jump. Moving to Claude's CLI tool and keeping the AI interface in the
  terminal feels a lot less distracting. The workflow just feels smoother,
  which makes sense since I prefer Neovim over VS Code anyway.

As the weeks went by, my velocity skyrocketed. The more I used these tools, the
faster features went from ideation to production. But the real breakthrough
wasn't just using AI; it was learning how to talk to it.

### From "Blind Prompting" to Context-Driven Directives

In the beginning, I asked the AI questions from a user perspective or in
high-level language. And I feel less-satisfied with the result of it.

I quickly discovered that targeting specific files yields vastly superior and
faster results than letting the AI guess the context. Instead of asking
"Implement a user blocking feature," I learned to say "Modify
`user_repository.go`, `user_handler.go`, and `profile_screen.dart` to support a
blocking mechanism." By feeding it the exact boundaries of the task, the
accuracy of the output reached near-perfection.

#### For the Case of Holistic Feature Development

Traditionally, I would build the backend endpoint in Go, test it, and then
switch context to Flutter to consume it. AI changed my mental model.

Instead of treating the frontend and backend as separate silos, I found
myself instructing the AI to build out the feature as a whole ecosystem.
I started asking it to crank out the Go endpoint and the Flutter UI in a
single breath. At first, I thought this habit contradicted my previous
realization that detailed prompts work better than high-level "user-view"
ones. But I realized I was actually hitting a sweet spot right in the
middle: I was taking my own user-perspective goals and immediately
translating them into a deeply technical blueprint. This became my go-to
approach for building big features from scratch. The real turning point
for me, though, was forcing myself to write a detailed implementation plan
into a Markdown file first. It allowed me to thoroughly review the
architecture and track my own progress as things came together.

The Catch? Token Costs. Flutter and frontend code in general inherently
consume significantly more tokens than concise backend Go code. Feeding UI
layouts, state management, and widgets into the context window gets expensive
quickly. While the holistic approach saved me massive amounts of
context-switching time, it definitely hit the wallet harder.

### The Cognitive Trade-Offs: Atrophy of the Mind

While my output speed has never been higher, I began noticing unsettling shifts
in my own engineering skills.

#### 1. Forgetting the Syntax

Slowly but surely, I am forgetting how to code without an assistant. When the
AI handles the boilerplate, the syntax, and the typing, your muscle memory
begins to fade.

#### 2. Outsourcing Investigation

I have noticed a decline in my urge to dive deep into debugging. Instead of
reading through tracebacks or manually analyzing database states, my first
instinct now is to dump raw logs, database query results, and error outputs
directly into the AI and ask it to investigate. It is highly efficient, but it
feels like outsourcing the soul of engineering.

#### 3. Losing Touch with Implementation Details

I find myself caring less and less about the granular implementation details of
the code itself. As long as the integration tests pass and the feature works
smoothly, I move on. As a craftsman, this is a compromise I don't entirely
love.

> **Keeping the Mind Sharp Outside of Work**
>
> To combat this cognitive decline, I have had to *consciously* schedule
> intentional training sessions outside of work hours. I force myself to do
> manual programming, practice data structures, and work through algorithms
> without any AI assistance. Paradoxically, using AI to save time at work has
> made my personal schedule much busier, just to maintain my mental edge.

### Guardrails & The Reality of the "AI Myth"

Despite using these tools heavily, I maintain a strict boundaries policy: **I
do not give AI access to everything.** Total autonomy is a security and
operational risk I am not willing to take. Man-in-the-middle verification is
still a mandatory part of my workflow.

Furthermore, the industry hype has created an **"AI Myth"** among clients.

Clients now expect complex features to be completed in a matter of minutes
because they believe the AI does all the work. I find myself spending more time
and effort managing expectations, educating clients, and explaining the
realities of software architecture than I used to.

### The Verdict: The Widening Gap in Software Engineering

Ultimately, these past two months have proven to me that **AI is not a
replacement for software engineers. It is a tool you must master to stay
competitive.** AI is not going to replace the profession anytime soon because
software engineering is about so much more than just churning out lines of
code; it is about systems thinking, security, compliance, and understanding
human needs.

However, AI will drastically widen the gap between two types of developers:

1. **The Code Workers:** Those who rely on AI solely to churn out repetitive,
   templated tasks, such as standard CRUD applications.
2. **The Systems Architects:** Those who use AI to blast through the
   boilerplate so they can focus their human intelligence on system
   architecture, deep technical design, and high-level problem-solving.

AI won't take your job, but an engineer leveraging AI to think at a higher
architectural level just might. The future belongs to those who know how to
direct the machine, not just those who write the code.
