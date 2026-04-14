// Wait for the DOM to load

document.addEventListener('DOMContentLoaded', function() {
  
  // Get references to buttons
  const highlightBtn = document.getElementById('highlightBtn');
  const saveBtn = document.getElementById('saveBtn');
  const clearBtn = document.getElementById('clearBtn');
  const savedList = document.getElementById('savedList');
  
  // Auth UI references
  const loginBtn = document.getElementById('loginBtn');
  const logoutBtn = document.getElementById('logoutBtn');
  const userProfile = document.getElementById('userProfile');
  const authSection = document.getElementById('authSection');
  const actionsSection = document.getElementById('actionsSection');
  const userAvatar = document.getElementById('userAvatar');
  const userName = document.getElementById('userName');
  
  const API_URL = 'http://localhost:5000/api';

  // Check auth state on load
  checkAuthState();
  
  // Load and display saved items
  loadSavedItems();

  // Login handler
  loginBtn.addEventListener('click', () => {
    loginBtn.textContent = 'Logging in...';
    loginBtn.disabled = true;
    
    chrome.runtime.sendMessage({ action: 'login' }, (response) => {
      loginBtn.textContent = 'Login with Google';
      loginBtn.disabled = false;
      
      if (response && response.success) {
        showNotification('Logged in successfully!');
        checkAuthState();
      } else {
        showNotification('Login failed: ' + (response?.error || 'Unknown error'));
      }
    });
  });

  // Logout handler
  logoutBtn.addEventListener('click', () => {
    chrome.storage.local.remove(['access_token', 'refresh_token', 'user'], () => {
      // Need to revoke token from identity API as well for full logout
      chrome.identity.getAuthToken({ 'interactive': false }, function(current_token) {
        if (!chrome.runtime.lastError && current_token) {
          chrome.identity.removeCachedAuthToken({ token: current_token }, function() {});
        }
      });
      showNotification('Logged out!');
      checkAuthState();
    });
  });

  function checkAuthState() {
    chrome.storage.local.get(['user'], (result) => {
      if (result.user) {
        // Authenticated
        authSection.style.display = 'none';
        userProfile.style.display = 'flex';
        actionsSection.style.display = 'block';
        
        userName.textContent = result.user.name;
        userAvatar.src = result.user.avatar_url;
      } else {
        // Not authenticated
        authSection.style.display = 'block';
        userProfile.style.display = 'none';
        actionsSection.style.display = 'none';
      }
    });
  }
  
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
    const pageData = {
      url: tab.url,
      title: tab.title,
      timestamp: new Date().toISOString()
    };
    
    // Save to backend if authenticated
    chrome.storage.local.get(['access_token', 'savedPages'], async (result) => {
      if (result.access_token) {
        try {
          saveBtn.textContent = 'Saving...';
          saveBtn.disabled = true;
          const res = await fetch(`${API_URL}/data/pages`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${result.access_token}`
            },
            body: JSON.stringify(pageData)
          });
          
          if (!res.ok) throw new Error('Backend sync failed');
          showNotification('Page synced to cloud!');
        } catch (err) {
          console.error('Sync error:', err);
          showNotification('Saved locally (sync failed)');
        } finally {
          saveBtn.textContent = 'Save Current Page';
          saveBtn.disabled = false;
        }
      }
      
      const savedPages = result.savedPages || [];
      savedPages.push(pageData);
      
      chrome.storage.local.set({ savedPages }, () => {
        if (!result.access_token) showNotification('Page saved locally!');
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
