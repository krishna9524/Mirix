const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('mirixApi', {
  // --- REMOVED 'sendChat' ---

  queryMemory: (query) => 
    ipcRenderer.invoke('api-query-memory', query),

  openFile: (fileUrl) => 
    ipcRenderer.invoke('open-file', fileUrl),

  generateTitle: (messageHistory) => 
    ipcRenderer.invoke('api-generate-title', messageHistory),

  // --- REMOVED 'stopGeneration' ---
});