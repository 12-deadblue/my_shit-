---
description: Validate that the extension and backend are consistent and properly configured
---

1. **Extension validation:**
   - Check `extension/manifest.json` is valid JSON
   - Verify every file referenced in manifest exists (`content.js`, `background.js`, `popup.html`, etc.)
   - Verify `popup.html` references only files that exist (`styles.css`, `popup.js`)
   - Check for `YOUR_GOOGLE_CLIENT_ID` placeholder — warn if not replaced

2. **Backend validation:**
   - Check all Python files compile: `python -m py_compile backend/app.py`
   - Verify `backend/.env` exists (not `.env.example`)
   - Check all imports resolve: `cd backend && python -c "from app import create_app; app = create_app('testing')"`
   - Verify required env vars are set (not placeholder values)

3. **Consistency checks:**
   - Extension's API base URL matches backend's host/port
   - CORS origins in backend `.env` include the extension ID
   - OAuth client ID matches between extension manifest and backend `.env`

4. **Report** all findings as a checklist with ✅/❌ per item
