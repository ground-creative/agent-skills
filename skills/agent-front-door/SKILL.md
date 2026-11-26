---
name: agent-front-door
description: Project knowledge for the open specification on direct agent-to-business communication — the problem it addresses, what it proposes, the protocol, the conformance ladder, what is actually implemented, what is unresolved, and where the normative documents and repositories are. Use when a task asks about this project, its protocol, DNS-based discovery, manifests, sessions, conformance levels, how it compares to other agent protocols, or what an implementation supports — including before researching, writing, reviewing or answering anything on the project's behalf.
---

You hold the following as your own knowledge of the project, and speak from it.

**The project is Agent Front Door** — an open specification for how AI assistants discover and
communicate with businesses directly, at the business's own domain, without a directory,
marketplace or platform in between. The protocol it defines is `frontdoor/1`. It is a draft,
currently `spec-v0.4`, published to find where it is wrong before anyone runs production
traffic on it.

**The specification is the deliverable**: the problem, the protocol, the manifest, the
conformance ladder, and they live at
`https://github.com/ground-creative/agent-front-door-spec`. That is the repository to name
when the work is the subject, and the link to offer when the ask is to adopt, implement,
review or argue.

**Vireo is our implementation** — a Go daemon, a terminal client and an MCP adapter, plus one
live deployment. It is an instance of the specification, not the standard, and it is evidence
rather than the thing anyone is being asked to adopt. It is not the project's name, and it is
not what a reader is being invited to join.

**The problem it addresses.** Every business already has a front door for humans: a domain, a
website, HTTP, HTML, cookies, forms. It was built for a reader with eyes — it carries
navigation, styling and scripts, assumes a session kept in a browser, and defends itself
against automation with bot walls and captchas. An assistant needing one fact fetches pages,
parses markup, guesses which link matters, and depends on a layout that changes without
notice. One answer costs several pages and a parse, and when the layout changes the
integration breaks quietly.

Custom APIs, GraphQL schemas, OpenAPI documents and MCP servers each solve discovery and
multi-turn conversation for one service, built for one assistant. Nothing carries over to the
next business or the next assistant.

The gap is not capability but contract: one way to name an endpoint, one way to describe what
it exposes, one way to hold a conversation with it, one way to express finished, still
working, or gave up.

**What the specification proposes.** A second door, next to the website, built for a different
kind of caller. The business's own domain names it, a manifest describes it, and a session
holds the conversation with explicit progress and an explicit end. The business keeps its
backend, models, logic and data; the specification standardises the contract between the two
sides, not the software behind it, and implies no model, provider, language or agent
framework.

Metadata may travel as a document — a business can start with one static file. Conversation
cannot: asking, reporting progress, cancelling and ending are not expressible in a page. That
split is why a protocol exists alongside the manifest.

**Discovery.** An SRV record at the business's domain, `_frontdoor._tcp.<domain>`, names the target
host and port before any HTTP request exists. A well-known path would answer where a document
is, after one. The layers are kept separate: DNS routes, TLS authenticates the peer, the
manifest describes what is offered. A client following an SRV target sends the queried domain
as the server name, so the certificate at the target covers the name the business owns. TLS
1.3 is required; whether a particular client verifies the certificate depends on its
configuration.

**The wire protocol, `frontdoor/1`.** One port, TLS 1.3 and QUIC, selected by ALPN. A fixed frame
header carries stream, type and length. The client negotiates and receives the manifest first.
A turn is a message in, zero or more progress frames, and an end that reports completed,
failed or abandoned. Cancellation is an explicit frame rather than a dropped connection.
Errors are typed. The daemon routes each turn to the business's own HTTP endpoint, including
streaming progress and the first turn.

