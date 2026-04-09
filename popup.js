// Wait for the DOM to load\

document.addEventListener('DOMContentLoaded', function() {
  
  // Get references to buttons
  const highlightBtn = document.getElementById('highlightBtn');
  const saveBtn = document.getElementById('saveBtn');
  const clearBtn = document.getElementById('clearBtn');
  const savedList = document.getElementById('savedList');
  
  // Load and display saved items
  loadSavedItems();
  
  // Highlight text on current page
  highlightBtn.addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    chrome.tabs.sendMessage(tab.id, { action: 'highlight' }, (response) => {
      if (response && response.success) {
        showNotification('Text highlighted!');
      }
    });
  });
  
  // Save current page URL and title
  saveBtn.addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Get existing saved items
    chrome.storage.local.get(['savedPages'], (result) => {
      const savedPages = result.savedPages || [];
      
      // Add new page
      savedPages.push({
        url: tab.url,
        title: tab.title,
        timestamp: new Date().toISOString()
      });
      
      // Save back to storage
      chrome.storage.local.set({ savedPages }, () => {
        showNotification('Page saved!');
        loadSavedItems();
      });
    });
  });
  
  // Clear all saved data
  clearBtn.addEventListener('click', () => {
    if (confirm('Clear all saved data?')) {
      chrome.storage.local.clear(() => {
        showNotification('All data cleared!');
        loadSavedItems();
      });
    }
  });
  
  // Load and display saved items
  function loadSavedItems() {
    chrome.storage.local.get(['savedPages'], (result) => {
      const savedPages = result.savedPages || [];
      
      if (savedPages.length === 0) {
        savedList.innerHTML = '<p class="empty">No saved pages yet</p>';
        return;
      }
      
      savedList.innerHTML = savedPages.map((page, index) => `
        <div class="saved-item">
          <a href="${page.url}" target="_blank">${page.title}</a>
          <button class="delete-btn" data-index="${index}">×</button>
        </div>
      `).join('');
      
      // Add delete functionality
      document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const index = parseInt(e.target.dataset.index);
          deleteSavedItem(index);
        });
      });
    });
  }
  
  // Delete a saved item
  function deleteSavedItem(index) {
    chrome.storage.local.get(['savedPages'], (result) => {
      const savedPages = result.savedPages || [];
      savedPages.splice(index, 1);
      
      chrome.storage.local.set({ savedPages }, () => {
        loadSavedItems();
      });
    });
  }
  
  // Show notification
  function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 2000);
  }
});
