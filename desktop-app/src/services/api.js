import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Smart wrapper for querying memory
export const queryMemory = async (query) => {
  // Check if we are running inside Electron
  if (window.mirixApi && window.mirixApi.queryMemory) {
    return await window.mirixApi.queryMemory(query);
  } 
  
  // Fallback for standard web browser
  const response = await apiClient.post('/query-memory', { query: query });
  return response.data;
};

// Smart wrapper for generating titles
export const generateTitle = async (messageHistory) => {
  if (window.mirixApi && window.mirixApi.generateTitle) {
    return await window.mirixApi.generateTitle(messageHistory);
  }
  
  const response = await apiClient.post('/generate-title', { messages: messageHistory });
  return response.data;
};

// Smart wrapper for opening files
export const openFile = (fileUrl) => {
  if (window.mirixApi && window.mirixApi.openFile) {
    return window.mirixApi.openFile(fileUrl);
  }
  
  // Browsers cannot open local desktop files directly due to security sandboxing.
  // Instead, we just open the file's backend URL in a new browser tab.
  window.open(fileUrl, '_blank');
};