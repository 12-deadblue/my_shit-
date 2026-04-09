---
description: Test assumptions before making changes (hypothesis testing)
---

1. State the hypothesis clearly (what you expect to happen)
2. Identify what could break:
   - Which files are affected?
   - Which API endpoints are involved?
   - Which database tables are touched?
3. Check for existing tests that cover the affected area
4. If no tests exist, write a quick test to validate current behavior BEFORE changing anything
5. Run the test to confirm current behavior matches expectations
6. Only THEN proceed with the change
7. Re-run the test after the change to verify the hypothesis
8. Report: hypothesis, test result before, change made, test result after
