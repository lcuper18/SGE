// electron/preload.js
// IPC Bridge seguro para comunicación Electron ↔ React

const { contextBridge, ipcRenderer } = require('electron');

// 🔒 Exponer solo APIs específicas y seguras
contextBridge.exposeInMainWorld('electron', {
  // Keytar para manejo seguro de tokens
  keytar: {
    setPassword: (account, token) => 
      ipcRenderer.invoke('keytar:setPassword', account, token),
    
    getPassword: (account) => 
      ipcRenderer.invoke('keytar:getPassword', account),
    
    deletePassword: (account) => 
      ipcRenderer.invoke('keytar:deletePassword', account)
  },

  // Información del entorno
  env: {
    platform: process.platform,
    isProduction: process.env.NODE_ENV === 'production'
  }
});

console.log('[Preload] IPC Bridge inicializado de forma segura');
