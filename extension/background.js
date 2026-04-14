chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed! Welcome! 🎉');
  chrome.storage.local.get(['savedPages'], (result) => {
    if (!result.savedPages) {
      chrome.storage.local.set({ savedPages: [] });
    }
  });
});

const API_URL = 'http://localhost:5000/api';

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'login') {
    handleLogin().then(sendResponse).catch(err => {
      console.error('Login error:', err);
      sendResponse({ success: false, error: err.message });
    });
    return true; // Let Chrome know we'll respond asynchronously
  }

  if (request.action === 'backgroundTask') {
    console.log('Background task received:', request.data);
    sendResponse({ status: 'completed' });
  }
  return true;
});

async function handleLogin() {
  return new Promise((resolve, reject) => {
    chrome.identity.getAuthToken({ interactive: true }, async (token) => {
      if (chrome.runtime.lastError || !token) {
        return reject(new Error(chrome.runtime.lastError?.message || 'Token empty'));
      }

      try {
        // Exchange Google token for our SaaS backend JWT
        const response = await fetch(`${API_URL}/auth/google`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ access_token: token })
        });

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.error || 'Backend auth failed');
        }

        const data = await response.json();
        
        // Save the JWTs and user info in chrome.storage.local
        chrome.storage.local.set({
          access_token: data.access_token,
          refresh_token: data.refresh_token,
          user: data.user
        }, () => {
          resolve({ success: true, user: data.user });
        });
      } catch (err) {
        reject(err);
      }
    });
  });
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete') {
    console.log('Page loaded:', tab.url);
  }
});

chrome.contextMenus.create({
  id: 'saveToExtension',
  title: 'Save to My Extension',
  contexts: ['selection', 'page']
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'saveToExtension') {
    console.log('Context menu clicked:', info.selectionText);
  }
});
