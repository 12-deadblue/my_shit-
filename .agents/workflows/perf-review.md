---
description: Review and optimize performance of backend endpoints
---

1. **Identify slow endpoints:**
   - Check which endpoints are called most frequently
   - Check which endpoints do the most database queries

2. **N+1 query check:**
   - Search for loops that query the database inside them
   - Replace with eager loading (`joinedload`, `subqueryload`) or batch queries

3. **Cache utilization check:**
   - For each read endpoint, verify if Redis caching is applied
   - Check if cache keys are being set with appropriate TTLs
   - Verify write-through invalidation happens on every mutation

4. **Response size check:**
   - Verify pagination is used for list endpoints (not returning unbounded results)
   - Check that `to_dict()` only includes necessary fields

5. **Index check:**
   - For frequently filtered/sorted columns, verify database indexes exist
   - Key columns: `users.google_id`, `users.email`, `saved_pages.user_id`, `usage_events.user_id`

6. **Report** with specific recommendations and estimated impact
