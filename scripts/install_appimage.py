#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import shutil
import subprocess

####################
# PREPARING APPIMAGE FOLDER
######

# check for uninstall_appimage binary in $PATH to integrate uninstall function
def uninstall_appimage_exists():
    for path in os.environ["PATH"].split(os.pathsep):
        full_path = os.path.join(path, "uninstall_appimage")
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return True
    return False

def prepare_appimage_folder(args, electron_dir, app_dir, home_dir):
    app_name_lower = args.appname.lower()

    # Directory paths
    app_dir_path = os.path.join(app_dir, app_name_lower)
    appimage_dir = f"{app_name_lower}.AppDir"
    usr_dir = os.path.join(appimage_dir, 'usr')
    bin_dir = os.path.join(usr_dir, 'bin')
    lib64_dir = os.path.join(usr_dir, 'lib64')

    # Create directories
    os.makedirs(bin_dir, exist_ok=True)

    # Move 'dist/linux-unpacked' to '{appName}.AppDir/usr' and rename it to 'lib64'
    dist_path = os.path.join(app_dir, 'dist', 'linux-unpacked')
    os.rename(dist_path, lib64_dir)

    # Create symlink in 'bin' folder
    os.symlink(os.path.join('..', 'lib64', app_name_lower), os.path.join(bin_dir, app_name_lower))

    # Copy 'AppRun' to AppDir
    shutil.copy(os.path.join(electron_dir, 'build', 'AppRun'), appimage_dir)

    # Copy and rename icon
    shutil.copy(os.path.join(app_dir, 'icon.png'), os.path.join(appimage_dir, f"{app_name_lower}.png"))

    # Create desktop file content within AppDir
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
Exec={app_name_lower} %U
"""

    desktop_file_path = os.path.join(appimage_dir, f"{args.appname}.desktop")
    with open(desktop_file_path, 'w') as desktop_file:
        desktop_file.write(desktop_content)

    # Prepare Desktop file that will be installed in user home directory
    # Copy the desktop file to the current app directory
    desktop_file_dest_path = os.path.join(app_dir, f"{args.appname}.desktop")
    shutil.copy(desktop_file_path, desktop_file_dest_path)

    # Check for the uninstall_appimage binary and prepare the uninstall action content if necessary
    uninstall_option = ""
    if uninstall_appimage_exists():
        uninstall_option = f"""
Actions=Uninstall;

[Desktop Action Uninstall]
Name=Uninstall Application
Exec=uninstall_appimage {args.appname}
"""

    # Read and modify the existing .desktop file content
    with open(desktop_file_dest_path, 'r') as file:
        lines = file.readlines()

    # Remove any existing Exec= lines
    lines = [line for line in lines if not line.startswith('Exec=')]

    # Define the new Exec line based on the --wayland argument
    exec_line = f"Exec={home_dir}/Applications/e-webapp-{app_name_lower}.AppImage %U\n"
    if args.wayland:
        exec_line = f"Exec={home_dir}/Applications/e-webapp-{app_name_lower}.AppImage --enable-features=UseOzonePlatform,WaylandWindowDecorations --ozone-platform-hint=auto --no-sandbox %U\n"

    # Append the new Exec line
    lines.append(exec_line)

    # Append the uninstall action if applicable
    if uninstall_option:
        lines.append(uninstall_option)

    # Write the modified content back to the .desktop file
    with open(desktop_file_dest_path, 'w') as file:
        file.writelines(lines)

def build_and_deploy_appimage(args, electron_dir, app_dir):
    app_name_lower = args.appname.lower()
    appimage_dir = f"{app_name_lower}.AppDir"
    appimage_file_name = f"e-webapp-{app_name_lower}.AppImage"

    # Build the AppImage
    os.chdir(app_dir)
    appimagetool_path = os.path.join(electron_dir, 'build', 'appimagetool') 
    subprocess.run([appimagetool_path, appimage_dir, os.path.join(app_dir, appimage_file_name)], check=True)

    # Define install paths
    applications_dir = os.path.expanduser('~/Applications')
    local_applications_dir = os.path.expanduser('~/.local/share/applications')

    # Ensure the target directories exist
    os.makedirs(applications_dir, exist_ok=True)
    os.makedirs(local_applications_dir, exist_ok=True)

    # Define the paths for the AppImage and .desktop file in the source directory
    appimage_source_path = os.path.join(app_dir, appimage_file_name)
    desktop_source_path = os.path.join(app_dir, f"{args.appname}.desktop")

    # Define the destination paths
    appimage_destination_path = os.path.join(applications_dir, appimage_file_name)
    desktop_destination_path = os.path.join(local_applications_dir, f"{args.appname}.desktop")

    # Move the AppImage to ~/Applications, overwrite if exists
    if os.path.exists(appimage_destination_path):
        os.remove(appimage_destination_path)
    shutil.move(appimage_source_path, applications_dir)

    # Move the desktop file to ~/.local/share/applications/, overwrite if exists
    if os.path.exists(desktop_destination_path):
        os.remove(desktop_destination_path)
    shutil.move(desktop_source_path, local_applications_dir)

    print(f"{args.appname} installed successfully.")

def handle_debug(args, app_dir):
    if args.install_appimage and not args.debug:
        # Delete the entire {appName} directory and all its content
        shutil.rmtree(app_dir)
    else:
        if args.debug:
            print(f"Debug mode is active. The directory {app_dir} will not be deleted.")