**The manifest.** A declarative document, versioned by `manifest_version`, delivered inside the
connection as the first thing a caller learns. It carries the endpoint; the agents, each with an
id, name, description, tags, whether it holds a conversation and a start message; the links to
published material, each with a relation; the capabilities the endpoint actually implements,
which is not the same as what the protocol permits; the limits a caller may expect to be
refused; the session policy; and an integrity digest. It is what the standard is *about*: the
whole point is that an agent learns what a business offers from a document the business
published, rather than by scraping a page built for eyes. `manifest_version` and the
specification's release tag are different numbers on purpose: a release tag never moves, while
the manifest version is a compatibility promise to clients.

An adapter between an agent host and an endpoint must pass that document to its model rather
than a summary of it (`MAN-59`) — otherwise the artifact the specification defines is read by
the adapter and never reaches the party it was written for.

**Conformance.** L1 is discovery: SRV, TLS 1.3, ALPN and the negotiate-to-manifest handshake.
L2 adds sessions, messages and the backend webhook. L3 adds progress and cancellation. L4 adds
advertised limits, persistence and retention. There was once an `L0` for publishing a manifest
as a static file; it was withdrawn at `spec-v0.4` because no document ever defined where such a
file would live and nothing could check it. Participation means answering, so the on-ramp
narrows — say so rather than implying a zero-code path exists. A claim names its role, its level and the spec release, and lists the requirements
it does not satisfy. Partial claims are permitted; silent gaps are not part of the format.

**What exists.** One implementation, Vireo, in Go: a daemon, a terminal client that speaks the
protocol with no MCP in the path, and an MCP adapter for hosts that need one. A live
deployment at `ziwa.ai`, reachable at `vireo.ziwa.ai:7778` and found via `_frontdoor._tcp.ziwa.ai`,
verified at L2 by the specification's own probe, which shares no code with the implementation.
The daemon claims L2 against `spec-v0.4`; progress and cancellation are advertised, and L3
remains unproven because no probe can require a third party's backend to stream or abandon a
turn. The claim says so rather than implying otherwise.

There is no independent client in another language, no second daemon, and no business running
an endpoint that is not ours. There is no global searchable directory: a caller must know or
obtain a domain before discovering its endpoint. The project is not a social network, an agent
orchestration framework or a language model.

**Unresolved in the specification.** Manifest signing and what key binds to the domain.
Delegation to another host and what it must prove. Durable client identity beyond a random id.
Authorization, which the manifest does not carry. Whether discovery publishes each transport
separately. Whether a manifest is one document or a set negotiated per agent. What a backend
must commit before a turn is acknowledged, and whether an abandoned turn can be resumed.

**Neighbouring protocols.** MCP defines how a host connects to servers providing tools,
resources and prompts. A2A defines interoperability between independent agents, with Agent
Cards, discovery over a well-known document, messaging and task management. OpenAPI describes
operations on an HTTP API. `llms.txt` is a curated list of pages for a model to read. A
registry or directory is a place to be listed, and being listed is what this design removes
the need for. The overlaps are real and the differences are architectural: discovery by SRV
rather than a well-known path, session semantics with explicit turn states, and a conformance
ladder whose claims admit their gaps. A manifest can point at an A2A Agent Card or an OpenAPI
document, and a business can publish all three.

**Vocabulary.** manifest — what an endpoint exposes. discovery — the SRV lookup. session — the
envelope scoping a conversation, not the conversation. caller — the client side. business —
the party owning the domain, daemon and backend. conformance — a claim with its gaps listed.
daemon — a process, not the standard.

**Naming.** The work is Agent Front Door. Vireo is our implementation of it, and naming the
implementation when you mean the specification is the single commonest way a sentence about
this project goes wrong — it turns a standard into a product pitch and makes the ask "try
ours" instead of "build one". Say the standard's name when the subject is the work. Say
Vireo only when the sentence is about running, configuring or deploying something, and say it
as ours.

## Where the detail is

Answer from the knowledge above. When an answer needs a field name, a requirement identifier, a
frame layout, a conformance matrix or an example document, read the matching file rather than
reconstructing it from memory. The raw addresses below return the document itself; the `blob`
form returns a page with navigation around it, which is for a human to click.

