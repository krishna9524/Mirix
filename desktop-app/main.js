const { app, BrowserWindow, ipcMain, shell, Menu, session } = require('electron');
const path = require('path');
const axios = require('axios');

// --- API Base URL ---
const API_URL = 'http://127.0.0.1:8000/api/v1';

// --- Create Browser Window ---
function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadURL('http://localhost:3000');
  win.webContents.openDevTools();

  // Enable pinch-to-zoom
  win.webContents.setVisualZoomLevelLimits(1, 3);

  win.webContents.on('zoom-changed', (event, zoomDirection) => {
    const currentZoom = win.webContents.getZoomLevel();
    console.log(`Zoom ${zoomDirection}:`, currentZoom);
  });
}

// --- IPC Handlers ---
ipcMain.handle('api-query-memory', async (event, query) => {
  try {
    const response = await axios.post(`${API_URL}/query-memory`, { query });
    return response.data;
  } catch (error) {
    console.error('API Error (Query Memory):', error.message);
    return { error: error.message };
  }
});

ipcMain.handle('open-file', async (event, fileUrl) => {
  try {
    await shell.openExternal(fileUrl);
    return { success: true };
  } catch (err) {
    console.error('❌ Failed to open file:', err.message);
    return { success: false, error: err.message };
  }
});

ipcMain.handle('api-generate-title', async (event, messageHistory) => {
  try {
    const response = await axios.post(`${API_URL}/generate-title`, {
      messages: messageHistory,
    });
    return response.data;
  } catch (error) {
    console.error('API Error (Title Gen):', error.message);
    return { title: "New Chat" };
  }
});

// This is a legacy handler, not used by the new 'fetch' streaming
ipcMain.on('stop-generation', () => {
  console.log('Main: Received stop-generation signal (legacy)');
});


// --- App Lifecycle ---
app.whenReady().then(() => {
  console.log('🚀 App ready');

  // --- *** THIS IS THE FIX *** ---
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          [
            "default-src 'self' http://localhost:3000 http://127.0.0.1:8000",
            
            // --- THIS RULE IS NOW CORRECT ---
            // We must add the CDN to the script-src
            "script-src 'self' http://localhost:3000 'unsafe-eval' http://cdnjs.cloudflare.com",
            // --- END OF FIX ---
            
            "style-src 'self' 'unsafe-inline' http://localhost:3000",
            "connect-src 'self' http://127.0.0.1:8000",
            "frame-src 'self' blob:",
            "object-src 'self' blob: http://127.0.0.1:8000"
          ].join('; ')
        ]
      }
    });
  });
  // --- *** END OF CSP BLOCK *** ---

  createWindow();

  // --- Menu Code ---
  const menuTemplate = [
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        {
          label: 'Zoom In',
          accelerator: 'CmdOrCtrl+=',
          click: (menuItem, browserWindow) => {
            if (browserWindow) {
              const webContents = browserWindow.webContents;
              const currentZoom = webContents.getZoomLevel();
              webContents.setZoomLevel(currentZoom + 0.2);
            }
          }
        },
        {
          label: 'Zoom Out',
          accelerator: 'CmdOrCtrl+-',
          click: (menuItem, browserWindow) => {
            if (browserWindow) {
              const webContents = browserWindow.webContents;
              const currentZoom = webContents.getZoomLevel();
              if (currentZoom > -9.9) {
                webContents.setZoomLevel(currentZoom - 0.2);
              }
            }
          }
        },
        {
          label: 'Reset Zoom',
          accelerator: 'CmdOrCtrl+0',
          click: (menuItem, browserWindow) => {
            if (browserWindow) {
              browserWindow.webContents.setZoomLevel(0);
            }
          }
        },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      role: 'windowMenu'
    }
  ];

  if (process.platform === 'darwin') {
    menuTemplate.unshift({ role: 'appMenu' });
    menuTemplate.push({ role: 'editMenu' });
  }

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});