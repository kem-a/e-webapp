#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import datetime
import requests
from bs4 import BeautifulSoup
import json
import sys
from urllib.parse import urljoin, urlparse
from PIL import Image
import shutil

#########################
# UPDATE EASYLIST TXT FILE FOR ADBLOCKER
#####

# Define URL and path variables inside the module
EASYLIST_URL = 'https://easylist.to/easylist/easylist.txt'
EASYLIST_PATH = 'resources/easylist.txt'

def update_easylist_if_needed():
    file_path = EASYLIST_PATH
    url = EASYLIST_URL
    
    if os.path.exists(file_path):
        file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        now = datetime.datetime.now()
        age_days = (now - file_mod_time).days
        
        if age_days > 10:
            print("Updating easylist.txt due to it being older than 10 days...")
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print("easylist.txt has been updated.")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download the new easylist.txt: {e}")
    else:
        print("easylist.txt does not exist. Downloading a new copy...")
        try:
            response = requests.get(url)
            response.raise_for_status()
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print("easylist.txt has been downloaded.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download easylist.txt: {e}")


#########################
# EXTRACT METADATA FROM WEB PAGE
#####

# webpage_meta.json file will b created with four elements
# Title, Comments, Keywords and Icon URL

def try_fetch_manifest_from_root(page_url):
    """Attempts to fetch the manifest.json file directly from the site root."""
    parsed_url = urlparse(page_url)
    root_manifest_url = f"{parsed_url.scheme}://{parsed_url.netloc}/manifest.json"
    try:
        response = requests.get(root_manifest_url)
        if response.status_code == 200:
            print(f"Manifest found at the root: {root_manifest_url}")
            return response.json(), root_manifest_url
    except requests.exceptions.RequestException:
        pass  # If the request fails, move on to searching within the page
    return None, None

def find_manifest_in_page(page_url):
    """Searches the webpage for a manifest link and fetches the manifest."""
    try:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        manifest_link_tag = soup.find('link', attrs={'rel': 'manifest'})
        if manifest_link_tag and 'href' in manifest_link_tag.attrs:
            manifest_url = urljoin(page_url, manifest_link_tag['href'])
            manifest_response = requests.get(manifest_url)
            if manifest_response.status_code == 200:
                print(f"Manifest found in page: {manifest_url}")
                return manifest_response.json(), manifest_url
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the webpage or manifest: {e}")
    return None, None

def fetch_and_save_high_res_icon(manifest, manifest_url):
    """Fetches the highest resolution icon from the manifest and saves it."""
    if manifest and 'icons' in manifest:
        icons = manifest['icons']
        largest_icon = max(icons, key=lambda icon: [int(n) for n in icon['sizes'].split('x', 1)][0] if 'sizes' in icon else 0)
        icon_url = urljoin(manifest_url, largest_icon['src'])
        return icon_url
    else:
        print("No icons found in the manifest.")
    return None

def extract_webpage_metadata(page_url):
    """Extracts title, description, and keywords from the webpage."""
    try:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text if soup.find('title') else ''
        description = soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else ''
        keywords = soup.find('meta', attrs={'name': 'keywords'})['content'] if soup.find('meta', attrs={'name': 'keywords'}) else ''
        
        return title, description, keywords
    except Exception as e:
        print(f"Error extracting webpage metadata: {e}")
        return '', '', ''

