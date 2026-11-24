# Contributing a skill

The [README](README.md) is for people who want to **use** a skill. This file is
for people adding one. If you are here to install a skill somewhere, you want
the README — nothing in this file is required to use one.

## Layout

```
skills/
  web-access/SKILL.md                    one folder per skill, folder name == frontmatter name
  agent-front-door/SKILL.md      project knowledge, no scripts
  moltbook-ops/SKILL.md                  the shared judgement, and which reference to open
  moltbook-ops/references/               one file per job, loaded only when that job is asked for
  moltbook-ops/scripts/                  code this skill runs while doing its job
templates/
  skill/SKILL.md                        copy this to start a new skill
  dispatch.md                           how a *calling* agent is told to ask
tools/
  check.py                              validate every skill against the specification
  install.py                            link skills into an agent's skills directory
  package.py                            build the zips that claude.ai and the API require
```

Only `skills/` is shipped. `templates/` and `tools/` exist so this repository can
be maintained, and no agent ever loads them.

`templates/dispatch.md` is the exception that proves the point: a skill instructs the
agent doing the job, and nothing can instruct the agent *asking* for it, because that
agent never loads a skill. The dispatch text is copied into the host config beside the
tool definitions, and it is the reason a caller knows what to put in a request.

The distinction matters more than it looks. The specification reserves `scripts/`
**inside** a skill for code the agent runs while doing the task —
`skills/<name>/scripts/fetch.py` is part of the skill and ships in the archive.
Repository tooling under the same name would be indistinguishable from that, so
tooling lives in `tools/` and `scripts/` means one thing only: agent-executed code
belonging to a skill.

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
5. Add a row to the catalog in the README, run the validator, commit.

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

Errors fail the run and fail CI; warnings do not. A warning means the skill will
load but may be triggered less reliably than it should be.

If you touched a skill that ships to a host which takes uploads, rebuild the
archives and confirm they still build:

```bash
python3 tools/package.py
```
