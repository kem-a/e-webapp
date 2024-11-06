#!/usr/bin/env python3
import os
import sys
import subprocess
import requests
import time
from datetime import datetime
import stat

def download_runtime(runtime_url, runtime_path, build_dir):
    """Download the AppImage runtime if a newer version is available."""
    print("Checking for latest AppImage runtime...")
    
    os.makedirs(build_dir, exist_ok=True)
    
    response = requests.head(runtime_url)
    remote_last_modified = response.headers.get('Last-Modified')
    if remote_last_modified is None:
        return True
    remote_time = datetime.strptime(remote_last_modified, '%a, %d %b %Y %H:%M:%S %Z').timestamp()

    if os.path.exists(runtime_path):
        local_time = os.path.getmtime(runtime_path)
        if remote_time > local_time:
            print("A newer runtime is available. Downloading...")
            download_file = True
        else:
            print(f"Using existing runtime in {build_dir}.")
            download_file = False
    else:
        print("Downloading AppImage runtime...")
        download_file = True
        
    if download_file:
        response = requests.get(runtime_url)
        with open(runtime_path, 'wb') as f:
            f.write(response.content)

def build_appimage(appdir_path, output_file, build_dir):
    """Build an AppImage from an input directory."""
    RUNTIME_URL = "https://github.com/AppImage/type2-runtime/releases/download/continuous/runtime-x86_64"
    RUNTIME_PATH = os.path.join(build_dir, "runtime-x86_64")
    SQUASHFS_FILE = os.path.join(build_dir, "app.squashfs")

    # Download runtime if necessary
    download_runtime(RUNTIME_URL, RUNTIME_PATH, build_dir)

    # Create SquashFS filesystem
    print("Creating SquashFS filesystem with gzip compression...")
    subprocess.run([
        "mksquashfs",
        appdir_path,
        SQUASHFS_FILE,
        "-comp",
        "gzip"
    ], check=True)

    # Combine runtime and SquashFS to create AppImage
    print("Generating AppImage...")
    with open(output_file, 'wb') as outfile:
        with open(RUNTIME_PATH, 'rb') as runtime:
            outfile.write(runtime.read())
        with open(SQUASHFS_FILE, 'rb') as squashfs:
            outfile.write(squashfs.read())

    # Make output file executable
    os.chmod(output_file, os.stat(output_file).st_mode | stat.S_IEXEC)

    # Clean up
    os.remove(SQUASHFS_FILE)

    print(f"AppImage created successfully: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input-directory> <output-file>")
        sys.exit(1)
        
    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    build_dir = "build"
    
    build_appimage(input_dir, output_file, build_dir)