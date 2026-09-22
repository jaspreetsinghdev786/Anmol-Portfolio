# Anmolpreet Singh - Video Editor Portfolio

Animated portfolio site for **Anmolpreet Singh**, video editor, plus the scraping pipeline used to build the original layout reference from [Fudali Studio](https://fudali.studio/?ref=killerportfolio).

---

## Brand Palette

| Swatch | Hex | Name | Used for |
|---|---|---|---|
| ⬜ | `#EADEDA` | Dust Grey | Light section backgrounds, wordmark text |
| 🟩 | `#7F9172` | Dusty Olive | Secondary accents, former green/lavender highlights |
| ⬛ | `#353535` | Graphite | Dark backgrounds, deep surfaces |
| 🟥 | `#AF5D63` | Dusty Mauve | Deep accent, gradient ends, hover states |
| 🟥 | `#ED474A` | Strawberry Red | Primary accent: headlines, links, slashes, CTAs |

The original purple Framer theme was remapped to this palette across all 857 inline
color literals in `index.html`. The pre-rebrand file is kept at `index_purple_backup.html`.

---

## 🚀 How to Run the Website Locally (With Full Animation Style)

You can launch the complete website locally with all original Framer micro-interactions, text morphing, continuous marquees, project sliders, and responsive typography:

### Option A: Using Python (Recommended)
```bash
python serve.py
```
This starts a local server at `http://localhost:3000` and automatically opens it in your default browser.

### Option B: Quick Launch (Windows)
Double-click `start_server.bat` inside this directory.

---

## 📁 Project Structure

```text
Anmol Bai/
│
├── index.html                  # Complete standalone website with all Framer animations & local assets
├── assets/                     # Scraped static assets
│   └── images/                 # Downloaded high-res PNGs, WebPs, SVGs, and brand mockups
│
├── serve.py                    # Lightweight local web server with auto-browser launch & CORS headers
├── start_server.bat            # Windows 1-click batch launcher
│
├── scrape_fudali.py            # Option 1: Basic Scraper (Requests + BeautifulSoup) -> fudali_scraped.csv
├── scrape_fudali_playwright.py # Option 2: Dynamic Scraper (Playwright) -> fudali_playwright.csv & fudali_content.json
├── download_complete_site.py   # Complete asset harvester & local link rewriter
│
├── fudali_scraped.csv          # Extracted content in CSV format (Option 1)
├── fudali_playwright.csv       # Extracted content in CSV format (Option 2)
└── fudali_content.json         # Structured JSON format of all headings, paragraphs, links, and images
```

---

## 🕷️ Scraping Scripts Included

### 1. Basic Scraper (`scrape_fudali.py`)
Uses `requests` and `BeautifulSoup` to extract page metadata, titles, headings `<h1>`–`<h6>`, paragraphs, lists, links, and image URLs.
```bash
python scrape_fudali.py
```
**Output:** `fudali_scraped.csv`

### 2. Dynamic Playwright Scraper (`scrape_fudali_playwright.py`)
Launches headless Chromium, scrolls through the entire 9,600px height to trigger lazy-loaded Framer components, and extracts full hydrated DOM content.
```bash
python scrape_fudali_playwright.py
```
**Output:** `fudali_playwright.csv` and `fudali_content.json`

### 3. Complete Asset Scraper (`download_complete_site.py`)
Downloads all 38+ brand images, SVGs, badges, and project mockups into the `assets/images/` directory and generates localized HTML.
```bash
python download_complete_site.py
```

---

## ✨ Preserved Animations & Interactive Effects

1. **Dynamic Text Rotator:** The hero section cycles between `GROW`, `START UP`, and `REBRAND` with smooth cubic-bezier transitions and glowing gradient typography.
2. **Dual-Column Portfolio Marquee:** Continuous vertical marquee displaying client mockups, Starbucks signage, packaging designs, and mobile app screens.
3. **Interactive Project Carousel:** Horizontal card gallery with hover states, tags, case study previews, and development stats.
4. **Process Timeline:** Step-by-step 4-week sprint cards (`01 Kick-off`, `02 Workshop`, `03 Create`, `04 Delivery`) with sleek borders and badge pills.
5. **Interactive FAQ Accordion:** Expanding answers with animated plus icons.
6. **Card Flip / Profile Interaction:** "Who is the designer? Click to find out" interactive card.
7. **Client & Agency Tickers:** Logos and badge highlights for Hitachi, Toyota Tsusho, Starbucks, B/S/H/, Bureau Veritas, and more.
8. **Contact CTA:** Interactive "Book a 30-min call with Magda" pill and email copy triggers.
