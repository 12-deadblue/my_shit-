---
description: Review code for security vulnerabilities before committing
---

1. Input validation check:
   - Scan all route handlers in backend/routes/ for endpoints that accept user input
   - Verify every request.get_json(), request.args, request.form has validation before use
   - Check for missing null/empty checks

2. SQL injection check:
   - Search for any raw SQL strings in backend/
   - Verify all database queries use SQLAlchemy ORM methods
   - Flag any string concatenation near database operations

3. Secret exposure check:
   - Search all files for hardcoded strings that look like keys, tokens, or passwords
   - Verify .env is in .gitignore
   - Check that no print() statements log sensitive data

4. Extension security check:
   - Verify no inline scripts in HTML files (extension/*.html)
   - Check content scripts sanitize DOM injections
   - Verify chrome.runtime.onMessage handlers validate the request.action field

5. Auth check:
   - Verify all data endpoints have @jwt_required() decorator
   - Verify admin endpoints have @admin_required decorator
   - Check rate limiting is applied to auth and payment routes

6. Report findings as a checklist per category
