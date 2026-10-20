# Hermes × n8n — Lab Skills & Agent Bootstrapping Prompt

Two battle-tested Hermes skills for learning **n8n by doing**, plus a ready-to-paste
prompt that gets any Hermes instance comfortable with n8n through a supervised
practice ladder (all workflows built are sandbox-prefixed, never activated, never
touch real data or credentials).

This is the exact method that took a fresh Hermes from zero to: expressions, loops,
error branches, sub-workflow libraries, webhook→dedupe→HTTP pipelines, workspace
error alarms, and local-LLM agent/capstone workflows — with every doc-vs-reality
gap caught by execution evidence, not assumed.

## What's in this repo

```
skills/n8n-lessons-learned/        # empirical gotchas: where n8n docs lie and what
                                   # actually happens at runtime (verified findings)
skills/n8n-self-study-curriculum/  # distilled learning roadmap + course digests +
                                   # the 5-step practice ladder this repo automates
support/mock_enrich.py             # zero-dependency fake "lead enrichment" API used
                                   # by the webhook pipeline lab (run anywhere, port 8899)
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

## Install

1. **Official n8n skills** (the how-to-build layer) — from
   [n8n-io/skills](https://github.com/n8n-io/skills):

   ```bash
   git clone https://github.com/n8n-io/skills /tmp/n8n-skills
   cp -r /tmp/n8n-skills/skills/n8n-* ~/.hermes/skills/
   ```

2. **These lab skills** (the learn-by-playing + gotchas layer):

   ```bash
   git clone <this-repo> /tmp/hermes-n8n-lab-skills
   cp -r /tmp/hermes-n8n-lab-skills/skills/* ~/.hermes/skills/
   ```

3. **An n8n instance + its MCP server** (n8n ≥ the version exposing the MCP server),
   registered in Hermes config as an HTTP MCP server with your bearer token.
   Verify before starting: your Hermes should see tools like
   `create_workflow_from_code`, `validate_workflow`, `execute_workflow`,
   `get_workflow_execution`.

4. *(For the webhook pipeline lab)* start the mock API:

   ```bash
   docker run -d --name hermes-lab-mock-enrich --restart unless-stopped \
     -v $PWD/support/mock_enrich.py:/app/mock_enrich.py:ro -p 8899:8899 \
     python:3-alpine python /app/mock_enrich.py
   ```

## The bootstrapping prompt

Paste everything in the block below to your Hermes. It contains its own safety
rails — keep them.

```text
You have the n8n skills installed (the official n8n-*-official set, plus
n8n-lessons-learned and n8n-self-study-curriculum) and the n8n MCP server
connected. Your mission: get comfortable with n8n by practicing, in this order.

Rules (strict):
- Prefix every workflow you create with "HERMES-LAB - ".
- Create workflows INACTIVE only. Never activate anything — with ONE exception:
  a workspace Error Trigger workflow may stay active (that is the only state in
  which an alarm can ring). Justify any exception in your final report.
- Never edit or delete workflows that don't start with "HERMES-LAB - ".
- Never ask for, store, invent, or bind credentials. If a node needs one, note
  it in the report and move on. Exception: if the human hands you a credential
  they created, you may bind it via the MCP and run the lab for real.
- No emails, messages, or external API calls with real data. Use the mock
  enrichment API (port 8899) or public echo endpoints with sample data.
- Every "it works" claim must cite an execution id and the runData field that
  proves it. No evidence, no claim.

Process — build the ladder, validating and running each step before the next:
1. FOUNDATION
   a. Manual trigger + Set node + expressions (ternaries, Luxon dates, node refs)
   b. Loops: Code node emitting sample items, per-item iteration, a real
      splitInBatches with nextBatch/onDone, aggregate on the done branch
   c. Error handling: per-item validator with onError continueErrorOutput wired
      to a Quarantine node; read error fields shape-agnostically
   d. Sub-workflows: a parent calling an INACTIVE sub via typed workflowInputs;
      then a shared sub called by TWO parents (once-mode and each-mode)
2. INTERMEDIATE
   e. Webhook pipeline: POST intake -> Split Out -> normalize -> Remove Duplicates
      -> HTTP Request enrichment (per-item query param, onError continueErrorOutput
      -> quarantine on non-2xx) -> Merge append
   f. Workspace error alarm: an Error Trigger workflow (stay ACTIVE) attached via
      the errorWorkflow setting to a victim workflow ending in Stop And Error.
      Prove both halves: a manual failure must NOT fire the alarm; a production
      run failure MUST fire it within ~50ms. Note: the alarm workflow must be
      published before the setting accepts it, and a Manual Trigger alone cannot
      be published — temporarily swap in a webhook trigger, then restore.
3. AI (only if the human confirms a local model is available, e.g. Ollama)
   g. AI Agent with a tool (e.g. Calculator) answering an arithmetic question;
      verify the tool was actually used via the run's subNodeExecutionData trace.
      Model name/serve state is the human's environment — test reachability from
      the n8n container yourself before blaming the node.
   h. Capstone: one source article -> 3 chained LLM calls (tweet with exact
      hashtag count, no-greeting email, N headlines) -> shaper -> a guard node
      that THROWS when all outputs are empty (defeat the Continue-on-Fail
      silent-success trap; prove it both red with a bogus model name and green
      with the real one).

Loop discipline:
- Read n8n-lessons-learned FIRST for each area; read the matching
  n8n-*-official skill for patterns. Before submitting SDK builder code,
  brace-balance it with a quick script — parser errors are cheap to prevent.
- Whenever reality disagrees with the docs, patch n8n-lessons-learned with the
  verified finding (what the docs say, what actually happens, the evidence).
- Finish with a report: per-lab run ids + proof fields, failures and fixes,
  skills that mattered, and a cleanup list (containers, daemons, models, scratch
  files) marked for the human's verdict — never delete anything unasked.
```

## Definition of done

A run of this prompt is complete when every ladder step has a successful
execution (verified via `get_workflow_execution` runData, not just `status`), the
alarm lab has its red/green contrast pair, the AI labs show real model traces or a
documented human-environment blocker, and `n8n-lessons-learned` came out richer
than it went in.

## Safety notes

- Everything built here is prefixed, inactive, and disposable; deletion order:
  HERMES-LAB workflows → mock container → any started daemons.
- The mock API and all sample data are fictional. The skills reference no
  credentials, tokens, hostnames, or personal data.
