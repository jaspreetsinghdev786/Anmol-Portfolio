import json
import time
from playwright.sync_api import sync_playwright

URL = "https://fudali.studio/?ref=killerportfolio"

def inspect_site():
    assets = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        def handle_response(response):
            try:
                assets.append({
                    "url": response.url,
                    "status": response.status,
                    "content_type": response.headers.get("content-type", ""),
                    "size": len(response.body()) if response.status == 200 else 0
                })
            except Exception:
                pass

        page.on("response", handle_response)

        print(f"Navigating to {URL}...")
        page.goto(URL, wait_until="networkidle", timeout=60000)
        time.sleep(2)

        # Smooth scroll down to trigger all animations / lazy loads
        print("Scrolling page to trigger animations and lazy loaded assets...")
        total_height = page.evaluate("document.body.scrollHeight")
        step = 500
        for y in range(0, total_height, step):
            page.evaluate(f"window.scrollTo(0, {y})")
            time.sleep(0.15)
        
        page.evaluate(f"window.scrollTo(0, {total_height})")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

        page.screenshot(path="screenshot_fudali_top.png")
        page.screenshot(path="screenshot_fudali_full.png", full_page=True)

        rendered_html = page.content()
        with open("rendered_fudali.html", "w", encoding="utf-8") as f:
            f.write(rendered_html)

        browser.close()

    with open("assets_catalog.json", "w", encoding="utf-8") as f:
        json.dump(assets, f, indent=2)

    print(f"Captured {len(assets)} network resources.")
    print("Screenshots saved: screenshot_fudali_top.png, screenshot_fudali_full.png")

if __name__ == "__main__":
    inspect_site()
