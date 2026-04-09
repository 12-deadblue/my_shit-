# My Extension — Project Rules

## Project Context
- **Backend**: Python 3.12+, Flask, SQLAlchemy, Redis
- **Frontend**: Chrome Extension (Manifest V3), vanilla JavaScript
- **Dashboard**: Single-page HTML/CSS/JS admin panel
- **Database**: SQLite (primary) + Redis (caching layer)
- **Auth**: Google OAuth 2.0
- **Payments**: Google Pay API for Web

## Directory Structure
```
extension/    → Chrome extension source files
backend/      → Flask API server
dashboard/    → Admin monitoring SPA
.agents/      → Agent workflows and skills
```

## Python Backend Rules

### Style & Standards
- Follow PEP 8. Use snake_case for functions/variables, PascalCase for classes.
- Use type hints for ALL function signatures and return values.
- Use Google-style docstrings for all public functions and classes.
- Organize imports: stdlib → third-party → local.
- Use the application factory pattern (`create_app()`).
- Organize routes using Flask Blueprints — one blueprint per domain.

### Error Handling
- Never use bare `except:` or `except Exception:`. Catch specific exceptions.
- Never expose stack traces to the client. Return JSON error responses.
- Use early returns (guard clauses) to reduce nesting.
- Log errors with Python's `logging` module, never `print()`.
- Example pattern:
```python
@bp.route("/example")
def example():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    # ... proceed with valid data
```

### Security
- NEVER hardcode secrets. Use environment variables via `.env`.
- NEVER use `eval()`, `exec()`, or `__import__()`.
- Always use SQLAlchemy ORM — never raw SQL strings.
- Validate ALL input with explicit checks before processing.
- Use parameterized queries if raw SQL is ever needed.
- Apply rate limiting to auth and payment endpoints.
- All API responses must be JSON. Never return HTML from API routes.

### Database
- SQLite is the primary store. Redis is cache only.
- Redis must degrade gracefully — app works without it (just slower).
- Use write-through caching: update DB first, then update Redis.
- All cache keys follow the pattern: `{entity}:{id}:{field}`.
- Set TTLs on all cache entries. Default: 15min for auth, 5min for data.

## Chrome Extension Rules

### Manifest V3
- Always use `manifest_version: 3`. Never use v2 features.
- Use `service_worker` for background scripts, not `persistent: true`.
- Follow principle of least privilege for permissions.
- Use `chrome.storage.local` for persistence, never `localStorage`.

### Code Style
- Use `const` and `let`. Never use `var`.
- Use `async/await` with chrome APIs, not callbacks where possible.
- Validate all messages received via `chrome.runtime.onMessage`.
- Content scripts must not assume page structure — be defensive.

### Security
- Never use inline scripts in HTML files (CSP violation).
- Validate all data received from content scripts in the background worker.
- Never inject user-generated content into the DOM without sanitizing.
- Use `chrome.alarms` instead of `setInterval` for background scheduling.

## Dashboard Rules
- Keep the dashboard as a static SPA — no build tools required.
- All data comes from the `/api/admin/` endpoints via fetch.
- Admin routes require JWT with admin role. Dashboard stores token in localStorage.
- Use CSS custom properties (variables) for theming — no inline styles.

## General Prohibitions
- Never commit `.env` files, database files, or `__pycache__/`.
- Never modify `requirements.txt` without also testing the install.
- Never change API response shapes without running `/api-change` workflow.
- Never delete files without confirming they have zero references.
- Never use `TODO` comments without linking to a tracking issue or task.

## Testing
- Backend tests go in `backend/tests/` using `pytest`.
- Test files must be named `test_*.py`.
- Each endpoint should have at least: happy path, auth failure, validation error.
- Use fixtures for database and Redis mocking.
