import os
import re
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

ASSETS_DIR = "assets"
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def download_file(url, target_path):
    if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
        return True
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            with open(target_path, "wb") as f:
                f.write(data)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def main():
    print("Reading raw_fudali.html...")
    with open("raw_fudali.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Download images
    print("Collecting and downloading images...")
    img_map = {}
    for img in soup.find_all("img"):
        for attr in ["src", "data-src"]:
            url = img.get(attr)
            if url and (url.startswith("http://") or url.startswith("https://")):
                clean_name = os.path.basename(urllib.parse.urlparse(url).path)
                if not clean_name or "." not in clean_name:
                    clean_name = f"img_{abs(hash(url))}.png"
                local_path = os.path.join(IMAGES_DIR, clean_name)
                if download_file(url, local_path):
                    img_map[url] = f"./assets/images/{clean_name}"

    # Also handle srcset
    for img in soup.find_all("img"):
        srcset = img.get("srcset")
        if srcset:
            parts = srcset.split(",")
            new_parts = []
            for part in parts:
                tokens = part.strip().split()
                if tokens:
                    u = tokens[0]
                    clean_name = os.path.basename(urllib.parse.urlparse(u).path)
                    if not clean_name or "." not in clean_name:
                        clean_name = f"img_{abs(hash(u))}.png"
                    local_path = os.path.join(IMAGES_DIR, clean_name)
                    if download_file(u, local_path):
                        img_map[u] = f"./assets/images/{clean_name}"
                        desc = tokens[1] if len(tokens) > 1 else ""
                        new_parts.append(f"./assets/images/{clean_name} {desc}".strip())
                    else:
                        new_parts.append(part.strip())
            if new_parts:
                img["srcset"] = ", ".join(new_parts)

    for url, local in img_map.items():
        for img in soup.find_all("img", src=url):
            img["src"] = local

    # Also handle favicon and icon links
    for l in soup.find_all("link", rel=lambda r: r and "icon" in r):
        href = l.get("href")
        if href and (href.startswith("http://") or href.startswith("https://")):
            clean_name = "favicon_" + os.path.basename(urllib.parse.urlparse(href).path)
            local_path = os.path.join(IMAGES_DIR, clean_name)
            if download_file(href, local_path):
                l["href"] = f"./assets/images/{clean_name}"

    # Save local version
    with open("index_local.html", "w", encoding="utf-8") as f:
        f.write(str(soup))

    print(f"Downloaded {len(img_map)} image assets.")
    print("Saved offline-asset version to index_local.html")

if __name__ == "__main__":
    main()
