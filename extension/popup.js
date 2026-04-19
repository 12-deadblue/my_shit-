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

  // Subscription UI references
  const subscriptionSection = document.getElementById('subscriptionSection');
  const subLoading = document.getElementById('subLoading');
  const subLoginPrompt = document.getElementById('subLoginPrompt');
  const subContent = document.getElementById('subContent');
  const planBadge = document.getElementById('planBadge');
  const planBadgeText = document.getElementById('planBadgeText');
  const planCards = document.getElementById('planCards');
  const activePlanInfo = document.getElementById('activePlanInfo');
  const activePlanEmoji = document.getElementById('activePlanEmoji');
  const activePlanName = document.getElementById('activePlanName');
  const activePlanExpires = document.getElementById('activePlanExpires');
  const cancelSubBtn = document.getElementById('cancelSubBtn');
  const upgradeProBtn = document.getElementById('upgradeProBtn');
  const upgradeLifetimeBtn = document.getElementById('upgradeLifetimeBtn');
  const footerText = document.getElementById('footerText');
  
  const API_URL = 'http://localhost:5000/api';

  // Check auth state on load
  checkAuthState();
  
  // Load and display saved items
  loadSavedItems();

  // ===== AUTH HANDLERS =====

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
    chrome.storage.local.get(['user', 'access_token'], (result) => {
      if (result.user) {
        // Authenticated
        authSection.style.display = 'none';
        userProfile.style.display = 'flex';
        actionsSection.style.display = 'block';
        
        userName.textContent = result.user.name;
        userAvatar.src = result.user.avatar_url;

        // Load subscription status
        loadSubscriptionStatus(result.access_token);
      } else {
        // Not authenticated
        authSection.style.display = 'block';
        userProfile.style.display = 'none';
        actionsSection.style.display = 'none';

        // Show login prompt in subscription section
        subLoginPrompt.style.display = 'block';
        subContent.style.display = 'none';
        subLoading.style.display = 'none';
        updateFooter('free');
      }
    });
  }

  // ===== SUBSCRIPTION HANDLERS =====

  async function loadSubscriptionStatus(accessToken) {
    if (!accessToken) {
      subLoginPrompt.style.display = 'block';
      subContent.style.display = 'none';
      return;
    }

    // Show loading
    subLoginPrompt.style.display = 'none';
    subLoading.style.display = 'block';
    subContent.style.display = 'none';

    try {
      const res = await fetch(`${API_URL}/subscription/status`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });

      if (!res.ok) {
        throw new Error('Failed to fetch subscription status');
      }

      const data = await res.json();
      const subscription = data.subscription || { plan: 'free', status: 'none' };
      
      subLoading.style.display = 'none';
      subContent.style.display = 'block';
      
      updateSubscriptionUI(subscription);
    } catch (err) {
      console.error('Subscription status error:', err);
      subLoading.style.display = 'none';
      subContent.style.display = 'block';
      // Default to free on error
      updateSubscriptionUI({ plan: 'free', status: 'none' });
    }
  }

  function updateSubscriptionUI(subscription) {
    const plan = subscription.plan || 'free';
    const status = subscription.status || 'none';

    // Update badge
    planBadge.className = 'plan-badge';
    if (plan === 'free' || status === 'none' || status === 'expired') {
      planBadge.classList.add('tier-free');
      planBadgeText.textContent = 'Free';
    } else if (plan === 'lifetime') {
      planBadge.classList.add('tier-lifetime');
      planBadgeText.textContent = 'Lifetime';
    } else {
      planBadge.classList.add('tier-pro');
      planBadgeText.textContent = 'Pro';
    }

    // Show plan cards or active info
    const isSubscribed = status === 'active' && plan !== 'free';

    if (isSubscribed) {
      // Hide plan cards, show active info
      planCards.style.display = 'none';
      activePlanInfo.style.display = 'block';

      if (plan === 'lifetime') {
        activePlanEmoji.textContent = '👑';
        activePlanName.textContent = 'Lifetime';
        activePlanExpires.textContent = 'Never expires';
        cancelSubBtn.style.display = 'none';
      } else {
        activePlanEmoji.textContent = '⭐';
        activePlanName.textContent = 'Pro Monthly';
        if (subscription.expires_at) {
          const expDate = new Date(subscription.expires_at);
          activePlanExpires.textContent = `Renews ${expDate.toLocaleDateString()}`;
        } else {
          activePlanExpires.textContent = '';
        }
        cancelSubBtn.style.display = 'inline-block';
      }
    } else {
      // Show plan cards, hide active info
      planCards.style.display = 'grid';
      activePlanInfo.style.display = 'none';
    }

    updateFooter(plan);
  }

  function updateFooter(tier) {
    const labels = {
      'free': '✨ Free tier',
      'pro': '⭐ Pro tier',
      'pro_monthly': '⭐ Pro tier',
      'lifetime': '👑 Lifetime tier'
    };
    footerText.innerHTML = `<span class="tier-text">${labels[tier] || labels['free']}</span>`;
  }

  // Upgrade button handlers
  upgradeProBtn.addEventListener('click', () => handleUpgrade('pro_monthly'));
  upgradeLifetimeBtn.addEventListener('click', () => handleUpgrade('lifetime'));

  async function handleUpgrade(planId) {
    const btn = planId === 'lifetime' ? upgradeLifetimeBtn : upgradeProBtn;
    const originalText = btn.textContent;
    
    btn.textContent = 'Processing...';
    btn.disabled = true;
    upgradeProBtn.disabled = true;
    upgradeLifetimeBtn.disabled = true;

    try {
      const result = await new Promise((resolve) => {
        chrome.storage.local.get(['access_token'], resolve);
      });

      if (!result.access_token) {
        showNotification('Please log in first');
        return;
      }

      // MVP: Send a mock payment token
      // In production, this would trigger the Google Pay flow
      const res = await fetch(`${API_URL}/subscription/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${result.access_token}`
        },
        body: JSON.stringify({
          plan_id: planId,
          payment_token: {
            type: 'CARD',
            info: { mock: true },
            tokenizationType: 'PAYMENT_GATEWAY'
          }
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || 'Payment failed');
      }

      showNotification('🎉 Subscription activated!');
      loadSubscriptionStatus(result.access_token);
    } catch (err) {
      console.error('Upgrade error:', err);
      showNotification('Upgrade failed: ' + err.message);
    } finally {
      btn.textContent = originalText;
      btn.disabled = false;
      upgradeProBtn.disabled = false;
      upgradeLifetimeBtn.disabled = false;
    }
  }

  // Cancel handler
  cancelSubBtn.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to cancel your subscription?')) {
      return;
    }

    cancelSubBtn.textContent = 'Cancelling...';
    cancelSubBtn.disabled = true;

    try {
      const result = await new Promise((resolve) => {
        chrome.storage.local.get(['access_token'], resolve);
      });

      const res = await fetch(`${API_URL}/subscription/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${result.access_token}`
        }
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || 'Cancel failed');
      }

      showNotification('Subscription cancelled');
      loadSubscriptionStatus(result.access_token);
    } catch (err) {
      console.error('Cancel error:', err);
      showNotification('Cancel failed: ' + err.message);
    } finally {
      cancelSubBtn.textContent = 'Cancel subscription';
      cancelSubBtn.disabled = false;
    }
  });

  // ===== PAGE ACTIONS =====
  
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
