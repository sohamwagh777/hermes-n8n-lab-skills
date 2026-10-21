# Hermes × n8n — The Warm-Up

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![secret-scan](https://github.com/sohamwagh777/hermes-n8n-lab-skills/actions/workflows/secret-scan.yml/badge.svg)](https://github.com/sohamwagh777/hermes-n8n-lab-skills/actions/workflows/secret-scan.yml)

**The n8n warm-up for Hermes agents** — a prompt-skill + practice gym so any
Hermes gets comfortable with n8n before it ever touches a real workflow. Two
battle-tested skills, the 13 practice workflows from a real supervised run
(import them, don't build them from scratch), a one-command sandbox, and a
ready-to-paste prompt that runs your agent through a supervised practice ladder
(all workflows built are sandbox-prefixed, never activated, never touch real
data or credentials).

This is the exact method that took a fresh Hermes from zero to: expressions,
loops, error branches, sub-workflow libraries, webhook→dedupe→HTTP pipelines,
workspace error alarms, and local-LLM agent/capstone workflows — with every
doc-vs-reality gap caught by execution evidence, not assumed.

## What's in this repo

```
skills/n8n-lessons-learned/        # empirical gotchas: where n8n docs lie and what
                                   # actually happens at runtime (verified findings)
skills/n8n-self-study-curriculum/  # distilled learning roadmap + course digests +
                                   # the 5-step practice ladder this repo automates
labs/*.json                        # the 13 HERMES-LAB workflows, credential-stripped,
                                   # import-ready (verified: re-imported into a live
                                   # n8n before publishing)
prompts/n8n-play.md                # the bootstrapping prompt, versioned separately
docs/TROUBLESHOOTING.md            # the doc-lies FAQ, in plain English
support/mock_enrich.py             # zero-dependency fake "lead enrichment" API used
                                   # by the webhook pipeline lab (port 8899)
support/report-template.md         # the evidence-or-no-claim report format
support/example-report.md          # an anonymized real report, as the quality bar
docker-compose.yml                 # one-command sandbox: n8n + mock API
SECURITY.md                        # the no-secrets policy (CI-enforced via gitleaks)
```

`n8n-lessons-learned` is the crown jewel — findings like:
- the Ollama chat node marks its credential "optional" but throws at runtime without one
- Error Trigger payload fields live at `execution.error.message` / `workflow.name`,
  not where the docs suggest
- per-node `settings` are silently dropped when creating workflows from SDK code
- error workflows can only be attached after being published, and only fire on
  production runs (so manual "tests" silently prove nothing)
- Continue-on-Fail turns dead-model runs into green runs with empty output — the
  silent-success trap, and the guard pattern that fixes it

## Quick start — the whole sandbox in one command

```bash
git clone https://github.com/sohamwagh777/hermes-n8n-lab-skills
cd hermes-n8n-lab-skills
docker compose up -d
```

- n8n UI: http://localhost:5678 (create a local owner account on first visit)
- mock API: `curl "http://localhost:8899/enrich?email=ada@acme.com"`
- wipe everything: `docker compose down -v`

## Import the labs (skip the building, keep the learning)

`labs/` holds all 13 workflows from a completed supervised run, with credential
bindings and every instance-specific identifier stripped. In the n8n UI:
**Workflows → ⋯ → Import from File**, one file per lab. Suggested order:

| File | Teaches |
|------|---------|
| 01-manual-set-expressions | expressions: ternaries, Luxon dates, node refs |
| 02-loops-code-transform | Code nodes, per-item iteration, splitInBatches + aggregate |
| 03-error-branch-handling | onError continueErrorOutput → Quarantine, error-field shapes |
| 04-parent-calls-sub + 04-sub-calc-stats | sub-workflows: typed inputs, return contracts |
| 05-ai-agent-ollama | AI Agent + Calculator tool on a local model |
| 06-webhook-dedupe-enrich | webhook → split → dedupe → HTTP enrich → merge |
| 07-sub-format-card + 07A + 07B | one shared sub called by two parents (each/once) |
| 08-victim-failing + 08-error-watcher | production-only error alarms, red/green proof |
| 09-ai-repurposer | 3 chained LLM calls + empty-output guard |

Two one-minute re-binds after importing (workflow ids are instance-specific,
so the shipped JSON points nowhere on purpose):

- **Labs 04 / 07A / 07B**: open the `Call Stats Sub` / `Card Each` / `Card Once`
  node and pick your imported sub-workflow (names are kept as hints).
- **Lab 08**: in the victim workflow's Settings, set *Error Workflow* to your
  imported watcher. Remember: the watcher must be **published** first
  (`docs/TROUBLESHOOTING.md`).

Labs 05 and 09 need an **Ollama credential** you create yourself (UI →
Credentials → Ollama, Base URL `http://host.docker.internal:11434`) — the
imported JSON deliberately carries none.

## Install the skills

1. **Official n8n skills** (the how-to-build layer) — from
   [n8n-io/skills](https://github.com/n8n-io/skills):

   ```bash
   git clone https://github.com/n8n-io/skills /tmp/n8n-skills
   cp -r /tmp/n8n-skills/skills/n8n-* ~/.hermes/skills/
   ```

2. **These lab skills** (the learn-by-playing + gotchas layer):

   ```bash
   git clone https://github.com/sohamwagh777/hermes-n8n-lab-skills /tmp/hermes-n8n-lab-skills
   cp -r /tmp/hermes-n8n-lab-skills/skills/* ~/.hermes/skills/
   ```

3. **An n8n instance + its MCP server** (n8n ≥ the version exposing the MCP
   server), registered in Hermes config as an HTTP MCP server with your bearer
   token. Verify before starting: your Hermes should see tools like
   `create_workflow_from_code`, `validate_workflow`, `execute_workflow`,
   `get_workflow_execution`.

## The bootstrapping prompt

It lives in [`prompts/n8n-play.md`](prompts/n8n-play.md) — paste it to your
Hermes and it will run the full ladder (or import the labs above and verify
them). It carries its own safety rails — keep them.

## Environment used in the reference run

The findings, labs, and prompt were earned on this stack — reproduce it or
swap equivalents:

- **n8n**: official Docker image on a bridge network (the `docker-compose.yml`
  above matches). The MCP server is exposed by n8n at `/mcp-server/http` and
  registered in Hermes as an HTTP MCP server with a bearer token.
- **LLM**: Ollama running on the **host** (not in the compose file), serving a
  small model (`bonsai-2:4b`). Two quirks that cost real debugging time and are
  documented in `docs/TROUBLESHOOTING.md`: it is a *reasoning* model, so AI
  nodes need `think: false` and `numPredict >= 1024` or answers come back empty;
  and `keepAlive: 30m` avoids ~3 s cold starts per call.
- **Host ↔ container networking**: the n8n container cannot use `localhost` for
  host services — the Ollama credential Base URL and the mock-API URL both use
  `http://host.docker.internal:<port>` (on Linux this needs
  `host.docker.internal:host-gateway`, which compose already sets).
- **Mock enrichment API**: the `mock-enrich` service from compose, on port 8899
  — fictional data, deterministic by email domain.
- **Credentials**: created by the human in the n8n UI (the Ollama one); the
  agent binds but never creates or reads them.

Your agent will need equivalents (any local or remote OpenAI-compatible model
works for the AI labs); nothing above is required by name.

## Definition of done

A run of the prompt is complete when every ladder step has a successful
execution (verified via `get_workflow_execution` runData, not just `status`), the
alarm lab has its red/green contrast pair, the AI labs show real model traces or a
documented human-environment blocker, and `n8n-lessons-learned` came out richer
than it went in.

## Safety & security notes

- Everything built by the prompt is prefixed, inactive, and disposable;
  deletion order: HERMES-LAB workflows → mock container → any started daemons.
- The mock API and all sample data are fictional. No skill, lab, prompt, or
  example in this repo contains credentials, tokens, hostnames, or personal
  data — and [gitleaks runs on every push](.github/workflows/secret-scan.yml)
  to keep it that way. See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) — so genuinely, not "all rights reserved" by accident.
