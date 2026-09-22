import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import json

BASE_URL = "https://fudali.studio/?ref=killerportfolio"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def scrape_page(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove script and style elements
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    data = {}

    # Title
    data["title"] = soup.title.get_text(strip=True) if soup.title else ""

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    data["meta_description"] = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""

    # Headings
    for level in range(1, 7):
        headings = [h.get_text(strip=True) for h in soup.find_all(f"h{level}")]
        data[f"h{level}"] = headings

    # Paragraphs and main text blocks
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    data["paragraphs"] = paragraphs

    # Lists
    lists = []
    for ul in soup.find_all(["ul", "ol"]):
        items = [li.get_text(strip=True) for li in ul.find_all("li")]
        if items:
            lists.append(items)
    data["lists"] = lists

    # Links
    links = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = urljoin(url, a["href"])
        links.append({"text": text, "url": href})
    data["links"] = links

    # Images
    images = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src:
            images.append({
                "src": urljoin(url, src),
                "alt": img.get("alt", "").strip()
            })
    data["images"] = images

    return data


def save_to_csv(data, filename="fudali_scraped.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Content"])

        writer.writerow(["Title", data["title"]])
        writer.writerow(["Meta Description", data["meta_description"]])

        for level in range(1, 7):
            for h in data[f"h{level}"]:
                writer.writerow([f"H{level}", h])

        for p in data["paragraphs"]:
            writer.writerow(["Paragraph", p])

        for lst in data["lists"]:
            writer.writerow(["List", " | ".join(lst)])

        for link in data["links"]:
            writer.writerow(["Link", f"{link['text']} -> {link['url']}"])

        for img in data["images"]:
            writer.writerow(["Image", f"{img['alt']} -> {img['src']}"])

    print(f"Data saved to {filename}")


if __name__ == "__main__":
    print(f"Scraping {BASE_URL} ...")
    scraped = scrape_page(BASE_URL)
    if scraped:
        save_to_csv(scraped)
        # Print a quick summary
        print("\n--- Summary ---")
        print("Title:", scraped["title"])
        print("H1:", scraped["h1"])
        print("Number of paragraphs:", len(scraped["paragraphs"]))
        print("Number of links:", len(scraped["links"]))
        print("Number of images:", len(scraped["images"]))
    else:
        print("Scraping failed.")
