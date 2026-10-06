# SECURITY.md

## Secrets
- Never commit .env or secrets.toml
- Use env vars/secret manager
- .env.example contains placeholders only

## Protections
- SSRF: validate URLs, timeouts, size limits (enrichment)
- Email injection: validate/sanitize AI outputs
- CSV injection: proper quoting in exports
- Suppression: DNC/unsubscribe enforced
- No secrets in logs/exports
- Dry-run mode prevents accidental sends
