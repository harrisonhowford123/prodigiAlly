// content.js - Injected into OneFlow pages to capture barcode scans

const SERVER_URL = 'http://192.168.111.230:8080';

// State
let isCapturing = false;
let currentEmployee = null;
let currentWorkstation = null;
let lastProcessedBarcode = null;
let lastProcessedTime = 0;

// Configuration
const MIN_BARCODE_LENGTH = 6;
const MAX_BARCODE_LENGTH = 15;
const DUPLICATE_TIMEOUT = 2000; // Prevent duplicate scans within 2 seconds

// Observers
let inputObserver = null;
let domObserver = null;

// Initialize
(async function init() {
  console.log('[ProdigiAlly] Content script loaded on OneFlow');
  
  // Wait for document to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupObservers);
  } else {
    setupObservers();
  }
  
  // Check if we should be capturing
  const stored = await chrome.storage.local.get(['employee', 'workstation', 'isLoggedIn']);
  if (stored.isLoggedIn) {
    currentEmployee = stored.employee;
    currentWorkstation = stored.workstation;
    isCapturing = true;
    console.log(`[ProdigiAlly] Resuming capture for ${currentEmployee} at ${currentWorkstation}`);
  }
  
  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'START_CAPTURE') {
      startCapture(request.employee, request.workstation);
    } else if (request.type === 'STOP_CAPTURE') {
      stopCapture();
    }
  });
})();

function setupObservers() {
  console.log('[ProdigiAlly] Setting up observers');
  
  // Monitor all input fields on the page
  monitorExistingInputs();
  
  // Watch for new input fields being added to the DOM
  domObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1) { // Element node
          // Check if the node itself is an input
          if (node.tagName === 'INPUT' || node.tagName === 'TEXTAREA') {
            attachInputListener(node);
          }
          // Check for inputs within the added node
          if (node.querySelectorAll) {
            const inputs = node.querySelectorAll('input, textarea');
            inputs.forEach(input => attachInputListener(input));
          }
        }
      });
    });
  });
  
  // Start observing the document for added nodes
  domObserver.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  console.log('[ProdigiAlly] Observers initialized');
}

function monitorExistingInputs() {
  const inputs = document.querySelectorAll('input, textarea');
  console.log(`[ProdigiAlly] Found ${inputs.length} existing input fields`);
  inputs.forEach(input => attachInputListener(input));
}

function attachInputListener(input) {
  // Skip if already monitoring
  if (input.dataset.prodigiAllyMonitored) {
    return;
  }
  
  input.dataset.prodigiAllyMonitored = 'true';
  
  // Track previous value
  let previousValue = input.value || '';
  let changeTimer = null;
  
  // Listen for input events
  const handleInput = (event) => {
    if (!isCapturing) return;
    
    const currentValue = input.value || '';
    
    // Clear existing timer
    if (changeTimer) {
      clearTimeout(changeTimer);
    }
    
    // Wait a bit to see if more characters are coming
    changeTimer = setTimeout(() => {
      // Check if value changed and looks like a barcode
      if (currentValue !== previousValue) {
        const newContent = currentValue;
        
        console.log(`[ProdigiAlly] Input changed: "${previousValue}" -> "${newContent}"`);
        
        // Check if the entire value is a barcode (scanner might replace field content)
        if (isValidBarcode(newContent)) {
          console.log(`[ProdigiAlly] Full field is barcode: ${newContent}`);
          processBarcodeCapture(newContent);
          previousValue = newContent;
          return;
        }
        
        // Check if a barcode was appended
        if (newContent.length > previousValue.length) {
          const addedText = newContent.substring(previousValue.length);
          console.log(`[ProdigiAlly] Text added: "${addedText}"`);
          
          if (isValidBarcode(addedText)) {
            console.log(`[ProdigiAlly] Added text is barcode: ${addedText}`);
            processBarcodeCapture(addedText);
          }
        }
        
        previousValue = newContent;
      }
    }, 100); // Wait 100ms after last character
  };
  
  input.addEventListener('input', handleInput);
  input.addEventListener('change', handleInput);
  
  console.log(`[ProdigiAlly] Attached listener to ${input.tagName} (type: ${input.type})`);
}

function isValidBarcode(barcode) {
  if (!barcode || typeof barcode !== 'string') return false;
  
  // Trim whitespace
  barcode = barcode.trim();
  
  // Check length
  if (barcode.length < MIN_BARCODE_LENGTH || barcode.length > MAX_BARCODE_LENGTH) {
    return false;
  }
  
  // Check if alphanumeric only
  if (!/^[A-Z0-9]+$/i.test(barcode)) {
    return false;
  }
  
  // Prefer specific lengths (10 for lead, 11 for ISO)
  if (barcode.length === 10 || barcode.length === 11) {
    return true;
  }
  
  // Allow other reasonable lengths
  return true;
}

