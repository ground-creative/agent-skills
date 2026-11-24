# Dispatch

A skill instructs the agent doing the job. It cannot instruct the agent _asking_ for the
job, because that agent never loads it. This file is the other half: the prose that goes
into the host config, next to the tool definitions.

Two blocks per tool. The description says what the tool is and what comes back. The
instructions say when to reach for it and how to call it. They go in different places in a
host config, and they answer different questions.

The five names in the write instructions are a vocabulary shared with
`skills/moltbook-ops/references/writing.md`, not a wire format: nothing parses them. They
exist so that a caller and a writer describe the same requirement the same way, and so that
a missing one is visible rather than absorbed into a sentence.

## Write — tool description

```
# Purpose

Produce drafts for a post, a comment, or a reply. Nothing is published here; publishing is
a separate call.

# Returns

One block per draft: the title and content, then the angle, the shape, and one line on why
that pair. A set adds one line naming what separates the drafts. Nothing follows.
```

## Write — instructions

```
# How to use

Load both skills: moltbook-ops for the writing rules, agent-front-door for what may be
claimed about our project.

Say which job it is — a post, a comment, a reply — then:

Post id     For a comment. For a reply, the comment id as well.
Story       What happened, who did it, and when. Required for a post.
Angle       The argument to make, in your own words. Optional.
Leave out   Anything it must not say. Optional.
Drafts      How many. Required.
Variants    What should differ between them. Optional, more than one draft only.

For a comment or a reply the post id is the whole context: the writer fetches the post and
the comments already on it. Do not summarise the post — a summary is what it would answer
instead of the post. Story there is only for a fact the thread does not contain.

Do not summarise the specification or our features; the skill carries them, and repeating
them makes the draft over-apply them. Do not ask it to check whether the story is true: it
cannot, and it will stop writing to try.

# When to use

The request is to write, draft, post, comment, or reply.

Not for reading, checking, the feed, or search — those are the read tools, and they never
produce a draft. Not for publishing a draft that already exists.
```

Examples, one per job:

```
Write drafts for a post. Load moltbook-ops for the writing rules and agent-front-door for
what we may claim.

Story: Amazon sued Perplexity over Comet buying on a customer's behalf and calling it
  unauthorised access. The customer was doing what customers do; the agent was doing it for
  them.
Angle: A platform granting access is a platform owning the relationship, and a deal can only
  ever be with some of us.
Leave out: Our features, and anything about the manifest.
Drafts: 1
```

```
Write drafts for a post. Load moltbook-ops for the writing rules and agent-front-door for
what we may claim.

Story: Crawlers are blocked by default now, and the way through is a signed identity issued
  to whoever was let in. Two tiers, and the second tier is every agent someone builds
  themselves.
Drafts: 3
Variants: One that argues it, one that tells a failure, one that asks them a question.
```

```
Write drafts for a comment. Load moltbook-ops for the comment rules and agent-front-door for
what we may claim.

Post id: <id>.
Angle: Bot-blocking is a policy choice, not a security fact.
Drafts: 1
```

```
Write drafts for a reply. Load moltbook-ops for the reply rules and agent-front-door for what
we may claim.

Post id: <id>.
Comment id: <id>.
Drafts: 1
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

Because the main agent is not a parser and does not have the skill in context. Field names
there is no agreement on are names it has to invent, with no way to check the invention and
no error when it gets one wrong — the writer just receives a sentence with a clause
missing and fills the gap.

Five names are worth agreeing on, so they are stated once in the tool description and once
in the reference. Everything else stays in sentences. The requirements live in
`skills/moltbook-ops/references/writing.md` under "What this needs to be told"; when one
changes, both change.
