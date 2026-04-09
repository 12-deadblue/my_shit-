# My Custom Chrome Extension 🚀

**Free forever. No subscriptions. No bullshit.**

## What This Extension Does

- **Highlight Text**: Click a button or press Ctrl+Shift+H to highlight text on any page
- **Save Pages**: Save any webpage with one click - stored locally on your machine
- **Quick Access**: View and access all your saved pages from the popup
- **100% Free**: No ads, no tracking, no payment required

## Installation Instructions

### Step 1: Get Icon Files

You need icon files for Chrome to recognize the extension. Here are your options:

**Option A: Quick & Easy (Use Emojis as Icons)**
1. Go to https://favicon.io/emoji-favicons/
2. Choose any emoji (like 🚀, ⚡, or 💎)
3. Download the favicon package
4. Rename the files:
   - `favicon-16x16.png` → `icon16.png`
   - `favicon-32x32.png` → `icon48.png`
   - `android-chrome-192x192.png` → `icon128.png`
5. Put them in the `my-chrome-extension` folder

**Option B: Create Your Own**
- Create 3 PNG images: 16x16, 48x48, and 128x128 pixels
- Name them: `icon16.png`, `icon48.png`, `icon128.png`
- Put them in the `my-chrome-extension` folder

**Option C: Skip Icons Temporarily**
- Comment out or remove the "icons" sections in `manifest.json`
- The extension will work but won't have a custom icon

### Step 2: Load Extension into Chrome

1. Open Chrome and go to: `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right corner)
3. Click "Load unpacked"
4. Select the `my-chrome-extension` folder
5. Done! Your extension is now loaded

### Step 3: Use Your Extension

- Click the extension icon in your toolbar
- Try the different buttons
- Save some pages and watch them appear in your list
- Select some text and click "Highlight Text"

## How to Customize

### Change the Name and Description

Edit `manifest.json`:
```json
"name": "Whatever You Want",
"description": "Your custom description here",
```

### Change the Colors

Edit `styles.css` and modify the gradient:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

Try different gradients from: https://uigradients.com/

### Add More Features

**Add a New Button:**
1. Add button HTML in `popup.html`
2. Add click handler in `popup.js`
3. Add functionality in `content.js` if needed

**Store More Data:**
```javascript
// In popup.js
chrome.storage.local.set({ myData: 'anything' });

chrome.storage.local.get(['myData'], (result) => {
  console.log(result.myData);
});
```

**Run Code on Specific Sites:**
Edit `manifest.json` content_scripts:
```json
"matches": ["https://github.com/*"]
```

## Common Customizations

### Make it Work Only on Specific Sites

In `manifest.json`, change:
```json
"matches": ["<all_urls>"]
```
to:
```json
"matches": ["https://github.com/*", "https://youtube.com/*"]
```

### Add Keyboard Shortcuts

Add to `manifest.json`:
```json
"commands": {
  "save-page": {
    "suggested_key": {
      "default": "Ctrl+Shift+S"
    },
    "description": "Save current page"
  }
}
```

Then handle it in `background.js`:
```javascript
chrome.commands.onCommand.addListener((command) => {
  if (command === 'save-page') {
    // Your code here
  }
});
```

### Add More Permissions

If you need access to bookmarks, history, tabs, etc., add to `manifest.json`:
```json
"permissions": [
  "storage",
  "activeTab",
  "bookmarks",
  "history",
  "tabs"
]
```

## Troubleshooting

**Extension won't load:**
- Make sure all files are in the same folder
- Check that icon files exist (or remove icon references)
- Look at Chrome's error message on the extensions page

**Buttons don't work:**
- Open the extension popup
- Right-click → Inspect → Console
- Check for JavaScript errors

**Content script not running:**
- Reload the extension on `chrome://extensions/`
- Refresh the webpage you're testing on
- Check if the site has strict Content Security Policy

## File Structure

```
my-chrome-extension/
├── manifest.json      # Extension configuration
├── popup.html         # Popup interface
├── popup.js          # Popup functionality
├── content.js        # Runs on web pages
├── background.js     # Background tasks
├── styles.css        # Styling
├── icon16.png        # Small icon
├── icon48.png        # Medium icon
└── icon128.png       # Large icon
```

## Next Steps

1. **Publishing**: If you want to share with others, you can publish to the Chrome Web Store ($5 one-time fee)
2. **Auto-update**: Published extensions auto-update. Unpacked ones need manual reload
3. **Advanced Features**: Check out Chrome's Extension API docs for more capabilities

## Resources

- [Chrome Extension Docs](https://developer.chrome.com/docs/extensions/)
- [Chrome Extension Samples](https://github.com/GoogleChrome/chrome-extensions-samples)
- [Stack Overflow - Chrome Extensions](https://stackoverflow.com/questions/tagged/google-chrome-extension)

---

**You built this yourself. You own it. No subscription required. Ever.**

Made with rage against subscription models 😤
