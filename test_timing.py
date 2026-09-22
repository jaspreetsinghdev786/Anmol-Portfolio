import time
import http.server, socketserver, threading
from playwright.sync_api import sync_playwright
from PIL import Image

PORT = 8119
httpd = socketserver.TCPServer(('', PORT), http.server.SimpleHTTPRequestHandler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    
    print('Testing raw_fudali.html...')
    page.goto(f'http://localhost:{PORT}/raw_fudali.html', wait_until='domcontentloaded')
    time.sleep(2)
    page.screenshot(path='raw_appear.png')
    im1 = Image.open('raw_appear.png')
    print('raw_fudali non-black bbox:', im1.getbbox())

    print('Testing index.html...')
    page.goto(f'http://localhost:{PORT}/index.html', wait_until='domcontentloaded')
    time.sleep(2)
    page.screenshot(path='index_appear.png')
    im2 = Image.open('index_appear.png')
    print('index.html non-black bbox:', im2.getbbox())

    browser.close()

httpd.shutdown()
