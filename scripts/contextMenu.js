const { Menu, MenuItem, shell, clipboard } = require('electron');

function buildContextMenu(mainWindow) {
  mainWindow.webContents.on('context-menu', (event, params) => {
    const contextMenu = new Menu();

    if (params.isEditable) {
      // Context menu for text box
      if (params.misspelledWord) {
        params.dictionarySuggestions.forEach((suggestion) => {
          contextMenu.append(new MenuItem({
            label: suggestion,
            click: () => mainWindow.webContents.replaceMisspelling(suggestion)
          }));
        });
        // Add the 'Add to Dictionary' option if there's a misspelled word.
        if (params.misspelledWord) {
          contextMenu.append(new MenuItem({ 
            label: 'Add to Dictionary', 
            click: () => mainWindow.webContents.session.addWordToSpellCheckerDictionary(params.misspelledWord) 
          }));
        }
        contextMenu.append(new MenuItem({ type: 'separator' }));
      }
      contextMenu.append(new MenuItem({ label: 'Undo', role: 'undo', accelerator: 'CmdOrCtrl+Z' }));
      contextMenu.append(new MenuItem({ label: 'Redo', role: 'redo', accelerator: 'CmdOrCtrl+Y' }));
      contextMenu.append(new MenuItem({ type: 'separator' }));
      contextMenu.append(new MenuItem({ label: 'Cut', role: 'cut', accelerator: 'CmdOrCtrl+X' }));
      contextMenu.append(new MenuItem({ label: 'Copy', role: 'copy', accelerator: 'CmdOrCtrl+C' }));
      contextMenu.append(new MenuItem({ label: 'Paste', role: 'paste', accelerator: 'CmdOrCtrl+V' }));
      contextMenu.append(new MenuItem({ label: 'Delete', role: 'delete' })); // No default accelerator
      contextMenu.append(new MenuItem({ label: 'Select All', role: 'selectAll', accelerator: 'CmdOrCtrl+A' }));
    } else {
      // Context menu for general page
      contextMenu.append(new MenuItem({ label: 'Back', click: () => mainWindow.webContents.goBack(), accelerator: 'Alt+Left' }));
      contextMenu.append(new MenuItem({ label: 'Forward', click: () => mainWindow.webContents.goForward(), accelerator: 'Alt+Right' }));
      contextMenu.append(new MenuItem({ label: 'Reload', click: () => mainWindow.webContents.reload(), accelerator: 'CmdOrCtrl+R' }));
      contextMenu.append(new MenuItem({ type: 'separator' }));
      contextMenu.append(new MenuItem({ label: 'Copy', role: 'copy', accelerator: 'CmdOrCtrl+C' }));
      contextMenu.append(new MenuItem({ label: 'Copy Link', click: () => clipboard.writeText(mainWindow.webContents.getURL()) })); // No default accelerator
      contextMenu.append(new MenuItem({ label: 'Open Link in Browser', click: () => shell.openExternal(mainWindow.webContents.getURL()) })); // No default accelerator
      contextMenu.append(new MenuItem({ label: 'Open page in Browser', click: () => shell.openExternal(mainWindow.webContents.getURL()) })); // No default accelerator
    }

    contextMenu.popup({
      window: mainWindow,
      x: params.x,
      y: params.y
    });
  });
}

module.exports = buildContextMenu;
