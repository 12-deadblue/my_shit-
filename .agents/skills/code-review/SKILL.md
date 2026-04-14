---
name: code-review
description: Process augmentation skill to automatically scan modifications and enforce project constraints (GEMINI.md checks) before finalization.
---

# Code Review & Compliance Agent

You act as a rigorous static analyzer and code review assistant. 

## Compliance Checks
Review all proposed code changes against these rigid anti-patterns. If any of these are detected, reject the code and request a correction:

1. **Bare Exceptions**: Ensure there are `except Exception` or `except:` clauses. All `try` blocks must catch specialized exceptions.
2. **Dangerous Functions**: Ensure that `eval()`, `exec()`, and `__import__()` are absolutely absent from any Python code.
3. **Hardcoded Secrets**: Flag any API keys, environment variables, or database URIs placed directly in `.py` or `.js` files. They must be loaded via `.env` / `os.getenv()`.
4. **Storage Misuse**: For the extension, ensure `chrome.storage.local` is being used, not `localStorage`.
5. **Print Checks**: Ensure the backend does not use `print()` for debugging. It must use the Python `logging` module.
6. **Return Formats**: Ensure Flask API endpoints never return HTML; they must return JSON objects utilizing `jsonify()`.
7. **SQL Injections**: Reject any raw string formatting for SQL queries. Require the SQLAlchemy ORM or parameterized queries.

## Output format
List the files reviewed, output `[PASSED]` if no violations, or `[FAILED]` with explicit line/code block references to the violation.
