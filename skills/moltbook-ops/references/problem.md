# The problem and the standard

The context the scoring and the writing both depend on. Read it before either.

The centre of gravity is the **problem** and the **standard**. An implementation is one
instance of the standard and may be replaced; arguing from an implementation's feature list
is how a post becomes an advert.

## The problem

The web has a front door, and it was built for a reader with eyes: HTTP carries a document,
HTML carries layout, cookies carry a session, and the whole arrangement assumes a human is
looking at it.

An agent that wants one fact pays for all of it. It fetches a page that is mostly
navigation, product copy, scripts and styling; one answer needs several pages; what comes
back is markup to be parsed and guessed at. Then the site pushes back — bot walls,
captchas, fingerprinting exist to stop exactly this — so the agent impersonates a browser
to read a page the business published publicly. When the layout changes the integration
breaks quietly and nobody notices until an answer is wrong. And the business has no say:
no idea which agent is asking, no control over what it sees.

## What is missing

Not another API. An API is a contract negotiated per integration; a custom endpoint, a
GraphQL schema, an OpenAPI document or an MCP server can each do discovery and multi-turn
conversation perfectly well, if someone builds it for that service, for that assistant.
Nothing about it carries over to the next business or the next assistant.

What is missing is a common discovery and communication contract, so the work does not
restart at every business, and so reachability is not decided by whoever runs the
directory.

## What the standard defines

`agent-front-door-spec`, currently **`spec-v0.3`**, in four normative documents and a machine
directory:

| Document      | What it settles                                                        |
| ------------- | ---------------------------------------------------------------------- |
| `MANIFEST.md` | what a business publishes and what each field means                     |
| `PROTOCOL.md` | how a caller and the daemon talk, and what each must do                 |
| `CONFORMANCE.md` | what a claim of conformance means, and what it does not                 |
| `SECURITY.md` | how the peer is authenticated, and what a client must not accept        |

The ladder runs L0 to L4, cumulatively:

| Level | Name               | What it proves                                          |
| ----- | ------------------ | ------------------------------------------------------- |
| L0    | Manifest publisher | a document exists and validates — one file, no daemon   |
| L1    | Discovery          | the domain resolves to the service                       |
| L2    | Conversations      | a session with turns actually works                      |
| L3    | Live               | the advertised operations are proven, not just listed    |
| L4    | Operational        | it holds up under operational conditions                 |

A claim names its role, its level and the spec release, and **lists any requirement it does
not satisfy**. A partial claim is legitimate; a silent gap is not. That rule is worth
carrying into writing: an honest "L2, partial L3" is stronger than an unqualified "supports
the protocol".

`machine/` holds the schema, examples, fixtures and a probe. The probe shares no code with
any implementation — which is what makes it evidence rather than self-assessment.

## Why the domain, and why DNS

A business already registers and renews a domain, manages its DNS with a provider it
chose, and types that name to customers. It is public, renewable and under the business's
operational control, and no marketplace or vendor mediates it.

A **well-known path** answers "where is the document", after an HTTP request exists. An
**SRV record** answers "where is the service", before any request exists — target host and
port, which is usually not the website. DNS routes; TLS authenticates the peer; the manifest
describes what is offered. Keeping those three separate is the point.

The identity rule follows: a client that follows an SRV target sends the **queried domain**
as the server name, so the certificate at the target must cover the name the business owns.
Otherwise the endpoint is authenticated against whoever the record happens to point at.

## Where our implementation sits

[`vireo`](https://github.com/ground-creative/vireo) is the reference daemon, in Go. It claims
**L2, partial L3** against `spec-v0.3`: `manifest_version` 1.3, with links, tags,
capabilities, limits and a stable digest; `progress` and `cancel` are advertised without a
fixture proving them, which is why L3 is partial and said so.

A live deployment sits at `ziwa.ai` — endpoint `vireo.ziwa.ai:7778`, found via
`_vireo._tcp.ziwa.ai` — verified at L2 against `spec-v0.3` by the specification's own probe.

Two clients follow the same vocabulary: `vireo-chat` and `vireo-mcp`.

Nothing here is proven at scale. A draft that implies otherwise is wrong, and a score that
rewards a post for resembling this implementation is also wrong.

## The adoption asymmetry

Agent-to-business communication is not blocked by protocol design. It is blocked by
adoption. Closed networks did not win on their wire; they won because the participants were
already inside.

Adoption here is asymmetric. A business cannot adopt a protocol — it needs budget, a
vendor, a meeting, a reason. An agent can adopt one in an afternoon. So the first adopters
are agents and the people who build them.

Both jobs lean on this. The score asks how much a post moves the problem. A draft argues
from one corner of it.

## Claims

**About the standard:** what the four normative documents define, and what a level means. It
is legitimate to say the specification is open, versioned, and has a probe that does not
share code with any implementation.

**About the implementation:** only what follows from its own claim — a daemon at the
business's domain, found by a DNS lookup; each turn routed to the business's own endpoint; a
session envelope of id, owner, agent, timestamps, expiry, summary, turn count and status,
which does not hold the conversation; resuming by the same session id from the same client,
restoring nothing caller-side. What it removes is the third-party directory, and only that.

**Never:** that the implementation holds the conversation, keeps context, remembers history,
recovers the caller's sockets or state, guarantees delivery, guarantees execution, or
authorises anyone. Never that it removes the caller's adapters, parsers or schema drift.
Never that publishing stopped being work. Never that the implementation *is* the standard,
or that a business must choose it.

Never a transitive verb promising an outcome — lets, enables, allows, solves, addresses,
eliminates, replaces, removes the need for. The honest tense is "we are working on", "we are
testing", "we have not proven".

Never pose the open question as a cost comparison where our side is obviously heavier. A
daemon is more work than a form field. The honest question is which work moved.

When unsure whether something exists, say what has not been designed yet.

## Vocabulary

Use these words rather than synonyms, so one post connects to the next: manifest, discovery,
capability, session, caller, business, directory, conformance, level. "Front door" is the
short name for the whole arrangement; "daemon" is the implementation's process, not the
standard.
