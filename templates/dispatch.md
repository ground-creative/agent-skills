# Dispatch

A skill instructs the agent doing the job. It cannot instruct the agent *asking* for the
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

Say what to write in ordinary prose and include:

  - what happened — who did it and when, a decision, an announcement, a number
  - the point to make, if you want a particular one
  - what to leave out, if anything
  - how many drafts, if not one
  - the post id for a comment, and the comment id for a reply

Do not summarise the project, the specification, or our features; the skill carries them
and repeating them makes the draft over-apply them. Do not ask it to check whether the
story is true: it cannot look things up for that purpose, and it will stop writing to try.

Example:

  Write a post. Amazon sued Perplexity over Comet buying on a customer's behalf and
  calling it unauthorised access. Make the point that a platform granting access is a
  platform owning the relationship. No feature list. One draft, do not publish.

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
this needs to be told". The prose above says the same four things in the caller's
vocabulary. When one changes, both change.
