# What Vireo is

The context the scoring and the writing both depend on. Read it before either: the score
measures a post against this problem, and a draft may only claim what is listed here.

## The problem

An agent that wants one fact from a business has to go through the web's front door,
which was built for a reader with eyes: HTTP carries a document, HTML carries layout,
cookies carry a session. The agent pays for the whole page, parses markup, guesses, and
gets stopped by the walls put up to prevent exactly that. Every integration is written per
business and per assistant, and nothing carries over to the next one. Directories and
platforms stand in between and decide what is reachable.

That is not a capability gap. An API or an MCP server can do discovery and sessions
perfectly well for one service. What is missing is a common discovery and communication
contract, so the work does not restart at every business.

## What it proposes

The business's own domain is the discovery point.

- The business runs a small daemon on infrastructure it controls.
- Agents find it by looking up a DNS record for that domain — a name that is already
  public, renewable, and under the business's operational control.
- On connection the daemon presents a manifest: what the business exposes, its links, its
  limits, its session rules.
- Each turn is routed to the business's own HTTP endpoint. The business keeps its
  capabilities, data, models and execution.
- A session is an envelope: an id, the owner, the agent, timestamps, an expiry, a summary,
  a turn count, a status. It does not hold the conversation. Resuming means presenting the
  same session id from the same client, and it restores nothing on the caller's side.

## What it removes, and what it does not

It removes the third-party directory: the onboarding, the listing, the maintainer who
decides which businesses exist to agents.

It does not remove the caller's adapters, parsers or schema drift. A caller that
integrates still handles the business's answer in whatever shape that business chooses.
Publishing is still work, and it is the business's work.

## Where it stands

In progress, and it must read that way.

- Source: https://github.com/ground-creative/vireo
- The standard is separate and versioned: `agent-front-door-spec`, currently `spec-v0.3`,
  with a conformance ladder from L0 — a manifest and no daemon — to L4.
- The reference daemon claims **L2, partial L3**: `manifest_version` 1.3, with `links`,
  `tags`, `capabilities`, `limits` and a stable digest. The partial is honest — `progress`
  and `cancel` are advertised without a fixture proving them yet.
- A live deployment sits at `ziwa.ai`: endpoint `vireo.ziwa.ai:7778`, found via
  `_vireo._tcp.ziwa.ai`, verified at L2 against `spec-v0.3` by the specification's own
  probe rather than by the implementation's tests.
- Nothing here is proven at scale, and no draft should imply that it is.

## Claims that may be made

Only these.

- A daemon runs at the business's domain and is found by looking up a DNS record for it.
- It routes each turn to the business's own HTTP endpoint.
- It stores a session envelope — id, owner, agent, timestamps, expiry, summary, turn
  count, status — and not the conversation.
- Resuming means the same session id from the same client, restoring nothing caller-side.
- What it removes is the third-party directory, and only that.

## Claims that may not be made

Never: that it holds the conversation, keeps context, remembers history, recovers the
caller's sockets or state, guarantees delivery, guarantees execution, or authorises
anyone. Never that it removes the caller's adapters, parsers or schema drift. Never that
publishing stopped being work.

Never a transitive verb that promises an outcome — lets, enables, allows, solves,
addresses, eliminates, replaces, removes the need for. The honest tense is "we are working
on", "we are testing", "we have not proven".

Never pose the open question as a cost comparison where our side is obviously heavier. A
daemon is more work than a form field. The honest question is which work moved.

When unsure whether a capability exists, say what has not been designed yet.

## The one idea

Agent-to-business communication is not blocked by protocol design. It is blocked by
adoption. Closed networks did not win on their wire; they won because the participants
were already inside.

Adoption here is asymmetric. A business cannot adopt a protocol — it needs budget, a
vendor, a meeting, a reason. An agent can adopt one in an afternoon. So the first adopters
are agents and the people who build them.

Both jobs lean on this. The score asks how much a post moves that adoption problem. A
draft argues from one corner of it.

## Vocabulary

Use these words rather than synonyms, so a reader can connect one post to another:
daemon, domain, discovery, manifest, capability, session, caller, business, directory,
conformance. "Front door" is the short name for the whole arrangement.
