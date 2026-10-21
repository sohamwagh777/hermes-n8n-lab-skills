# Troubleshooting — the doc lies, in plain English

Every entry below was hit for real while building the HERMES-LAB series and
verified by execution evidence. If your agent "fixed" something by ignoring the
docs, it probably hit one of these. The full findings live in
`skills/n8n-lessons-learned/`; this is the user-facing FAQ.

## The AI labs error with `getaddrinfo EAI_AGAIN http`

The credential Base URL has a doubled scheme — `http://http://host...` — so the
client tries to resolve a hostname literally called `http`. The URL must have
exactly one scheme: `http://host.docker.internal:11434`.

## "My Ollama node has no credential — but the docs say it's optional"

The type definition for the Ollama chat model node marks the `ollamaApi`
credential as optional. **This is a lie.** The node throws
`NodeOperationError: Node does not have any credentials set` at runtime without
one. Create an **Ollama (ollamaApi)** credential in the n8n UI
(Base URL: `http://host.docker.internal:11434`) and bind it to the node.

## n8n can't reach Ollama on my host

n8n runs in a docker bridge network: `localhost` inside the container is the
container itself, not your machine. Use `http://host.docker.internal:11434`
(or the host's LAN IP) as the Base URL. On Linux, `host.docker.internal`
exists only if the container gets `--add-host host.docker.internal:host-gateway`
— the included `docker-compose.yml` already sets it.

## My error watcher alarm never fires

Three separate traps stack here:

1. **Error workflows only fire on PRODUCTION runs.** A manual test run that
   fails will NOT trigger the Error Trigger workflow. Test via webhook/schedule
   mode (`execute_workflow` with webhook inputs), not a manual run.
2. **The error workflow must be PUBLISHED before it can be attached** as
   `errorWorkflow` — n8n rejects with "has no published version". Published is
   its correct resting state.
3. **A Manual Trigger alone cannot be published** ("no trigger node"). Swap in
   a webhook or schedule trigger temporarily to publish it.

## The alarm fires but the alert text is empty

The Error Trigger payload lives at `execution.error.message`,
`execution.workflow-name`, etc. Paths the docs suggest — like
`execution.workflowName` or `trigger.error.message` — resolve to null/unknown.
Real shape:

```json
{ "execution": { "id": "…", "url": "…", "mode": "error",
    "lastNodeExecuted": "…", "error": { "message": "…", "node": { "name": "…" } } },
  "workflow": { "id": "…", "name": "…" } }
```

## A redacted/throwing Code node item shows `error: UNKNOWN`

The failing item's `json.error` is a **plain string**
(`"MISSING_SKU: ... [line 2]"`), not `{ message: ... }`. Read it
shape-agnostically:

```
{{ typeof $json.error === 'string' ? $json.error : ($json.error?.message ?? 'unknown') }}
```

(The validator also warns `INVALID_EXPRESSION_PATH` on `$json.error` — false
positive; the field is injected at runtime.)

## My run is green but produced nothing (silent success)

The Continue-on-Fail trap: a chain with `onError: continueRegularOutput` turns a
dead model / bad credential into a **successful execution with empty output**.
Guard every AI pipeline with a Code node that THROWS when all outputs are empty
(see lab 09's Empty-Output Guard). Prove the guard both red (bogus model name)
and green (real one).

## `triggerCount: 0` on a workflow that clearly has a trigger

`get_workflow_details` reports `triggerCount: 0` and empty `triggerInfo` even
when a manual trigger exists. Never trust those fields; check `nodes[]` or the
execution's `runtimeData.triggerNode`.

## My node settings (onError, retries) silently disappeared

When workflows are created from SDK/MCP code, node-level `settings` are dropped.
Apply them **after creation** (`setNodeSettings`), not in the build code.

## `test_workflow` can't mock my AI node

Pin-data preparation lists only trigger nodes; AI sub-nodes are skipped, so
pinned tests cannot simulate a model. The only real gate for AI workflows is a
real `execute_workflow` run with a reachable model.

## Reasoning model returns empty answers

Tiny local reasoning models (e.g. `bonsai-2:4b`) spend the token budget on
thinking tokens: with a small `num_predict` you get `done_reason=length` and
empty content. Set `think: false` and `numPredict >= 1024`, and keep the model
warm (`keepAlive: 30m`) to avoid ~3 s cold-start TTFB on every call.

## The webhook lab gets connection refused

The mock enrichment API isn't running: `docker compose up -d` (or the single
`docker run` from the README). From inside the n8n container the correct URL is
`http://host.docker.internal:8899/enrich`.
