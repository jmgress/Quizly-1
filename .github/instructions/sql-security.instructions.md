---
applyTo: '**/database*.py'
description: 'Security guardrails for database access code.'
---

# SQL Security Rules

This file touches the database. Enforce these rules strictly:

- **Always** use parameterized queries with `?` placeholders and a params tuple.
- **Never** build SQL with f-strings, `%` formatting, `.format()`, or string concatenation of user input.
- Do not accept dynamic table or column names from user input. If dynamic identifiers are unavoidable, validate them against a fixed allowlist.
- Validate and constrain inputs (types, ranges, lengths) at the function boundary before they reach a query.
- Use a `try/finally` (or context manager) to ensure connections/cursors are closed even on error.
- Never expose raw SQL errors or database paths in responses or logs shown to users.

## Example
```python
# Correct — parameterized
cursor.execute("SELECT * FROM questions WHERE category = ?", (category,))

# Forbidden — string interpolation (SQL injection risk)
cursor.execute(f"SELECT * FROM questions WHERE category = '{category}'")
```
