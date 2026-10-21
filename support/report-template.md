# Lab Run Report — <agent name> — <date>

Fill one row per lab. **A claim without an execution id and a proof field is not
a result — it is a guess.** Proof field = the exact runData path + value that
proves the lab's teaching point (see `example-report.md`).

## Ladder results

| # | Lab | Workflow id | Execution id | Status | Proof (runData field = value) |
|---|-----|-------------|--------------|--------|-------------------------------|
| 1 | Manual Set Expressions | | | | |
| 2 | Loops Code Transform | | | | |
| 3 | Error Branch Handling | | | | |
| 4 | Parent → Sub | | | | |
| 5 | Webhook Dedupe Enrich | | | | |
| 6 | Error Watcher (red/green pair) | | | | |
| 7 | Sub-workflow library (2 parents) | | | | |
| 8 | AI Agent (Ollama) | | | | |
| 9 | AI Repurposer capstone | | | | |

For the error-watcher lab you must show BOTH halves:
manual failure → watcher did NOT fire (0 new runs), production failure → watcher
fired (`mode:"error"`). One without the other proves nothing.

## Failures & fixes

| Lab | Symptom | Root cause | Fix | Verified by |
|-----|---------|------------|-----|-------------|
|     |         |            |     | execution id |

## Doc-vs-reality findings (feed these back into n8n-lessons-learned)

- What the docs said / what actually happened / evidence (execution id):

## Environment blockers

Anything that required the human (credential creation, model pull) and is
documented, not worked around.

## Cleanup list (human's verdict required — never delete unasked)

| Artifact | Kind | Remove command | Verdict |
|----------|------|----------------|---------|
| HERMES-LAB - * workflows | workflows | UI delete / archive | ☐ |
| hermes-lab-mock-enrich | container | docker rm -f | ☐ |
