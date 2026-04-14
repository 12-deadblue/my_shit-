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
 3.1 Understanding:
   - trace the scope of error by using unit test  analysis and assert funtions.
   

4. Hypothesize:
   - Form ONE specific hypothesis about the root cause
   - Predict what you would see if the hypothesis is correct.
  4.1 Hypothesizing
   -based on hypothesize  google the posial paracticise related to testing in that unit.Before writing fullfladged test in that scope of error
 4.2 Hypothesizing 
   - use sites like Stackoverflow to find a proprare referaces

5. Test:
   - Write a minimal test or check that validates/invalidates the hypothesis
   - Do NOT make code changes yet
  5.1 - the test should be writed based on techniques that you will google.
 5.2 -  comment test after idintifing the cause of problem.
 
6. Fix:
   - Only after confirming the root cause, make the minimal fix
   - Explain WHY the fix works, not just WHAT it changes.
 6.1 Fix -  specify the difficulty of fix. On scale from 1 to 10
7. Verify:
   - Run existing tests to make sure nothing else broke
   - Re-test the original reproduction case
  7.1 
   - DON'T CHANGE TESTS IF THE PROBLEM IS TOO HARD TO FIX. 
  7.2 
   - MAKE THE COMMIT BEFORE WRITING IN TEST CASES
 7.3 
  - follow THE protocl of commits in described in Commit.md
8. Prevent:
   - If this bug class could recur, suggest adding a test or validation to catch it.
 8.1-Before adding tests read the content of tests.md. D
 