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
        return {'title': title, 'description': description, 'keywords': keywords}
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the webpage: {e}")
        return {}

def get_webpage_metadata(page_url):

    metadata = extract_webpage_metadata(page_url)
    manifest, manifest_url = try_fetch_manifest_from_root(page_url)
    if not manifest:
        manifest, manifest_url = find_manifest_in_page(page_url)
    
    icon_url = None
    if manifest:
        icon_url = fetch_and_save_high_res_icon(manifest, manifest_url)

    metadata['icon_url'] = icon_url or ""
    with open('webpage_meta.json', 'w') as file:
        json.dump(metadata, file, indent=4, ensure_ascii=False)


#########################
# GET ICON FROM WEB PAGE OR COPY DEFAULT
#####

def get_default_icon(electron_dir, app_dir, template_dir):
    # Path to search for 'webpage_meta.json'
    meta_file_path = os.path.join(electron_dir, 'webpage_meta.json')
    icon_path = os.path.join(app_dir, 'icon.png')
    default_icon_path = os.path.join(electron_dir, 'src', 'assets/' 'default.png')

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
