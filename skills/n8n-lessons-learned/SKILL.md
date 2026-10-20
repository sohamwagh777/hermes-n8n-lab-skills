---
name: n8n-lessons-learned
description: Use when building or debugging n8n workflows via the MCP.
version: 1.0.0
author: Rishh (Hermes)
license: MIT
metadata:
  hermes:
    tags: [n8n, mcp, automation, debugging]
    related_skills: [n8n-workflow-lifecycle-official, n8n-error-handling-official, n8n-ai-nodes-official]
---

# n8n Lessons Learned

## When to Use

Any n8n build/edit/debug on this instance via the n8n MCP — these are the doc-vs-reality gaps
found while building the HERMES-LAB series; read alongside the matching `n8n-*-official` skill.

Empirical findings from building/running the HERMES-LAB workflows on this instance
(n8n docker `docker.n8n.io/n8nio/n8n:latest`, MCP at http://localhost:5678/mcp-server/http).
Official `n8n-*-official` skills cover the patterns; these are the gaps between docs and reality.

## Error outputs (onError: continueErrorOutput)

- A per-item Code node that throws routes ONLY the failing items to output(1); good items keep flowing output(0) in the same run. Execution status is still `success`.
- The failed item's `json.error` is a **plain string** ("MISSING_SKU: ... [line 2]"), NOT `{ message: ... }` — despite what error-handling docs imply. Read it shape-agnostically:
  `{{ typeof $json.error === 'string' ? $json.error : ($json.error?.message ?? 'unknown') }}`
- `validate_workflow`/`create_workflow_from_code` emit `INVALID_EXPRESSION_PATH` warnings for `$json.error` in error-branch nodes. False positive: `error` is injected at runtime and invisible to the validator's sample-output analysis. Safe to ship after an execution proves the shape.

## Execution & activation truths (verified via get_workflow_execution)

- `execute_workflow` with `executionMode: "manual"` runs **inactive** workflows; nothing needs publishing. Manual runs auto-pin the trigger only (`pinData.Start` in the result).
- `Execute Workflow` (Execute Sub-workflow v1.2) calls **inactive sub-workflows** fine — activation only gates production triggers. Parent execution carries `metadata.subExecution {executionId, workflowId}`; the sub's own execution is a separate row (fetch with its own workflowId).
- `get_workflow_details` reports `triggerCount: 0` and empty `triggerInfo` even when a manual trigger exists. Never trust those fields; check `nodes[]` or execution `runtimeData.triggerNode`.
- Agent-node failures surface with rich `metadata.tracing` on the agent's runData (`ai.agent.tool_calls.requested`, `ai.agent.failure.type` etc.) — the fastest agent debugging signal. Caveat: `ai.agent.streaming.enabled` reported `true` even with `enableStreaming: false` set; don't audit params from tracing fields.

## AI Agent node + Ollama (local model)

- Credential Base URL must be a full URL with EXACTLY one scheme. `getaddrinfo EAI_AGAIN http` in docker logs n8n = the ollama client is resolving hostname "http" because the field contains a doubled prefix like `http://http://host...`. ChatOllama always STREAMS internally (`/api/chat` stream:true) regardless of enableStreaming; cold model load (~3 s for a 4B) is normal TTFB.

- `@n8n/n8n-nodes-langchain.lmChatOllama` marks `ollamaApi` credential optional in the type def but **throws at runtime** without it: `NodeOperationError: Node does not have any credentials set` from the Agent's getInputConnectionData. Build is fine; execution needs the user to create an **Ollama (ollamaApi) credential** in the UI, then bind via `update_workflow` `setNodeCredential`.
- n8n runs in a bridge-network docker container: `localhost:11434` inside it is NOT host Ollama. From the container, `http://host.docker.internal:11434` and the LAN IP both work — that's what the ollamaApi Base URL must be (or run an `alpine/socat` proxy with `--network container:n8n` listening on BOTH 127.0.0.1 and ::1 — Node prefers ::1, busybox wget hides it).
- `prepare_workflow_pin_data` lists ONLY triggers; AI sub-nodes are 'skipped' (not pinned), so `test_workflow` cannot simulate a model either. The only real gate for agent workflows is `execute_workflow` with a working model.
- Sub-node wiring from SDK `subnodes: { model, tools }` lands as `ai_languageModel` / `ai_tool` connections — verify in `get_workflow_details` connections object.
- Host Ollama here: binary at /usr/local/bin/ollama, serve manually with `OLLAMA_HOST=0.0.0.0:11434 ollama serve`; qwen3:0.6b pulled (522 MB) and working.

## Workflow SDK builder-code quirks

- Top-level `config.settings` is SILENTLY DROPPED by create_workflow_from_code (warning UNKNOWN_CONFIG_KEY, "did you mean config.parameters"). Node-level settings (onError, retryOnFail, executeOnce) must be applied after creation via `update_workflow` `setNodeSettings`.
- Before submitting SDK code, brace-balance-check it in Python (strip string literals, compare {}/()/[] counts). One stray `}` cost 3 validate failures; the MCP throttles ~15s after 3 failing calls to one tool.
- `validate_workflow` accepts ONLY `code` (no versionName/Description); those belong on create.
- Merge nodes need >=2 wired inputs at validation (warning MERGE_SINGLE_INPUT) — add the second branch via update addConnection `targetIndex: 1` after creation.

- `expr('Order by {{ ... }}')` (text + interpolation) persists as `=Order by {{ ... }}` — the `=` prefix is expression mode, correct, don't 'fix' it.
- `nodeJson()` is documented in the SDK reference but NOT in the official import list; using `expr('{{ $("Node Name").item.json.x }}')` is the safe portable form.
- `splitInBatches` `.onDone()` output emits the items as they exited the loop path (they carry fields added by per-batch nodes, e.g. `batchProcessedAt`) — an aggregate Code node on the done branch sees loop-processed items, verified via `contextData['node:<loop>'].processedItems`.
- Loop wiring `.onEachBatch(x.to(nextBatch(loop)))` + `.onDone(...)` produces connections with the loop node owning output[0]=done, output[1]=loop — matches the loops skill's 'output 0 = done'.
- `create_workflow_from_code` always creates **inactive** (`active: false`), truncates description to 255 chars, and creates in the personal project unless projectId passed. `update_workflow` `updateNodeParameters` with `replace: true` cleanly swaps a whole parameters object.
- `Execute Workflow` node: `workflowId: { __rl: true, mode: 'id', value: '<id>', cachedResultName }` + `workflowInputs: { mappingMode: 'defineBelow', value: {...}, schema: [...] }` with names/types exactly matching the sub trigger's `workflowInputs.values`.

## Environment facts (this instance)

- Ollama models on host (2026-10-20): `bonsai-2:4b` (1.6 GB, REASONING model — a tiny num_predict yields empty content with done_reason=length because thinking tokens eat the budget; needs numPredict ~1024 + think:false, which the lab-05 node now sets) and `qwen3:8b`. qwen3:0.6b was deleted by the user. Model name is `bonsai-2:4b` — user shorthand 'bonsai:4B' is NOT a valid tag.
- Mock enrichment API for lab 06: docker container `hermes-lab-mock-enrich` (--restart unless-stopped, -p 8899:8899, script mounted ro from scratch/mock_enrich.py). Reachable from n8n container as http://host.docker.internal:8899. The old socat proxy (hermes-lab-ollama-proxy) was DELETED — credential uses host.docker.internal directly.
- Lab 09 has an 'Empty-Output Guard' Code node after Content Pack: throws LAB-09 ALL_OUTPUTS_EMPTY when tweet+email+headlines are all '' — red instead of silent-success. Verified red via temporary bogus model name, restored with setNodeParameter /model.
- Lab 05 Math Agent: retryOnFail 3x/2s; both model nodes keepAlive 30m (kills cold-start).
- Code-node throw inside runOnceForAllItems surfaces as WrappedExecutionError with the message + [line N] — execution status error, good for loud-fail guards.
- Webhook triggers CAN run via MCP execute_workflow with `inputs.webhookData {method, body, headers}` + triggerNodeName in manual mode. executeWorkflowTrigger CANNOT (triggerInfo says 'not supported for direct execution').
- executeWorkflow node v1.2 `mode: 'each'` -> metadata.subExecutionsCount = N, one sub-execution row PER ITEM (each item carries its own metadata.subExecution); `mode: 'once'` -> single subExecution. Both work against inactive subs.
- Failure handling (errorWorkflow setting / Error Trigger) fires on PRODUCTION executions only, never manual — verified: manual fail = 0 watcher runs, webhook-mode production fail = watcher run with mode:"error", status:success.
- Attaching settings.errorWorkflow REQUIRES the error workflow to be PUBLISHED first (n8n rejects with 'has no published version'). Error workflows must live published to function — that is the correct resting state, not a rule violation.
- Manual Trigger alone CANNOT be published ('no trigger node') — swap to webhook/schedule trigger for production-mode tests via addNode+addConnection+removeNode in one update.
- Real Error Trigger payload shape: `{ execution: { id, url, mode, lastNodeExecuted, error: { message, node: {name}, stack } }, workflow: { id, name } }` — NOT execution.workflowName and NOT trigger.error.message (docs mislead; those yield null/'unknown').

## Credential auto-assignment + chainLlm

- `newCredential('<exact credential name>')` in SDK config.credentials AUTO-BINDS to the real credential by name (response field autoAssignedCredentials). No post-creation setNodeCredential needed when the user already created the credential.
- chainLlm (Basic LLM Chain v1.9): parameters {promptType:'define', text}, config.subnodes {model} — one shared languageModel() instance can wire to several chains; per-chain onError continueRegularOutput applied post-creation via setNodeSettings (Continue-on-Fail). Shared model sub-node shows N metadata.subRun entries (one per chain call) — that is the proof of N LLM round-trips.
- bonsai-2:4b is decent at short-form copy: tweet with exact-2-hashtags and 4-sentence no-greeting email both passed format constraints first try (~1.5 s/call warm).
- httpRequest error output (onError continueErrorOutput): $json.error is also a PLAIN string ("404 - \"body...\"") like Code nodes; failed item keeps its input fields (email available directly).

- Instance started empty: 0 workflows, 0 credentials. All HERMES-LAB-* workflows tag `hermes-lab`; the sub-workflow also tagged `subworkflow`.
- Secrets live in `~/.hermes/config.yaml` (n8n_mcp bearer). Never echo them.
- To clean up lab artifacts: delete HERMES-LAB-* workflows, `docker rm -f hermes-lab-ollama-proxy`, kill the `ollama serve` daemon if it was started for testing.