def get_webpage_metadata(page_url):
    """Extract webpage metadata and save to webpage_meta.json."""
    print(f"Extracting metadata from: {page_url}")
    
    # Extract basic metadata
    title, description, keywords = extract_webpage_metadata(page_url)
    
    # Try to find manifest and icon
    icon_url = None
    
    # Try manifest from root
    manifest, manifest_url = try_fetch_manifest_from_root(page_url)
    if manifest:
        icon_url = fetch_and_save_high_res_icon(manifest, manifest_url)
    
    # If no manifest icon, try searching in page
    if not icon_url:
        manifest, manifest_url = find_manifest_in_page(page_url)
        if manifest:
            icon_url = fetch_and_save_high_res_icon(manifest, manifest_url)
    
    # If still no icon, try common favicon locations
    if not icon_url:
        parsed_url = urlparse(page_url)
        favicon_urls = [
            f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico",
            f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.png",
            f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.svg"
        ]
        
        for favicon_url in favicon_urls:
            try:
                response = requests.head(favicon_url, timeout=5)
                if response.status_code == 200:
                    icon_url = favicon_url
                    break
            except:
                continue
    
    # Save metadata to file
    metadata = {
        'title': title,
        'description': description,
        'keywords': keywords,
        'icon_url': icon_url or ''
    }
    
    # Get the directory where we should save the metadata
    electron_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    meta_file_path = os.path.join(electron_dir, 'webpage_meta.json')
    
    try:
        with open(meta_file_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Metadata saved to: {meta_file_path}")
        print(f"  Title: {title}")
        print(f"  Icon: {icon_url or 'None'}")
    except Exception as e:
        print(f"Error saving metadata: {e}")

#########################
# ICON SEARCH AND HANDLING FUNCTIONS
#####

def get_system_icon_theme():
    """Get the current system icon theme name."""
    try:
        # Try gsettings first (GNOME/GTK)
        import subprocess
        result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'icon-theme'],
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            theme = result.stdout.strip().strip("'\"")
            if theme and theme != 'Default':
                return theme
    except:
        pass
    
    # Try GTK config file
    gtk_config = os.path.expanduser("~/.config/gtk-3.0/settings.ini")
    if os.path.exists(gtk_config):
        try:
            with open(gtk_config, 'r') as f:
                for line in f:
                    if line.startswith('gtk-icon-theme-name='):
                        theme = line.split('=', 1)[1].strip()
                        if theme:
                            return theme
        except:
            pass
    
    # Default fallback
    return "hicolor"

def get_comprehensive_search_paths(theme_name):
    """Generate comprehensive search paths for icons with scalable first."""
    search_paths = []
    
    # Base icon directories
    base_dirs = [
        "/usr/share/icons",
        "/usr/local/share/icons", 
        os.path.expanduser("~/.local/share/icons"),
        os.path.expanduser("~/.icons")
    ]
    
    # Icon sizes in order of preference (largest first)
    sizes = ["512x512", "256x256", "128x128", "96x96", "64x64", "48x48", "32x32", "24x24", "16x16"]
    
    # Categories to search
    categories = ["apps", "applications", "places", "mimetypes", "devices", "status"]
    
    # 1. Current theme paths - SCALABLE FIRST
    for base_dir in base_dirs:
        theme_dir = os.path.join(base_dir, theme_name)
        if os.path.exists(theme_dir):
            # Scalable paths FIRST (higher priority)
            for category in categories:
                search_paths.append(os.path.join(theme_dir, "scalable", category))
            # Then size-specific paths
            for size in sizes:
                for category in categories:
                    search_paths.append(os.path.join(theme_dir, size, category))
    
    # 2. Hicolor fallback (universal theme) - SCALABLE FIRST
    if theme_name != "hicolor":
        for base_dir in base_dirs:
            hicolor_dir = os.path.join(base_dir, "hicolor")
            if os.path.exists(hicolor_dir):
                # Scalable paths FIRST
                for category in categories:
                    search_paths.append(os.path.join(hicolor_dir, "scalable", category))
                # Then size-specific paths
                for size in sizes:
                    for category in categories:
                        search_paths.append(os.path.join(hicolor_dir, size, category))
    
    # 3. Legacy pixmaps paths
    search_paths.extend([
        "/usr/share/pixmaps",
        os.path.expanduser("~/.local/share/pixmaps")
    ])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_paths = []
    for path in search_paths:
        if path not in seen:
            seen.add(path)
            unique_paths.append(path)
    
    return unique_paths

def find_app_icon_comprehensive(app_name, search_paths):
    """Find application icon with comprehensive pattern matching."""
    app_variants = [
        app_name.lower(),
        app_name.lower().replace('_', '-'),
        app_name.lower().replace('-', '_'),
        app_name.lower().replace(' ', '-'),
        app_name.lower().replace(' ', '_'),
    ]
    
    # Remove duplicates
    app_variants = list(set(app_variants))
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
            
        try:
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    file_lower = file.lower()
                    file_base = os.path.splitext(file_lower)[0]
                    
                    # Check various matching patterns
                    for variant in app_variants:
                        # Exact match
                        if file_base == variant:
                            return os.path.join(root, file)
                        
                        # Starts with variant
                        if file_base.startswith(variant + '-'):
                            return os.path.join(root, file)
                        
                        if file_base.startswith(variant + '_'):
                            return os.path.join(root, file)
                        
                        # Contains variant (for complex names)
                        if variant in file_base and len(variant) > 3:
                            return os.path.join(root, file)
                            
        except (OSError, PermissionError):
            continue
    
    return None

