# Agent Skills

A **collection** of portable skills for our agents, in the
[Agent Skills](https://agentskills.io) format: one folder per skill, a `SKILL.md`
with YAML frontmatter, Markdown instructions, and optional `scripts/`,
`references/` and `assets/`.

A skill is not a prompt. Prompts are per-conversation; a skill is versioned,
validated, loadable by many agents, and loaded only when a task matches its
description. Invariants live in the skill; the specific task stays in the agent's
prompt.

## Catalog

| Skill               | What it is for                                                                                                                                        |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `moltbook-activity` | reading what happened on our Moltbook posts — who replied, what they are building, what is still unanswered — and deciding what deserves attention next |
| `web-access`        | getting information off the open web — a page read, a site walked for its own services and terms, a question answered from sources — and finishing it |

The catalog is the human index; each skill's frontmatter `description` is the
machine index. What you install is one folder under `skills/` — everything else
in this repository is for the people maintaining it, see
[CONTRIBUTING.md](CONTRIBUTING.md).

## Install

### 1. Get the repository

```bash
git clone https://github.com/ground-creative/agent-skills.git
cd agent-skills
```

Without git, download
`https://github.com/ground-creative/agent-skills/archive/refs/heads/main.tar.gz`
and unpack it. Every command below is relative to that checkout, so `cd` in first.

### 2. Put the skill where a host looks

One skill folder works on every host that supports the Agent Skills format. How
it gets there differs, because some hosts read a directory and others take an
upload.

| Host              | Reads                                                                           | Install                                                      |
| ----------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| VS Code (Copilot) | `~/.agents/skills/<name>/SKILL.md`                                              | `python3 tools/install.py`                                   |
| Claude Code       | `~/.claude/skills/<name>/` (personal) or `.claude/skills/` (project, committed) | `python3 tools/install.py --target ~/.claude/skills`         |
| claude.ai         | an uploaded **zip** of the skill folder                                         | `python3 tools/package.py`, then upload `dist/<name>.zip`    |
| Claude API        | an uploaded skill, referenced by `skill_id`                                     | `python3 tools/package.py`, then `client.skills.create(...)` |
| another client    | whatever directory its own docs name, same folder shape                         | copy or symlink `skills/<name>/` there                       |

Links beat copies where the host reads a directory: this repository stays the
single source, so editing a skill here changes what the agent loads and the two
cannot drift. Claude Code follows a symlinked skill folder, so `install.py` is
safe there as well as here.

```bash
python3 tools/install.py                 # link into ~/.agents/skills
python3 tools/install.py --target ~/.claude/skills
python3 tools/install.py --check         # verify a host, change nothing
```

`--check` exits non-zero when a skill is missing or points somewhere else, which
is how you verify a host instead of assuming it.

The whole installation, if you would rather not run a script:

```bash
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/web-access" ~/.agents/skills/web-access
```

### Uploading to claude.ai or the API

Those paths do not read a directory, so the folder has to be packaged:

```bash
python3 tools/package.py            # writes dist/<name>.zip for every skill
```

The upload rules are stricter than the filesystem ones, and this is where a
"portable" skill usually stops being portable:

- `SKILL.md` at the upload root, or at the top of a single enclosing folder;
- total size under 30 MB uncompressed;
- **only the six spec fields** in the frontmatter — `name`, `description`,
  `license`, `compatibility`, `metadata`, `allowed-tools`. Claude Code accepts
  extra fields such as `disable-model-invocation`; an upload rejects them with a
  hard error instead of ignoring them. `package.py` fails on any extra field, so
  a skill that packages is a skill that uploads;
- at most 20 skills per request.

Skills uploaded through the API are **workspace-scoped**: any key with access to
the workspace can use, and delete, them. Upload through a workspace-scoped key if
that matters.

## Using a skill from an agent

A host's prompt format is the host's business — Claude Code, VS Code and others
each define their own, and none of them is the Agent Skills format. So this
repository ships skills and nothing else. An agent prompt should be three things:

1. the role, in one sentence;
2. "activate `web-access`" — the description is what does the activating;
3. the rules that are true of _this_ agent and not of every agent that reads the
   web.

Anything general belongs in the skill. If you find yourself writing the budget,
a citation rule or a failure table into a prompt, it is in the wrong file: the
skill is versioned and validated, the prompt is neither.

## Contributing

Adding, changing or validating a skill is a different job from using one, and it
has its own file: [CONTRIBUTING.md](CONTRIBUTING.md). You do not need it to
install anything.

## License

Apache-2.0. The verbatim text is in `LICENSE`; `NOTICE` carries the attribution.
