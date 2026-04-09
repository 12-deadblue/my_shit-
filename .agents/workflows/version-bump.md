---
description: Bump the version number in manifest.json and related files
---

1. Read current version from extension/manifest.json
2. Ask the user for the new version (or suggest incrementing the patch number)
3. Update version in extension/manifest.json
4. If generate-extension.html exists, update the embedded manifest version there too
5. Report the version change
