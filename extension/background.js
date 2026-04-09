chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed! Welcome! 🎉');
  chrome.storage.local.get(['savedPages'], (result) => {
    if (!result.savedPages) {
      chrome.storage.local.set({ savedPages: [] });
    }
  });
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'backgroundTask') {
    console.log('Background task received:', request.data);
    sendResponse({ status: 'completed' });
  }
  return true;
});

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
