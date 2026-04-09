---
description: Add a new feature end-to-end across extension, backend, and dashboard
---

1. **Understand the feature:**
   - What does the user want?
   - Which components are involved? (extension, backend, dashboard, or all?)
   - Does it need a new API endpoint?
   - Does it need a new database model/field?
   - Is it free or Pro-only?

2. **If new API endpoint needed:**
   - Add route to the appropriate blueprint in `backend/routes/`
   - Add `@jwt_required()` if authenticated
   - Add `@admin_required` if admin-only
   - Add rate limiting if it's a write endpoint
   - Update Redis cache if applicable

3. **If new database field/model needed:**
   - Add to `backend/db/models.py`
   - Add `to_dict()` method for serialization
   - The database will auto-migrate on next restart (SQLAlchemy create_all)

4. **If extension UI changes needed:**
   - Update `extension/popup.html` for new UI elements
   - Update `extension/popup.js` for behavior
   - If Pro-only, add license check via `license.js`

5. **If dashboard changes needed:**
   - Add new view or update existing in `dashboard/index.html`
   - Add data fetching in `dashboard/dashboard.js`

6. **Write tests:**
   - Add test in `backend/tests/test_<feature>.py`
   - Test happy path, auth failure, and validation error

7. **Run /validate to verify consistency**
