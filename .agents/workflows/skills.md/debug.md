---
description: Debug an issue step by step without guessing
---

1. Reproduce:
   - Get the exact error message or unexpected behavior description
   - Identify which component is affected (extension, backend, dashboard)

2. Locate:
   - If backend error: check the Flask logs, find the traceback
   - If extension error: check the browser console (popup or background service worker)
   - If dashboard error: check browser console on the dashboard page
   - Search for the error message string in codebase with grep

3. Understand:
   - Read the code around the error location
   - Trace the data flow: where does the input come from? What transformations happen?
   - Check if it is a cache issue (stale Redis data?) try redis_client.invalidate_*

4. Hypothesize:
   - Form ONE specific hypothesis about the root cause
   - Predict what you would see if the hypothesis is correct

5. Test:
   - Write a minimal test or check that validates/invalidates the hypothesis
   - Do NOT make code changes yet

6. Fix:
   - Only after confirming the root cause, make the minimal fix
   - Explain WHY the fix works, not just WHAT it changes

7. Verify:
   - Run existing tests to make sure nothing else broke
   - Re-test the original reproduction case

8. Prevent:
   - If this bug class could recur, suggest adding a test or validation to catch it
