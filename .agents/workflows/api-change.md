---
description: Checklist for making API endpoint changes safely
---

1. Identify all endpoints being changed (route, method, request/response shape)
2. Check if any extension JS files call the affected endpoints (search extension/ for the URL path)
3. Check if the dashboard calls the affected endpoints (search dashboard/ for the URL path)
4. If request shape changes: update all callers
5. If response shape changes: update all consumers
6. If adding a new endpoint: add it to the appropriate blueprint in backend/routes/
7. If removing an endpoint: verify zero callers exist before deleting
8. Run backend tests to verify no regressions
9. Update the API documentation in README if it exists
10. Report a summary of all changes and affected files
