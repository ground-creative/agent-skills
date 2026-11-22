---
name: skill-name
description: What this skill does, and when to use it — including the words a task would contain when it should be triggered. This sentence does the whole job of matching a task to the skill, so name both the capability and the trigger.
---

# Skill title

One paragraph: the capability this skill gives the agent, in the agent's terms.

## When this applies

- the situations that should activate it;
- and the near-misses that should not, so the agent does not overreach.

## How to do it

Steps or rules, in the order they matter. Invariants live here; the specific task
lives in the agent's prompt.

## What good output looks like

A small example, or an explicit shape. If the skill ends with a proposal or a
hand-off, say so and say that the agent must not act on its own proposal.

## Anti-patterns

- the specific mistakes this skill exists to prevent.

<!--
Authoring notes, delete before shipping:
- `name` must equal the directory name, lowercase, hyphens only.
- Body under 500 lines; move detail into references/ and link it.
- No tool schemas: the MCP server already advertises them.
- Validate with `python3 tools/check.py skills`.
-->
