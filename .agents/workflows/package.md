---
description: Package the Chrome extension for distribution or testing
---

// turbo-all

1. Verify all required extension files exist in `extension/`:
   - `manifest.json`
   - `popup.html`
   - `popup.js`
   - `content.js`
   - `background.js`
   - `styles.css`

2. Validate `manifest.json` is valid JSON and has required fields:
   - `manifest_version` must be 3
   - `name`, `version`, `description` must exist
   - All referenced files (`content.js`, `background.js`, `popup.html`) must exist

3. If `extension/icons/` directory has PNG files, verify they are referenced in manifest

4. Create a build ZIP:
   ```
   cd extension && zip -r ../dist/extension-v$(jq -r .version manifest.json).zip . -x ".*"
   ```

5. Report final ZIP size and contents
