// popup.js - Extension popup controller

const SERVER_URL = 'http://192.168.111.230:8080';

// State management
let isLoggedIn = false;
let currentEmployee = null;
let currentWorkstation = null;

// DOM elements
let loginView, mainView;
let usernameSelect, passwordInput, workstationSelect;
let loginBtn, logoutBtn;
let loginError, currentUser, currentStation, barcodeList;

document.addEventListener('DOMContentLoaded', async () => {
  // Get DOM elements
  loginView = document.getElementById('loginView');
  mainView = document.getElementById('mainView');
  usernameSelect = document.getElementById('username');
  passwordInput = document.getElementById('password');
  workstationSelect = document.getElementById('workstation');
  loginBtn = document.getElementById('loginBtn');
  logoutBtn = document.getElementById('logoutBtn');
  loginError = document.getElementById('loginError');
  currentUser = document.getElementById('currentUser');
  currentStation = document.getElementById('currentStation');
  barcodeList = document.getElementById('barcodeList');
  
  // Check if already logged in
  const stored = await chrome.storage.local.get(['employee', 'workstation', 'isLoggedIn']);
  if (stored.isLoggedIn) {
    currentEmployee = stored.employee;
    currentWorkstation = stored.workstation;
    showMainView();
  } else {
    await loadInitialData();
  }
  
  // Event listeners
  loginBtn.addEventListener('click', handleLogin);
  logoutBtn.addEventListener('click', handleLogout);
  
  // Listen for barcode updates from content script
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'BARCODE_SCANNED') {
      updateBarcodeDisplay(request.barcode);
    }
  });
});

async function loadInitialData() {
  try {
    // Clear existing options first
    usernameSelect.innerHTML = '<option value="">Select Employee...</option>';
    workstationSelect.innerHTML = '<option value="">Select Workstation...</option>';
    
    // Load employees
    const empResponse = await fetch(`${SERVER_URL}/api/employees`);
    const empData = await empResponse.json();
    
    if (empData.status === 'success') {
      empData.employees.forEach(emp => {
        const option = document.createElement('option');
        option.value = emp.employeeName;
        option.textContent = emp.employeeName;
        option.dataset.password = emp.password;
        usernameSelect.appendChild(option);
      });
    }
    
    // Load workstations
    const wsResponse = await fetch(`${SERVER_URL}/api/facilityWorkstations`);
    const wsData = await wsResponse.json();
    
    if (wsData.status === 'success') {
      wsData.workstations.forEach(ws => {
        const option = document.createElement('option');
        option.value = ws;
        option.textContent = ws;
        workstationSelect.appendChild(option);
      });
    }
  } catch (error) {
    showError('Failed to load data. Check server connection.');
    console.error('Error loading data:', error);
  }
}

async function handleLogin() {
  const username = usernameSelect.value;
  const password = passwordInput.value;
  const workstation = workstationSelect.value;
  
  // Validate inputs
  if (!username || !password || !workstation) {
    showError('Please fill all fields');
    return;
  }
  
  // Get stored password for validation
  const selectedOption = usernameSelect.options[usernameSelect.selectedIndex];
  const correctPassword = selectedOption.dataset.password;
  
  if (password !== correctPassword) {
    showError('Invalid password');
    return;
  }
  
  try {
    loginBtn.disabled = true;
    loginBtn.textContent = 'Logging in...';
    
    // Check if already logged in
    const checkResponse = await fetch(`${SERVER_URL}/api/getEmployeeLoginState`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({employeeName: username})
    });
    
    const checkData = await checkResponse.json();
    
    if (checkData.loggedIn) {
      showError('User already logged in elsewhere');
      return;
    }
    
    // Log the user in
    const loginResponse = await fetch(`${SERVER_URL}/api/loggedin`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({employeeName: username})
    });
    
    const loginData = await loginResponse.json();
    
    if (loginData.status === 'success') {
      // Save to storage
      currentEmployee = username;
      currentWorkstation = workstation;
      
      await chrome.storage.local.set({
        employee: username,
        workstation: workstation,
        isLoggedIn: true
      });
      
      // Notify content script to start capturing on OneFlow tabs
      chrome.tabs.query({url: [
        "*://pro.oneflowcloud.com/*",
        "*://pro.oneflow.com/*"
      ]}, tabs => {
        tabs.forEach(tab => {
          chrome.tabs.sendMessage(tab.id, {
            type: 'START_CAPTURE',
            employee: username,
            workstation: workstation
          });
        });
      });
      
      showMainView();
    } else {
      showError('Login failed: ' + (loginData.message || 'Unknown error'));
    }
  } catch (error) {
    showError('Server connection failed');
    console.error('Login error:', error);
  } finally {
    loginBtn.disabled = false;
    loginBtn.textContent = 'Login & Start Scanning';
  }
}

async function handleLogout() {
  try {
    // Log out from server
    await fetch(`${SERVER_URL}/api/loggedOut`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({employeeName: currentEmployee})
    });
    
    // Clear storage
    await chrome.storage.local.clear();
    
    // Notify content script to stop capturing
    chrome.tabs.query({url: [
      "*://pro.oneflowcloud.com/*",
      "*://pro.oneflow.com/*"
    ]}, tabs => {
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, {type: 'STOP_CAPTURE'});
      });
    });
    
    // Reset UI
    currentEmployee = null;
    currentWorkstation = null;
    isLoggedIn = false;
    passwordInput.value = '';
    
    // Show login view
    loginView.classList.remove('hidden');
    mainView.classList.add('hidden');
    
    // IMPORTANT: Reload the employee and workstation dropdowns
    await loadInitialData();
    
  } catch (error) {
    console.error('Logout error:', error);
  }
}

function showMainView() {
  currentUser.textContent = currentEmployee;
  currentStation.textContent = currentWorkstation;
  
  loginView.classList.add('hidden');
  mainView.classList.remove('hidden');
  
  // Load recent scans from storage
  loadRecentScans();
}

async function loadRecentScans() {
  const stored = await chrome.storage.local.get(['recentScans']);
  if (stored.recentScans && stored.recentScans.length > 0) {
    barcodeList.innerHTML = '';
    stored.recentScans.slice(-10).reverse().forEach(scan => {
      const item = document.createElement('div');
      item.className = 'barcode-item';
      item.textContent = scan;
      barcodeList.appendChild(item);
    });
  } else {
    // Show "No scans yet" message
    barcodeList.innerHTML = '<div style="color: #999; text-align: center;">No scans yet</div>';
  }
}

function updateBarcodeDisplay(barcode) {
  // Add to display
  const item = document.createElement('div');
  item.className = 'barcode-item';
  item.textContent = barcode;
  
  // Remove "No scans yet" message if present
  if (barcodeList.children[0]?.style?.color === '#999') {
    barcodeList.innerHTML = '';
  }
  
  barcodeList.insertBefore(item, barcodeList.firstChild);
  
  // Keep only last 10
  while (barcodeList.children.length > 10) {
    barcodeList.removeChild(barcodeList.lastChild);
  }
  
  // Update storage
  chrome.storage.local.get(['recentScans'], result => {
    const scans = result.recentScans || [];
    scans.push(barcode);
    if (scans.length > 50) scans.shift(); // Keep max 50 in storage
    chrome.storage.local.set({recentScans: scans});
  });
}

function showError(message) {
  loginError.textContent = message;
  loginError.classList.remove('hidden');
  setTimeout(() => {
    loginError.classList.add('hidden');
  }, 5000);
}