def download_web_icon(icon_url, target_path):
    """Download icon from web with proper error handling."""
    try:
        response = requests.get(icon_url, timeout=10, stream=True)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if not any(img_type in content_type for img_type in ['image/', 'application/octet-stream']):
            return False
            
        # Check content length (avoid very small or huge files)
        content_length = response.headers.get('content-length')
        if content_length:
            size = int(content_length)
            if size < 100 or size > 10*1024*1024:  # < 100 bytes or > 10MB
                return False
        
        # Download and save
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Verify the downloaded file is actually an image
        try:
            with Image.open(target_path) as img:
                img.verify()
            return True
        except:
            # Not a valid image, remove it
            if os.path.exists(target_path):
                os.remove(target_path)
            return False
            
    except Exception as e:
        print(f"Failed to download web icon: {e}")
        return False

def get_app_icon(app_name, electron_dir, app_dir):
    """Main function to get application icon with improved search order."""
    import cairosvg
    
    target_icon_path = os.path.join(app_dir, 'icon.png')
    default_icon_path = os.path.join(electron_dir, 'src', 'assets', 'default.png')
    
    print(f"Searching for icon for '{app_name}'...")
    
    # Step 1: Search in system icon themes
    print("Step 1: Searching system icon themes...")
    current_theme = get_system_icon_theme()
    print(f"Current icon theme: {current_theme}")
    
    search_paths = get_comprehensive_search_paths(current_theme)
    print(f"Searching in {len(search_paths)} locations...")
    
    found_icon = find_app_icon_comprehensive(app_name, search_paths)
    if found_icon:
        print(f"✓ Found system icon: {found_icon}")
        
        # Convert if needed
        if not found_icon.lower().endswith('.png'):
            try:
                # Convert to PNG
                if not os.path.exists(app_dir):
                    os.makedirs(app_dir, exist_ok=True)
                cairosvg.svg2png(url=found_icon, write_to=target_icon_path)
                print(f"✓ Icon converted to PNG: {target_icon_path}")
                return True
            except Exception as e:
                print(f"Failed to convert icon: {e}")
                # Fall through to copy as-is
                pass
        
        # Copy PNG directly
        shutil.copy(found_icon, target_icon_path)
        print(f"✓ Icon copied to: {target_icon_path}")
        return True
    
    print("✗ No system icon found")
    
    # Step 2: Try web page icon (using original working logic)
    print("Step 2: Searching web page for icon...")
    meta_file_path = os.path.join(electron_dir, 'webpage_meta.json')
    
    if os.path.exists(meta_file_path):
        try:
            with open(meta_file_path, 'r') as f:
                meta_data = json.load(f)
            
            icon_url = meta_data.get('icon_url', '')
            if icon_url:
                print(f"Found web icon URL: {icon_url}")
                if download_web_icon(icon_url, target_icon_path):
                    print("✓ Web icon downloaded successfully")
                    return True
                else:
                    print("✗ Web icon download failed")
        except Exception as e:
            print(f"Error reading web metadata: {e}")
    
    print("✗ No web icon found")
    
    # Step 3: Use default fallback
    print("Step 3: Using default fallback icon...")
    if os.path.exists(default_icon_path):
        shutil.copy(default_icon_path, target_icon_path)
        print(f"✓ Default icon copied to: {target_icon_path}")
        return True
    else:
        print("✗ Default icon not found!")
        return False

#########################
# GET ICON FROM WEB PAGE OR COPY DEFAULT
#####

# Note: Icon handling has been moved to the main e-webapp script for better integration
# with the comprehensive search system. This function is kept for backward compatibility
# but is no longer used in the main workflow.

def get_default_icon(electron_dir, app_dir, template_dir):
    # Path to search for 'webpage_meta.json'
    meta_file_path = os.path.join(electron_dir, 'webpage_meta.json')
    icon_path = os.path.join(app_dir, 'icon.png')
    default_icon_path = os.path.join(electron_dir, 'src', 'assets', 'default.png')

    if os.path.exists(meta_file_path):
        with open(meta_file_path, 'r') as meta_file:
            meta_data = json.load(meta_file)
        icon_url = meta_data.get('icon_url', '')

        if icon_url:
            print(f"Downloading icon from {icon_url}")
            try:
                response = requests.get(icon_url)
                response.raise_for_status()  # Check if the request was successful
                with open(icon_path, 'wb') as f:
                    f.write(response.content)
                print("Icon downloaded and saved.")
                return
            except requests.RequestException as e:
                print(f"Failed to download the icon: {e}")

    # If icon_url is empty or download failed, use the default icon
    print("Using the default icon.")
    shutil.copy(default_icon_path, icon_path)
