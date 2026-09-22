import csv
import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://fudali.studio/?ref=killerportfolio"

def scrape_with_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        print(f"Navigating to {URL} with Playwright...")
        page.goto(URL, wait_until="networkidle", timeout=60000)
        
        # Scroll to load dynamic components
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)
        
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements for clean text scraping
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    data = {}
    data["title"] = soup.title.get_text(strip=True) if soup.title else ""
    meta_desc = soup.find("meta", attrs={"name": "description"})
    data["meta_description"] = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""

    for level in range(1, 7):
        data[f"h{level}"] = [h.get_text(strip=True) for h in soup.find_all(f"h{level}")]

    data["paragraphs"] = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]

    # Lists
    lists = []
    for ul in soup.find_all(["ul", "ol"]):
        items = [li.get_text(strip=True) for li in ul.find_all("li")]
        if items:
            lists.append(items)
    data["lists"] = lists

    data["links"] = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = urljoin(URL, a["href"])
        data["links"].append({
            "text": text,
            "url": href
        })

    data["images"] = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src:
            data["images"].append({
                "src": urljoin(URL, src),
                "alt": img.get("alt", "").strip()
            })

    return data


def save_to_csv(data, filename="fudali_playwright.csv"):
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
        for lst in data.get("lists", []):
            writer.writerow(["List", " | ".join(lst)])
        for link in data["links"]:
            writer.writerow(["Link", f"{link['text']} -> {link['url']}"])
        for img in data["images"]:
            writer.writerow(["Image", f"{img['alt']} -> {img['src']}"])
    print(f"Data saved to {filename}")


def save_to_json(data, filename="fudali_content.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Structured data saved to {filename}")


if __name__ == "__main__":
    print("Scraping with Playwright...")
    result = scrape_with_playwright()
    save_to_csv(result)
    save_to_json(result)
    print("\n--- Summary ---")
    print("Title:", result["title"])
    print("H1:", result["h1"])
    print("Number of paragraphs:", len(result["paragraphs"]))
    print("Number of links:", len(result["links"]))
    print("Number of images:", len(result["images"]))