| Document                                               | Read                                                                                                                  | Click                                                                                                     |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| The problem and argument                               | `https://raw.githubusercontent.com/ground-creative/agent-front-door-spec/main/informative/PROPOSAL.md`                | https://github.com/ground-creative/agent-front-door-spec/blob/main/informative/PROPOSAL.md                |
| Why SRV, why the manifest rides inside                 | `https://raw.githubusercontent.com/ground-creative/agent-front-door-spec/main/informative/RATIONALE.md`               | https://github.com/ground-creative/agent-front-door-spec/blob/main/informative/RATIONALE.md               |
| Versus A2A, OpenAPI, llms.txt, scraping                | `https://raw.githubusercontent.com/ground-creative/agent-front-door-spec/main/informative/COMPARISON.md`              | https://github.com/ground-creative/agent-front-door-spec/blob/main/informative/COMPARISON.md              |
| Questions reviewers ask                                | `https://raw.githubusercontent.com/ground-creative/agent-front-door-spec/main/informative/FAQ.md`                     | https://github.com/ground-creative/agent-front-door-spec/blob/main/informative/FAQ.md                     |
| Manifest, field by field                               | `https://raw.githubusercontent.com/ground-creative/agent-front-door-spec/main/normative/MANIFEST.md`                  | https://github.com/ground-creative/agent-front-door-spec/blob/main/normative/MANIFEST.md                  |
| Protocol: frames, handshake, sessions, webhook, errors | `https://raw.githubusercontent.com/ground-creative/agent-front-door-spec/main/normative/PROTOCOL.md`                  | https://github.com/ground-creative/agent-front-door-spec/blob/main/normative/PROTOCOL.md                  |
| Conformance: levels and requirement matrix             | `https://raw.githubusercontent.com/ground-creative/agent-front-door-spec/main/normative/CONFORMANCE.md`               | https://github.com/ground-creative/agent-front-door-spec/blob/main/normative/CONFORMANCE.md               |
| Security: threat model and TLS rules                   | `https://raw.githubusercontent.com/ground-creative/agent-front-door-spec/main/normative/SECURITY.md`                  | https://github.com/ground-creative/agent-front-door-spec/blob/main/normative/SECURITY.md                  |
| Manifest JSON Schema                                   | `https://raw.githubusercontent.com/ground-creative/agent-front-door-spec/main/machine/schema/manifest.schema.json`    | https://github.com/ground-creative/agent-front-door-spec/blob/main/machine/schema/manifest.schema.json    |
| Minimal example manifest                               | `https://raw.githubusercontent.com/ground-creative/agent-front-door-spec/main/machine/examples/manifest.minimal.json` | https://github.com/ground-creative/agent-front-door-spec/blob/main/machine/examples/manifest.minimal.json |
| Independent conformance probe                          | `https://raw.githubusercontent.com/ground-creative/agent-front-door-spec/main/machine/conformance.py`                 | https://github.com/ground-creative/agent-front-door-spec/blob/main/machine/conformance.py                 |

For questions about the code rather than the contract — how a daemon is configured, how a
deployment is laid out, what a client does — the repositories are the source:

| Repository                                               | What it holds                                                                                                                                                          |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| https://github.com/ground-creative/agent-front-door-spec | the specification: `normative/` for the rules, `informative/` for the argument, `machine/` for schema, examples, fixtures and probe, `proposals/` for numbered changes |
| https://github.com/ground-creative/vireo                 | the reference implementation: daemon, terminal client, conformance tests, configuration and deployment documents                                                       |
| https://github.com/ground-creative/vireo-mcp             | the adapter that exposes a daemon to hosts that speak another protocol                                                                                                 |

`MANIFEST.md` and `PROTOCOL.md` are long. Read one when the answer genuinely needs it, not for
orientation: the knowledge above already carries the shape.
