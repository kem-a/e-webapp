#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import shutil

def generate_desktop_file(args, app_dir, home_dir):
    app_name_lower = args.appname.lower()
    desktop_content = f"""[Desktop Entry]
Name={args.appname}
Comment={args.appname} Electron web application wrapper. Github:https://github.com/kem-a/e-webapp
GenericName={args.appname} Electron Application
Terminal=false
Type=Application
Icon={app_name_lower}
Categories=Network;Qt;GTK;
Keywords={args.appname},electron,kemm-a,e-webapp
StartupWMClass=e-webapp-{app_name_lower}
StartupNotify=true
X-GNOME-UsesNotifications=true
Exec={home_dir}/.local/share/e-webapp/e-webapp-{app_name_lower}/{app_name_lower} %U
Actions=Uninstall;

[Desktop Action Uninstall]
Name=Uninstall Application
Exec={home_dir}/.local/bin/uninstall-e-webapp -n {args.appname}
"""

    desktop_file_path = os.path.join(app_dir, f"{args.appname}.desktop")
    with open(desktop_file_path, 'w') as desktop_file:
        desktop_file.write(desktop_content)

    return desktop_file_path

def install_app(args, app_dir, home_dir):
    app_name_lower = args.appname.lower()
    desktop_file_path = generate_desktop_file(args, app_dir, home_dir)

    # Define install paths
    local_applications_dir = os.path.expanduser('~/.local/share/applications')
    e_webapp_dir = os.path.expanduser(f'~/.local/share/e-webapp/e-webapp-{app_name_lower}')
    local_bin_dir = os.path.expanduser('~/.local/bin')

    # Ensure the target directories exist
    os.makedirs(local_applications_dir, exist_ok=True)
    os.makedirs(e_webapp_dir, exist_ok=True)
    os.makedirs(local_bin_dir, exist_ok=True)

    # Define the paths for the .desktop file and app folder in the source directory
    desktop_source_path = desktop_file_path
    app_source_path = os.path.join(app_dir, 'dist', 'linux-unpacked')

    # Define the destination paths
    desktop_destination_path = os.path.join(local_applications_dir, f"{args.appname}.desktop")
    app_destination_path = e_webapp_dir
    uninstall_script_source_path = os.path.join(os.path.dirname(__file__), '../uninstall-e-webapp')
    uninstall_script_destination_path = os.path.join(local_bin_dir, 'uninstall-e-webapp')

    # Copy the .desktop file to ~/.local/share/applications/, overwrite if exists
    if os.path.exists(desktop_destination_path):
        os.remove(desktop_destination_path)
    shutil.copy(desktop_source_path, local_applications_dir)

    # Copy the app folder to ~/.local/share/e-webapp/{app_name}, overwrite if exists
    if os.path.exists(app_destination_path):
        shutil.rmtree(app_destination_path)
    shutil.copytree(app_source_path, app_destination_path)

    # Copy the uninstall script to ~/.local/bin/, overwrite if exists
    if os.path.exists(uninstall_script_destination_path):
        os.remove(uninstall_script_destination_path)
    shutil.copy(uninstall_script_source_path, uninstall_script_destination_path)

    # Change the file permission to executable
    os.chmod(uninstall_script_destination_path, 0o755)

    print(f"{args.appname} installed successfully.")
