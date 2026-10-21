# Security Policy

## Our no-secrets policy

This repo is a learning playground. It must never contain secrets, and CI
enforces it on every push and pull request (`.github/workflows/secret-scan.yml`,
gitleaks). The rules that keep it that way:

- **No credentials in the repo, ever.** Lab workflows are committed with their
  credential bindings stripped; each user creates their own credentials in their
  own n8n instance.
- **No tokens, API keys, or bearer values** in workflow JSON, prompts, examples,
  or docs — including revoked or expired ones.
- **No instance identifiers**: workflow IDs, credential IDs, owner names/emails,
  hostnames, private IPs.
- Lab sample data is fictional by design (mock enrichment API, fake leads).

## Reporting a vulnerability

If you believe you found a secret or a vulnerability in this repo:

1. Use **GitHub private vulnerability reporting** on this repo's Security tab, or
   open a private contact via the owner's GitHub profile.
2. Include the file path and commit; do not post the secret publicly in an issue.
3. If a real credential was ever committed here, treat it as compromised: revoke
   it first, then report — rotation is the fix, deletion from history is cleanup.

## Scope note

These labs automate n8n through an agent. The bootstrapping prompt
(`prompts/n8n-play.md`) carries its own safety rails (sandbox prefixes, inactive
workflows, no credential handling, evidence-or-no-claim). Run them against
throwaway instances you own — never against production n8n or real data.
