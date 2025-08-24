const { app, BrowserWindow, Tray, session, Menu, shell } = require('electron');
const windowStateKeeper = require('electron-window-state');
const { ElectronBlocker } = require('@ghostery/adblocker-electron');
const path = require('path');
const fs = require('fs');
const blocker = ElectronBlocker.parse(fs.readFileSync(path.join(__dirname, 'resources', 'easylist.txt'), 'utf-8'));
const buildContextMenu = require(path.join(__dirname, 'scripts', 'contextMenu.js'));
const setApplicationMenu = require(path.join(__dirname, 'scripts', 'menu.js'));
const config = require(path.join(__dirname, 'config.js'));

// PARAMETERS
let enforceSingleInstance = config.enforceSingleInstance;     // Set this variable to control the single instance lock
if (config.trayIconName) { enforceSingleInstance = true };        // Force single instance if tray icon is enabled

const userAgents = {
  chrome: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
  edge: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.3405.111',
  firefox: 'Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0',
  safari: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 15_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15',
};
// Set a global custom user agent for the entire app
if (config.userAgentString !== "honest") {
  app.userAgentFallback = userAgents[config.userAgentString] || userAgents.chrome;
};

let mainWindow;
let tray = null;
let appID = 'e-webapp-' + config.appName.toLowerCase();

// Set a custom userData path
app.setPath('userData', path.join(app.getPath('appData'), appID));

let gotTheLock = true;
if (enforceSingleInstance) {
  gotTheLock = app.requestSingleInstanceLock();
  if (!gotTheLock) {
    app.quit();
  } else {
    app.on('second-instance', () => {
      if (mainWindow) {
        if (!mainWindow.isVisible()) {
          mainWindow.show();
        } else if (mainWindow.isMinimized()) {
          mainWindow.restore();
        }
        mainWindow.focus();
      }
    });
  }
}

app.on('ready', () => {
  // Load the previous state with fallback to defaults
  let mainWindowState = windowStateKeeper({
    defaultWidth: 1000,
    defaultHeight: 800
  });

  mainWindow = new BrowserWindow({
    x: mainWindowState.x,
    y: mainWindowState.y,
    width: mainWindowState.width,
    height: mainWindowState.height,
    autoHideMenuBar: config.mainMenuHidden,
    webPreferences: {
      sandbox: true,
      plugins: true,
      nodeIntegration: false,
      contextIsolation: true,
      nativeWindowOpen: true,
    }
  });

  setApplicationMenu(mainWindow);
  if (config.shouldShowContextMenu) { buildContextMenu(mainWindow) };
  if (config.enableAdBlocker) { blocker.enableBlockingInSession(session.defaultSession) };

  mainWindowState.manage(mainWindow);
  mainWindow.loadURL(config.webPath);


  // Tray icon implementation
  if (config.trayIconName) {
    tray = new Tray(path.join(__dirname, config.trayIconName));
    const contextMenu = Menu.buildFromTemplate([
      { label: 'Show App', click: () => mainWindow.show() },
      {
        label: 'Quit', click: () => {
          app.isQuiting = true;
          app.quit();
        }
      }
    ]);
    tray.setToolTip(config.appName);
    tray.setContextMenu(contextMenu);
    tray.on('click', () => {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
      }
    });
    // If tray is enabled then hide main window instead of quit
    mainWindow.on('close', (event) => {
      if (!app.isQuiting) {
        event.preventDefault();
        mainWindow.hide();
      } else {
        mainWindow = null;
      }
    });
  }

  mainWindow.webContents.on('did-finish-load', () => {
    // Inject custom CSS file
    if (config.injectCustomCSS) {
      fs.readFile(path.join(__dirname, 'resources', 'custom.css'), 'utf-8', (error, data) => {
        if (!error) {
          mainWindow.webContents.insertCSS(data)
        } else {
          console.log(error)
        }
      });
    }
  });

  // Inject custom JavaScript file
  if (config.injectCustomJS) {
    fs.readFile(path.join(__dirname, 'resources', 'custom.js'), 'utf-8', (error, data) => {
      if (!error) {
        mainWindow.webContents.executeJavaScript(data);
      } else {
        console.log(error);
      }
    });
  }

});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
