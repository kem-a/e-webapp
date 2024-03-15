# Electron Web Wrapper Application

This project provides a script to create a web wrapper application using Electron. It's designed to encapsulate a web address into a standalone desktop application, enhancing usability and integration with desktop environments.

## Features

- **Web to Desktop Conversion**: Easily convert any web address into a desktop application.
- **Custom User Agent**: Choose between Chrome, Edge, and Safari user agents for web requests.
- **Ad Blocker**: Integrate an ad blocker to improve browsing experience within the app.
- **Native notifications**: Supports native desktop notifications.
- **Custom CSS/JS Injection**: Ability to inject custom CSS and JavaScript for personalized app appearances and functionality.
- **Tray Icon**: Option to add a tray icon for easy access and control.
- **Single Instance Enforcement**: Ensure only a single instance of the application runs at a time.
- **Desktop Integration**: Automatically generates `.desktop` file for Linux desktop environments, including an optional uninstall action if [uninstall_appimage](https://github.com/kem-a/uninstall_appimage) binary is found in the `$PATH`.

## Prerequisites

- Python 3
- Node.js and npm
- Electron and Electron-builder
- cairosvg (for icon conversion)

## Setup and Installation

1. **Clone the Repository**: Start by cloning this repository to your local machine.

   ```sh
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install Dependencies**: Make sure you have Node.js and npm installed, then run:

   ```sh
   npm install
   ```

3. **Running the Script**: Use the script to build your Electron app with the desired web address and app name.

   ```sh
   ./e-webapp --webaddress "https://example.com" --appname "ExampleApp" --install
   ```

   Replace `https://example.com` with the web address you want to wrap and `"ExampleApp"` with your desired application name.

## Command Line Arguments

The script supports various command line arguments to customize the application build:

- `-w`, `--webaddress`: **Required**. The web address to wrap into a desktop application.
- `-n`, `--appname`: **Required**. The name of the application.
- `-i`, `--icon`: Path to the application icon (PNG only).
- `-t`, `--trayicon`: Path to the tray icon (PNG only, optional).
- `-u`, `--user-agent`: User agent for the web requests (options: firefox, chrome, edge, safari, honest; default: chrome).
- `-c`, `--inject-css`: Inject custom CSS (boolean, optional).
- `-j`, `--inject-js`: Inject custom JavaScript (boolean, optional).
- `-b`, `--adblocker`: Enable the ad blocker (default: disabled).
- `-e`, `--main-menu`: Hide the main app menu, can be unhidden with Alt (default: disabled).
- `-m`, `--context-menu`: Disable the context menu (default: enabled).
- `-s`, `--single-instance`: Enable single instance mode (boolean, optional).
- `--wayland`: Force Wayland window rendering.
- `--install`: Build and install the AppImage and desktop file (Linux only).
- `--debug`: Keep the build directory for debugging.

For more detailed information on each argument, type `--help` when running the script.

## Building the AppImage

After running the script with the `--install` flag, an AppImage and a `.desktop` file for your application will be generated. You can find these in the `~/Applications` and `~/.local/share/applications/` directories, respectively.

## Debugging

Pass the `--debug` flag to keep the build directory for debugging purposes.

## Known Bugs and Issues

* screen sharing does not work (would appreciate if someone can help me with this)
* some web site notifications won't work due to custom implementation, like outlook.com or icloud.com
* new windows from links open with default menus that action main menu, like quit will quit entire app not just new window
* no proper internal url handling

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements or suggestions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
