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

| Skill        | What it is for                                                                                                                            |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `web-access` | getting information off the open web — a page read, a document fetched, a question answered from sources — and finishing the task with it |

Add a row here when you add a skill. The catalog is the human index; the
frontmatter `description` is the machine index.

## Layout

```
skills/
  web-access/SKILL.md       one folder per skill, folder name == frontmatter name
templates/
  skill/SKILL.md            copy this to start a new skill
tools/
  check.py                  validate every skill against the specification
  install.py                link skills into an agent's skills directory
  package.py                build the zips that claude.ai and the API require
```

Two things sit outside `skills/` on purpose:

- `templates/` is not a skill, and the validator would rightly reject a skill
  whose name is `skill-name`.
- `tools/` is repository maintenance. Nothing in it is loaded by an agent.

That separation is not cosmetic. The specification reserves `scripts/` **inside**
a skill for code the agent runs while doing the task —
`skills/<name>/scripts/fetch.py` is part of the skill and ships in the archive.
Repository tooling under the same name would make the two indistinguishable, so
tooling lives in `tools/` and `scripts/` means one thing only: agent-executed
code belonging to a skill.

## Add a skill

```bash
cp -r templates/skill skills/<name>
```

Then:

1. Set `name` in the frontmatter to **exactly** `<name>`. This is the rule people
   miss, and the validator enforces it.
2. Write the description as "what it does **and when to use it**". That sentence
   is the only thing loaded before activation, so it does the entire job of
   matching a task to a skill.
3. Put invariants in the skill body; keep the agent's prompt down to role plus
   activation.
4. If the body passes 500 lines, move detail into `references/` and link it.
5. Add a row to the catalog, run `python3 tools/check.py skills`, commit.

## Validate

```bash
pip install pyyaml
python3 tools/check.py skills
```

Checks what is easy to get wrong and expensive to discover late:

- frontmatter exists, parses, and carries `name` and `description`;
- `name` is lowercase words joined by single hyphens, at most 64 characters, and
  **matches its directory name**;
- `description` is present, at most 1024 characters, and says when to use the
  skill, not only what it does;
- no XML tags in the frontmatter;
- the body stays under 500 lines;
- every relative Markdown link resolves to a file in the skill.

Errors fail the run (and CI); warnings do not. A warning means the skill will load
but may be triggered less reliably than it should be.

## Install

One skill folder works on every host that supports the Agent Skills format. How
it gets there differs, because some hosts read a directory and others take an
upload.

| Host           | What it reads                                                            | How you install it                                             |
| -------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------- |
| this editor    | `~/.agents/skills/<name>/SKILL.md`                                       | `python3 tools/install.py`                                     |
| Claude Code    | `~/.claude/skills/` (personal) or `.claude/skills/` (project, committed) | `python3 tools/install.py --target ~/.claude/skills`           |
| claude.ai      | an uploaded **zip** of the skill folder                                  | `python3 tools/package.py`, then upload `dist/<name>.zip`      |
| Claude API     | an uploaded skill, referenced by `skill_id`                              | `python3 tools/package.py`, then `client.skills.create(...)`   |
| another client | whatever directory it documents, same folder shape                       | copy or symlink `skills/<name>/` there                         |

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

## License

Apache-2.0. The verbatim text is in `LICENSE`; `NOTICE` carries the attribution.
