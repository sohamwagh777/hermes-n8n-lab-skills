# The n8n Practice-Ladder Prompt — v1

Paste everything below the divider to your Hermes. It carries its own safety
rails — keep them. Version history: v1 = the original prompt from the repo
launch (identical), versioned separately so it can evolve without churning the README.

---

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
  files) marked for the human's verdict — never delete anything unasked. Use
  support/report-template.md as the report shape.