async function processBarcodeCapture(barcode) {
  barcode = barcode.trim().toUpperCase();
  
  // Prevent duplicate processing
  const now = Date.now();
  if (barcode === lastProcessedBarcode && (now - lastProcessedTime) < DUPLICATE_TIMEOUT) {
    console.log(`[ProdigiAlly] Skipping duplicate barcode: ${barcode}`);
    return;
  }
  
  lastProcessedBarcode = barcode;
  lastProcessedTime = now;
  
  console.log(`[ProdigiAlly] Processing barcode: ${barcode}`);
  
  // ALWAYS save to storage (even if popup is closed)
  chrome.storage.local.get(['recentScans'], result => {
    const scans = result.recentScans || [];
    scans.push(barcode);
    if (scans.length > 50) scans.shift(); // Keep max 50 in storage
    chrome.storage.local.set({recentScans: scans});
    console.log(`[ProdigiAlly] Saved barcode to storage. Total scans: ${scans.length}`);
  });
  
  // Try to notify popup (will fail silently if popup is closed)
  chrome.runtime.sendMessage({
    type: 'BARCODE_SCANNED',
    barcode: barcode
  }).catch(err => console.log('[ProdigiAlly] Could not notify popup (popup likely closed):', err));
  
  // Determine if it's lead or ISO barcode
  let leadBarcode = null;
  let isoBarcode = null;
  
  if (barcode.length === 10) {
    leadBarcode = barcode;
  } else if (barcode.length === 11) {
    isoBarcode = barcode;
  }
  
  // Send to server
  try {
    const params = new URLSearchParams({
      containerID: '',
      orderNumber: '',
      leadBarcode: leadBarcode || '',
      isoBarcode: isoBarcode || '',
      workstation: currentWorkstation,
      employeeName: currentEmployee
    });
    
    const response = await fetch(`${SERVER_URL}/api/orderTrack?${params}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
      console.log(`[ProdigiAlly] Successfully sent barcode to server`);
      showVisualFeedback('✓ Scanned: ' + barcode, '#6D05FF');
    } else {
      console.error('[ProdigiAlly] Server error:', data.message);
      showVisualFeedback('✗ Error: ' + data.message, '#FF4C4C');
    }
  } catch (error) {
    console.error('[ProdigiAlly] Failed to send barcode to server:', error);
    showVisualFeedback('✗ Connection Error', '#FF4C4C');
  }
}

function showVisualFeedback(message, color) {
  // Determine if this is an error (red) or success (purple)
  const isError = color === '#FF4C4C';
  
  // Create status banner if it doesn't exist
  let statusBanner = document.querySelector('.prodigially-status-banner');
  if (!statusBanner) {
    statusBanner = document.createElement('div');
    statusBanner.className = 'prodigially-status-banner';
    statusBanner.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 999999;
      max-width: 300px;
    `;
    document.body.appendChild(statusBanner);
    
    // Add animation styles if not present
    if (!document.querySelector('style[data-prodigially]')) {
      const style = document.createElement('style');
      style.setAttribute('data-prodigially', 'true');
      style.textContent = `
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        @keyframes slideOut {
          from {
            transform: translateX(0);
            opacity: 1;
          }
          to {
            transform: translateX(100%);
            opacity: 0;
          }
        }
        .prodigially-close-btn {
          position: absolute;
          top: 8px;
          right: 8px;
          width: 20px;
          height: 20px;
          background: rgba(255, 255, 255, 0.3);
          border: none;
          border-radius: 50%;
          cursor: pointer;
          font-size: 14px;
          line-height: 18px;
          color: white;
          font-weight: bold;
          transition: background 0.2s;
        }
        .prodigially-close-btn:hover {
          background: rgba(255, 255, 255, 0.5);
        }
      `;
      document.head.appendChild(style);
    }
  }
  
  // Create the permanent status box if it doesn't exist
  let permanentStatus = statusBanner.querySelector('.prodigially-permanent-status');
  if (!permanentStatus && currentEmployee) {
    permanentStatus = document.createElement('div');
    permanentStatus.className = 'prodigially-permanent-status';
    permanentStatus.style.cssText = `
      background: #E8F5E9;
      color: #2E7D32;
      padding: 12px 20px;
      border-radius: 5px;
      font-family: Arial, sans-serif;
      font-size: 13px;
      font-weight: bold;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      margin-bottom: 10px;
      border: 2px solid #6D05FF;
      animation: slideIn 0.3s ease;
    `;
    permanentStatus.innerHTML = `
      <div style="font-size: 14px; margin-bottom: 5px;">✓ Scanning Active</div>
      <div style="font-size: 12px; opacity: 0.9;">
        ${currentEmployee}<br>
        ${currentWorkstation}
      </div>
    `;
    statusBanner.appendChild(permanentStatus);
  }
  
  // Create notification below the status
  const notification = document.createElement('div');
  notification.className = 'prodigially-notification';
  notification.style.cssText = `
    background: ${color};
    color: white;
    padding: 12px ${isError ? '40px' : '20px'} 12px 20px;
    border-radius: 5px;
    font-family: Arial, sans-serif;
    font-size: 14px;
    font-weight: bold;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    animation: slideIn 0.3s ease;
    margin-bottom: 10px;
    word-break: break-all;
    position: relative;
  `;
  notification.textContent = message;
  
  // Add close button for errors
  if (isError) {
    const closeBtn = document.createElement('button');
    closeBtn.className = 'prodigially-close-btn';
    closeBtn.innerHTML = '×';
    closeBtn.onclick = () => {
      notification.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => {
        notification.remove();
      }, 300);
    };
    notification.appendChild(closeBtn);
  }
  
  statusBanner.appendChild(notification);
  
  // Auto-remove only success messages (not errors)
  if (!isError) {
    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 3000);
  }
}

function startCapture(employee, workstation) {
  currentEmployee = employee;
  currentWorkstation = workstation;
  isCapturing = true;
  lastProcessedBarcode = null;
  lastProcessedTime = 0;
  
  console.log(`[ProdigiAlly] Started capturing for ${employee} at ${workstation}`);
  showVisualFeedback('Scanning Active', '#6D05FF');
}

function stopCapture() {
  isCapturing = false;
  currentEmployee = null;
  currentWorkstation = null;
  lastProcessedBarcode = null;
  lastProcessedTime = 0;
  
  // Remove the status banner
  const statusBanner = document.querySelector('.prodigially-status-banner');
  if (statusBanner) {
    statusBanner.remove();
  }
  
  console.log('[ProdigiAlly] Stopped capturing');
}

// Cleanup on unload
window.addEventListener('beforeunload', () => {
  if (domObserver) {
    domObserver.disconnect();
  }
});