// electron/main.js
// Configuración segura según SECURITY.md

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const keytar = require('keytar');

const SERVICE_NAME = 'sge-grades-mvp';
const ACCOUNT_NAME = 'auth-token';

let mainWindow = null;

// 🔒 Electron Security Hardening
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 768,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,           // ✅ Previene RCE desde renderer
      contextIsolation: true,            // ✅ Aísla mundo de Electron del mundo web
      enableRemoteModule: false,         // ✅ Remote está deprecado y es inseguro
      sandbox: true,                     // ✅ Sandbox adicional
      webSecurity: true,                 // ✅ No deshabilitar nunca
      allowRunningInsecureContent: false // ✅ Solo HTTPS en producción
    },
    icon: path.join(__dirname, '../assets/icon.png')
  });

  // Desarrollo: cargar localhost
  // Producción: cargar build estático
  const startUrl = process.env.ELECTRON_START_URL || 
                   `file://${path.join(__dirname, '../frontend/build/index.html')}`;
  
  mainWindow.loadURL(startUrl);

  // DevTools solo en desarrollo
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }

  // 🔒 Prevenir navegación externa
  mainWindow.webContents.on('will-navigate', (event, url) => {
    const allowedOrigins = [
      'http://localhost:3000',
      'http://localhost:8000'
    ];
    
    const urlObj = new URL(url);
    const isAllowed = allowedOrigins.some(origin => url.startsWith(origin));
    
    if (!isAllowed && urlObj.protocol !== 'file:') {
      event.preventDefault();
      console.warn(`[Security] Blocked navigation to: ${url}`);
    }
  });

  // 🔒 Prevenir apertura de nuevas ventanas
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    console.warn(`[Security] Blocked new window: ${url}`);
    return { action: 'deny' };
  });

  // 🔒 Content Security Policy
  mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          "default-src 'self'; " +
          "script-src 'self' 'unsafe-inline'; " +  // React necesita inline
          "style-src 'self' 'unsafe-inline'; " +
          "img-src 'self' data:; " +
          "connect-src 'self' http://localhost:8000; " +  // FastAPI local
          "font-src 'self'; " +
          "object-src 'none'; " +
          "base-uri 'self'; " +
          "form-action 'self'; " +
          "frame-ancestors 'none'; " +
          "upgrade-insecure-requests;"
        ]
      }
    });
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// 🔒 IPC Handlers seguros para keytar (tokens)
ipcMain.handle('keytar:setPassword', async (event, account, token) => {
  try {
    await keytar.setPassword(SERVICE_NAME, account, token);
    console.log(`[Keytar] Token guardado para: ${account}`);
    return { success: true };
  } catch (error) {
    console.error('[Keytar] Error guardando token:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('keytar:getPassword', async (event, account) => {
  try {
    const token = await keytar.getPassword(SERVICE_NAME, account);
    return { success: true, token };
  } catch (error) {
    console.error('[Keytar] Error obteniendo token:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('keytar:deletePassword', async (event, account) => {
  try {
    await keytar.deletePassword(SERVICE_NAME, account);
    console.log(`[Keytar] Token eliminado para: ${account}`);
    return { success: true };
  } catch (error) {
    console.error('[Keytar] Error eliminando token:', error);
    return { success: false, error: error.message };
  }
});

// App lifecycle
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// 🔒 Deshabilitar manejo de certificados inválidos
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  event.preventDefault();
  callback(false);  // Rechazar certificados inválidos
  console.error(`[Security] Certificate error for ${url}: ${error}`);
});
