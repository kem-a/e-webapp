const { shell, app, session, Menu, clipboard } = require('electron');

function setApplicationMenu(mainWindow) {
    const template = [
        {
            label: 'File',
            submenu: [
                {
                    label: 'Open App in Default Browser',
                    click: () => shell.openExternal(mainWindow.webContents.getURL()),
                    accelerator: 'CmdOrCtrl+Shift+O' // Custom accelerator
                },
                { role: 'quit', accelerator: 'CmdOrCtrl+Q' } // Quit accelerator provided by role
            ]
        },
        {
            label: 'Edit',
            submenu: [
                { role: 'undo' },
                { role: 'redo' },
                { type: 'separator' },
                { role: 'cut' },
                { role: 'copy' },
                {
                    label: 'Copy as Plain Text',
                    click: () => mainWindow.webContents.copy(), // Custom copy as plain text action
                    accelerator: 'CmdOrCtrl+Shift+C' // Custom accelerator
                },
                {
                    label: 'Copy Current URL',
                    click: () => clipboard.writeText(mainWindow.webContents.getURL()),
                    accelerator: 'CmdOrCtrl+L' // Custom accelerator for copying URL
                },
                { role: 'paste' },
                { type: 'separator' },
                { role: 'selectAll' }
            ]
        },
        {
            label: 'View',
            submenu: [
                { label: 'Back', click: () => mainWindow.webContents.goBack(), accelerator: 'Alt+Left' },
                { label: 'Forward', click: () => mainWindow.webContents.goForward(), accelerator: 'Alt+Right' },
                { role: 'reload', accelerator: 'CmdOrCtrl+R' },
                { type: 'separator' },
                { role: 'zoomIn', accelerator: 'CmdOrCtrl+=' },
                { role: 'zoomOut', accelerator: 'CmdOrCtrl+-' },
                { role: 'resetZoom', accelerator: 'CmdOrCtrl+0' },
                { type: 'separator' },
                { role: 'togglefullscreen', accelerator: 'F11' } // Fullscreen toggle accelerator
            ]
        },
        {
            label: 'Tools',
            submenu: [
                {
                    label: 'Reset Application',
                    click: () => {
                        session.defaultSession.clearStorageData(); // Clear app cache and data
                        app.relaunch(); // Relaunch the app
                        app.exit(); // Exit the app
                    },
                    accelerator: 'CmdOrCtrl+Shift+R' // Custom accelerator for resetting app
                },
                { role: 'toggleDevTools', accelerator: 'CmdOrCtrl+Shift+I' } // Dev tools toggle accelerator
            ]
        },
        {
            label: 'Help',
            submenu: [
                {
                    label: 'About',
                    click: () => {
                        // Code to open a small about window
                    }
                },
                {
                    label: 'Report an Issue',
                    click: () => shell.openExternal('https://github.com/AI-ien/nativefier'),
                    accelerator: 'CmdOrCtrl+Shift+I' // Custom accelerator for reporting an issue
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}
module.exports = setApplicationMenu;
