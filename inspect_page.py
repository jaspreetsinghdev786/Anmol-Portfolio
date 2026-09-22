from bs4 import BeautifulSoup

with open('raw_fudali.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("Title:", soup.title.get_text() if soup.title else None)
print("\n--- Scripts ---")
for i, s in enumerate(soup.find_all('script')):
    t = s.get('type', 'standard')
    src = s.get('src')
    content = s.string or ""
    print(f"Script {i}: type={t}, src={src}, inline_len={len(content)}")

print("\n--- Links ---")
for l in soup.find_all('link'):
    print(f"Link: rel={l.get('rel')} href={l.get('href')}")
