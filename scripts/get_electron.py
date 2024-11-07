#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import tempfile

# Constants
TEMP_NODE_MODULES = os.path.join(tempfile.gettempdir(), 'ewebapp_node_modules')

def check_npm():
    """Check if npm is available on the system"""
    return shutil.which('npm') is not None

def check_toolbox_npm():
    """Check if npm is available in toolbox"""
    try:
        result = subprocess.run(['toolbox', 'run', 'which', 'npm'], stdout=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False

def setup_electron(app_dir, electron_version=None):
    """Setup electron and required npm packages"""
    # Ensure temp directory exists
    os.makedirs(TEMP_NODE_MODULES, exist_ok=True)

    # Setup electron version
    electron_version = f"@{electron_version}" if electron_version else "@latest"
    npm_commands = [
        f"npm install electron{electron_version} --save-dev",
        "npm install electron-builder --save-dev",
        "npm install --save electron-window-state",
        "npm install --save @ghostery/adblocker-electron"
    ]

    # Check for npm availability
    if check_npm():
        print("npm exists on host system.")
    elif check_toolbox_npm():
        print("npm exists in toolbox.")
        npm_commands = ["toolbox run " + cmd for cmd in npm_commands]
    else:
        raise RuntimeError("npm does not exist on host system or in toolbox. Please install npm and nodejs.")

    # Install packages in temp directory if needed
    for cmd in npm_commands:
        subprocess.run(cmd, shell=True, cwd=TEMP_NODE_MODULES, check=True)

    return TEMP_NODE_MODULES