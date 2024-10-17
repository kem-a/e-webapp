// inject.js
const { remote } = require('electron');
const currentWindow = remote.getCurrentWindow();

// Adjust the height of the window
const [width, height] = currentWindow.getSize();
currentWindow.setSize(width, height - 20);

