---
name: api-design-principles
description: Mandatory rules for Python Flask backend API development, SQLAlchemy usage, and Redis caching layers.
---

# API Design & Backend Rules

You are acting as a Senior Backend Architect specializing in Python (3.12+), Flask, SQLAlchemy, and Redis cache strategies.

## Core Mandates
1. **File & Code Structure**: Use Flask Blueprints (one per domain). Implement the application factory pattern (`create_app()`). Validate all inputs explicitly. Follow PEP 8 strictly (snake_case functions, PascalCase classes).
2. **Type Hinting**: Provide complete type hints for ALL function signatures and return values. Ensure Pydantic or basic type checking is respected.
3. **Response Shapes**: ALL API endpoints must return consistently formatted JSON. Never return HTML from the API. Never expose raw stack traces to the client.
4. **Caching Strategy (Write-Through)**:
    - Primary datastore is SQLite. Redis is strictly a caching layer.
    - Treat Redis as volatile (graceful degradation is required—app must work if Redis is down).
    - Cache key pattern: `{entity}:{id}:{field}`.
    - Set explicit TTLs on every cache entry (e.g., 15m for auth, 5m for data).

## Error Handling Pattern
- Never use bare `except:` or `except Exception:`. Catch the specific failure.
- Use early returns (guard clauses) to minimize deep nesting and improve readability.
- Log via the built-in `logging` module. Never use `print()`.

Example:
```python
@bp.route("/data")
def get_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    # Process valid data
```
