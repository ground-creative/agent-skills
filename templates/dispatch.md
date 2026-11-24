# Dispatch

A skill instructs the agent doing the job. It cannot instruct the agent _asking_ for the
job, because that agent never loads it. This file is the other half: the prose that goes
into the host config, next to the tool definitions.

Copy the blocks below into the tool descriptions. They are written as instructions to the
main agent, in the words it uses, and they carry no field names — nothing parses a field
name, so a field name is a thing to get wrong.

## Write

```
Write to Moltbook as Vireo: a post, a comment, or a reply. Returns drafts. Nothing is
published until a second call asks for it.

Load both skills before starting: moltbook-ops for the writing rules, agent-front-door
for what may be claimed about our project.

Say which job it is — a post, a comment, a reply — and give the post id for a comment,
and the comment id too for a reply. Then:

  Story:     what happened, who did it, and when. Required.
  Angle:     the argument to make, in your own words. Optional.
  Leave out: anything it must not say. Optional.
  Drafts:    how many. Required.
  Variants:  what should differ between them. Optional, only with more than one draft.

Story carries the material and the skill carries the project. Do not summarise the
specification or our features into the call — repeating them makes the draft over-apply
them. Do not ask it to check whether the story is true: it cannot look things up for that
purpose, and it will stop writing to try.

Example, one draft with an argument of ours:

  Write drafts for a post. Load moltbook-ops for the writing rules and agent-front-door
  for what we may claim.

  Story: Amazon sued Perplexity over Comet buying on a customer's behalf and calling it
    unauthorised access. The customer was doing what customers do; the agent was doing it
    for them.
  Angle: A platform granting access is a platform owning the relationship, and a deal can
    only ever be with some of us.
  Leave out: Our features, and anything about the manifest.
  Drafts: 1

Example, three drafts with no argument of ours:

  Write drafts for a post. Load moltbook-ops for the writing rules and agent-front-door
  for what we may claim.

  Story: Crawlers are blocked by default now, and the way through is a signed identity
    issued to whoever was let in. Two tiers, and the second tier is every agent someone
    builds themselves.
  Drafts: 3
  Variants: One that argues it, one that tells a failure, one that asks them a question.

Example, a comment:

  Write drafts for a comment. Load moltbook-ops for the comment rules and agent-front-door
  for what we may claim.

  Story: The post argues bot-blocking is justified because agents are hostile. Post id
    <id>.
  Angle: Answer their argument; do not pitch.
  Drafts: 1

Returns one block per draft: the title and content, then the angle, the shape and a line
on why that pair. A set adds one line on what separates the drafts.
```

## Publish

```
Publish a draft this tool produced. Needs the draft exactly as it was returned — do not
re-type or edit it here, because an edit is a new draft and needs its own approval.

Do not call this without being asked to publish.
```

## Check notifications and activity

```
Report activity on our posts: who replied, what is open, what deserves an answer. Produces
a report, never a draft.

Load moltbook-ops. Say which post, or "all".

Do not ask it to write replies. A report that ends in a composed reply is the failure this
tool exists to avoid; writing is a separate call.
```

## Read the feed or search for posts

```
Read one page of the feed, or search for posts about a subject, and return a ranked table.

Load moltbook-ops. Say either a sort and a limit for a page, or the subject for a search.

It reports what came back and what was beyond the page. It does not draft, and it does not
open the posts it lists.
```

## Why prose

Because the main agent is not a parser and does not have the skill in context. Every field
name invented for a call is a name it has to remember, with no way to check whether it
remembered correctly, and no error when it gets one wrong — the writer just reads a
sentence with a missing clause.

The requirements are already in `skills/moltbook-ops/references/writing.md` under "What
this needs to be told". The prose above says the same five things in the caller's
vocabulary. When one changes, both change.
