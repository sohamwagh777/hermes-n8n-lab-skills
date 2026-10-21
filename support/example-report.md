# Lab Run Report — Rishh (Hermes) — 2026-10-20  *(anonymized example)*

> This is the expected shape of a finished run, anonymized. Execution ids are
> shortened; real reports must include full ids so the human can re-check with
> `get_workflow_execution`.

## Ladder results

| # | Lab | Workflow id | Execution id | Status | Proof (runData field = value) |
|---|-----|-------------|--------------|--------|-------------------------------|
| 1 | Manual Set Expressions | aa11…aa11 | 312 | success | `runData["Build Record"][0].json.receiptId = "RCPT-20261020-ADA"`, tier `"VIP"` |
| 2 | Loops Code Transform | bb22…bb22 | 318 | success | loop `contextData['node:Batch 5'].processedItems = 12`; aggregate: 3 categories, revenue sum matches hand-check |
| 3 | Error Branch Handling | cc33…cc33 | 326, 329 | success | good: 3 items output(0); bad item on output(1) with `json.errorCode = "MISSING_SKU"` (run 329 after fix) |
| 4 | Parent → Sub | dd44…dd44 | 337 | success | `metadata.subExecution = {executionId: 338, workflowId: "ee55…ee55"}`; return contract consumed downstream |
| 5 | Webhook Dedupe Enrich | ff66…ff66 | 344 | success | 4 leads in → 3 enriched (1 dup removed) + 1 quarantined (`non-2xx` from mock API) |
| 6 | Error Watcher | gg77…gg77 | 351 vs 353 | red/green | manual fail → watcher run count unchanged (0); production (webhook-mode) fail → watcher run `mode:"error", status:"success"` with formatted alert |
| 7 | Sub lib (2 parents) | hh88…hh88 | 360, 362 | success | 07A each-mode: `metadata.subExecutionsCount = 2`; 07B once-mode: single `subExecution` |
| 8 | AI Agent (Ollama) | ii99…ii99 | 371 | success | `runData.Agent[0].metadata.tracing["ai.agent.tool_calls.requested"] = ["Calculator"]`, answer = 1024 |
| 9 | AI Repurposer | jj00…jj00 | 377 (green), 380 (red) | red/green | green: 3 subRun entries (3 LLM calls), tweet had exactly 2 hashtags; red: guard Code node threw `LAB-09 ALL_OUTPUTS_EMPTY` with bogus model name |

## Failures & fixes

| Lab | Symptom | Root cause | Fix | Verified by |
|-----|---------|------------|-----|-------------|
| 3 | Quarantine showed `UNKNOWN` | error output's `json.error` is a plain string, not `{message}` as docs imply | shape-agnostic expression `typeof … === 'string' ? …` | exec 329 |
| 8 | `NodeOperationError: Node does not have any credentials set` | Ollama credential is type-def "optional" but runtime-required | human created ollamaApi credential (Base URL host.docker.internal:11434), bound via setNodeCredential | exec 371 |

## Doc-vs-reality findings (fed back into n8n-lessons-learned)

- Docs: error payload at `trigger.error.message` → reality: `execution.error.message`
  (evidence: exec 353 watcher runData).
- Docs: credential optional → reality: hard runtime requirement (exec 371).

## Environment blockers

- Ollama model pull + credential creation were human-side (documented, not bypassed).

## Cleanup list (human's verdict required)

| Artifact | Kind | Remove command | Verdict |
|----------|------|----------------|---------|
| HERMES-LAB - * (13) | workflows | UI archive/delete | kept for reuse |
| hermes-lab-mock-enrich | container | docker rm -f | kept |
