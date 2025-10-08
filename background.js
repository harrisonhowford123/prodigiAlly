// background.js - Service worker for the extension

// Keep track of active state
let isActive = false;

// Listen for installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('ProdigiAlly Barcode Scanner installed');
  
  // Set default storage values
  chrome.storage.local.set({
    isLoggedIn: false,
    employee: null,
    workstation: null,
    recentScans: []
  });
});

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  // Forward messages to popup if it's open
  chrome.runtime.sendMessage(request).catch(() => {
    // Popup is not open, that's okay
  });
});

// Optional: Handle extension icon click to ensure popup opens
chrome.action.onClicked.addListener((tab) => {
  // This won't fire if popup is defined in manifest
  // But kept here for completeness
});

// Keep service worker alive (Chrome tends to suspend service workers)
const keepAlive = () => {
  // Simple heartbeat to prevent suspension
  chrome.storage.local.get(['isLoggedIn'], (result) => {
    if (result.isLoggedIn) {
      // Still active, check again in 30 seconds
      setTimeout(keepAlive, 30000);
    }
  });
};

// Start keep-alive when extension loads
keepAlive();