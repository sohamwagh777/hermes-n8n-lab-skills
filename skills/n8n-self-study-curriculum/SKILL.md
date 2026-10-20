---
name: n8n-self-study-curriculum
description: Use when learning n8n or planning what to study next.
version: 1.0.0
author: Rishh (Hermes)
license: MIT
metadata:
  hermes:
    tags: [n8n, learning, curriculum, automation]
    related_skills: [n8n-lessons-learned, using-n8n-skills-official, n8n-workflow-lifecycle-official]
---

# n8n Self-Study Curriculum

## When to Use

The user asks about learning n8n, "what next in n8n", practice projects, or references the
KDnuggets roadmap / GenAI Unplugged Zero-to-Hero course. Complements `n8n-*-official` skills
(those = how to build; this = what to learn, in what order, plus distilled course takeaways).

## Sources (full text read 2026-10-20)
- KDnuggets "Automations with n8n: A Self-Study Roadmap" (Vinod Chugani, Aug 2025): kdnuggets.com/automations-with-n8n-a-self-study-roadmap
- GenAI Unplugged "FREE n8n Full Course: Zero to Hero in AI Automation" (Dheeraj Sharma, Feb 2026; 42 lessons / 47 YouTube videos): genaiunplugged.substack.com/p/free-n8n-full-course-zero-to-hero-ai-automation

## Why n8n (both sources agree)
- "nodemation" = node-based + Node.js; fair-code license; self-host free with unlimited executions.
- Pricing per workflow EXECUTION (not per step): a 50-step workflow costs the same as 5-step. Zapier = per task, Make = per operation.
- 400-500+ integrations, LangChain AI nodes, Code nodes (JS/Python), full REST API, Git integration.
- Progression: visual → logic/conditions → custom code, same platform.

## Roadmap stages (KDnuggets)
1. FOUNDATION: official Level-1 free course (~2h, docs.n8n.io/courses/level-one/), Quickstart (docs.n8n.io/try-it-out/), beginner YouTube playlist, 4400+ templates at n8n.io/workflows. Drill JSON data flow via node I/O tabs + Set node. Projects: Sheets→email, form→Slack, scheduled daily report.
2. INTERMEDIATE: Code nodes, Error workflows, HTTP Request node + auth methods, sub-workflows (DRY). Projects: CRM lead processing, e-commerce order pipeline, multi-platform content publishing.
3. ADVANCED: self-hosting, custom nodes, direct SQL (Postgres/MySQL), LangChain multi-agent systems, Task Runners for perf. Projects: AI ticket routing, multi-source analytics, multi-agent orchestration.

## Course structure (GenAI Unplugged, 8 sections)
S1 Intro (L1-4): workflow = Trigger→Processing→Action; map the process before building; start small, test, iterate. n8n vs Zapier vs Make 15-point comparison.
S2 Getting Started (L5-11): Cloud 14-day trial / `npm install -g n8n` + `n8n start` (Node 20.19–24.x; `npx n8n` to try without install; community license unlocks history/debugging/folders) / Docker for prod (persistent volume, easy host migration). Node types: Trigger, App, Core, Cluster(AI). Data = JSON items; access via `{{ $json.field }}`; binary handled separately.
S3 Deep Dive (L12-30): IF (binary branch) + Switch (multi); Merge modes = Append / Combine by Position / Combine by Field / Multiplex; Set (Edit Fields) add/rename/clean; Aggregate many→one (sum/count/concat/group-by); Remove Duplicates (by field, keep first/last); Webhook node = unique URL per workflow (Google Forms needs Apps Script); Loop Over Items = batching + rate-limit waits + early exit; optimize: filter early, minimize nodes, cache, monitor exec time; expressions `$json.x`, `$node["Name"].json.x`, `$now`/`$today`; Code node: `$input.all()`, must return item array, self-hosted can install libs; ITEM LINKING: paired items preserve lineage across splits/merges — Aggregate and Code BREAK pairing; HTTP node = any REST API (headers/auth/body/response parsing); Pin Data freezes outputs for fast dev + edge-case edits; mock data in Manual Trigger; sub-workflows via Execute Workflow: clear I/O, descriptive names, keep inactive copies as versions; binary: read Drive/S3/FTP/HTTP, convert formats, ZIP/extract, write back/attach.
S4 Errors (L31-34): "Continue on Fail" + configurable retries; design idempotent ops; execution logs = per-node I/O, failed nodes red; most errors are AUTH — check credentials/re-OAuth first; Error Trigger workflow = one workspace-wide failure watcher → Slack/email alert; Stop And Error node for deliberate validation failures.
S5 Projects (L35-38): Gmail attachments→Drive (filter sender/type, folder by date, label+archive); lead-enrichment capstone = Capture→Enrich→Qualify→Route (Hunter.io via HTTP node, graceful fallbacks, HTML→PDF report→Drive→notify sales).
S6 AI (L39-44): OpenAI node, prompt crafting, parse structured responses; AI email assistant (summarize/draft/route by sentiment); AI blog writer (outline→sections→SEO→Notion; chain multiple AI calls for long content); repurpose 1 blog→4 social formats; resume screening (PDF extract→AI parse→score→rank→route + notify).
S7 Final (L45): faceless YouTube channel autopilot (script→assets→thumbnail→multi-platform schedule).
S8 Enterprise (L46-47): roles Owner/Admin/Member; credential sharing without exposing keys; n8n REST API (activate/deactivate, fetch executions) via HTTP node or n8n-api node; Execution Data node = custom fields to filter thousands of executions; Git version control dev/prod + rollbacks; Global Variables; external secrets (HashiCorp Vault / AWS Secrets Manager / Azure Key Vault); log streaming to central monitoring.

## Best practices distilled
- Descriptive node names ("Format Date for Airtable"); align + color-code canvas.
- Credentials ONLY via credential manager / env vars — never hardcoded.
- "Execute Node Once"/Test Step before full runs; never test on production data.
- Don't over-automate what is faster manually; modularize instead of sprawling canvases.
- Debug order: credentials → data-format match at node boundary → isolate failing node → temp logging nodes.

## Practice ladder (sequential, builds on this instance's HERMES-LAB setup)
1. Scheduled Sheets→email digest (foundation).
2. Webhook form → Remove Duplicates → HTTP-node enrich → Slack (Merge + auth practice).
3. Sub-workflow library: "Notify Slack", "Enrich Contact" called by 2+ parents (DRY).
4. Workspace-wide Error Trigger → alert with execution link.
5. AI content-repurposing capstone (1 input → N platform outputs) with Continue-on-Fail + pinned test data.

## Fetching pitfalls
- KDnuggets blocks curl (returns ~1.1KB JS-wall stub) → prefix URL with https://r.jina.ai/ and web_extract.
- Substack: curl + regex-strip `<article>` block works fine (419KB page → ~31KB text).
- Course videos are YouTube-only; the takeaways above are the text digest — no need to watch to advise.
