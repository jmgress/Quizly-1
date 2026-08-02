---
mode: agent
description: 'Run an OWASP Top 10 security audit on the selected code and report structured findings.'
---

# Security Audit (OWASP Top 10)

Audit the selected code for security vulnerabilities against the **OWASP Top 10**. Do not modify any code — report findings only.

## Focus Areas
- Injection (SQL, command, template) — especially raw SQL in `database.py` and any string-built queries.
- Broken authentication / authorization on API and admin endpoints.
- Sensitive data exposure — API keys or secrets in logs, errors, or responses.
- Security misconfiguration (CORS, debug flags, permissive defaults).
- Path traversal — relevant to the logging system in `backend/logging_config.py`.
- Insecure dependencies.

## Output Format
For each finding, produce a row:

| Severity | OWASP Category | Location | Finding | Remediation |
|----------|----------------|----------|---------|-------------|

- **Severity**: Critical / High / Medium / Low.
- **Location**: file and line reference.
- **Remediation**: a concrete, minimal fix.

End with a one-line summary: total findings by severity. If no issues are found, say so explicitly and note what you checked.
