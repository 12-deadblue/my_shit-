---
description: Generate a pull request description from recent changes
---

1. Run git diff --stat to see which files changed
2. Run git diff to see the actual changes
3. Categorize changes by component:
   - Backend (backend/)
   - Extension (extension/)
   - Dashboard (dashboard/)
   - Config/DevOps (root files, .agents/, .github/)

4. Generate a PR description following this template:

   ## Summary
   [One-line description of what this PR does]

   ## Changes
   ### Backend
   - [change 1]

   ### Extension
   - [change 1]

   ### Dashboard
   - [change 1]

   ## Testing
   - [ ] Backend tests pass (cd backend and pytest)
   - [ ] Extension loads in Chrome without errors
   - [ ] Dashboard renders correctly

5. Output the PR description for the user to copy
