// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  
  if (request.action === 'highlight') {
    highlightSelectedText();
    sendResponse({ success: true });
  }
  
  return true; // Keep the message channel open for async response
});

// Highlight selected text on the page
function highlightSelectedText() {
  const selection = window.getSelection();
  
  if (selection.toString().length > 0) {
    const range = selection.getRangeAt(0);
    const span = document.createElement('span');
    span.style.backgroundColor = '#ffeb3b';
    span.style.padding = '2px';
    span.textContent = selection.toString();
    
    range.deleteContents();
    range.insertNode(span);
    
    // Clear selection
    selection.removeAllRanges();
  } else {
    // If no text is selected, highlight all paragraphs temporarily
    const paragraphs = document.querySelectorAll('p');
    paragraphs.forEach(p => {
      p.style.backgroundColor = '#ffeb3b';
      p.style.transition = 'background-color 1s';
      
      setTimeout(() => {
        p.style.backgroundColor = '';
      }, 1000);
    });
  }
}

// Example: You can add more content script functionality here
// Listen for specific keyboard shortcuts
document.addEventListener('keydown', (e) => {
  // Ctrl+Shift+H to highlight
  if (e.ctrlKey && e.shiftKey && e.key === 'H') {
    highlightSelectedText();
  }
});

console.log('My custom extension loaded! 🚀');
