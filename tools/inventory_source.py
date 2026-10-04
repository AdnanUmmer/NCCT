"""Bounded, read-only public-site inventory. Run manually, never during deployment."""
import json
import re
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urldefrag
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'docs' / 'source-inventory'
out.mkdir(parents=True, exist_ok=True)
queue = deque(['https://ncctdxb.com/en/index.html'])
seen, rows = set(), []
while queue and len(seen) < 100:
    url = queue.popleft()
    if url in seen:
        continue
    seen.add(url)
    row = {'url': url}
    try:
        with urlopen(Request(url, headers={'User-Agent': 'NCCT content migration audit'}), timeout=15) as response:
            raw = response.read(3000000)
            row['status'] = response.status
        soup = BeautifulSoup(raw, 'html.parser')
        row['title'] = soup.title.get_text(' ', strip=True) if soup.title else ''
        row['links'] = sorted({urldefrag(urljoin(url, a['href']))[0] for a in soup.select('a[href]') if a['href']})
        row['images'] = [{'url': urljoin(url, a['src']), 'alt': a.get('alt', '')} for a in soup.select('img[src]')]
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        row['text'] = soup.get_text(' ', strip=True)
        for link in row['links']:
            parsed = urlsplit(link)
            if parsed.netloc == 'ncctdxb.com' and parsed.path.startswith('/en/') and not parsed.query and not re.search(r'\.(pdf|jpe?g|png|webp|svg|zip|mp4)$', parsed.path, re.I):
                queue.append(link)
    except Exception as error:
        row['error'] = str(error)
    rows.append(row)
    (out / 'inventory.json').write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding='utf-8')
    print(row.get('status', 'ERROR'), url, flush=True)
print(f'{len(rows)} pages inventoried')
