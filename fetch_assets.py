"""One-time source audit and image import. No external services at runtime."""
from pathlib import Path
from urllib.parse import urljoin
import json, re
from io import BytesIO
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).parent
OUT = ROOT / 'static/images'
OUT.mkdir(parents=True, exist_ok=True)
base = 'https://ncctdxb.com/en/index.html'
soup = BeautifulSoup((ROOT/'docs/source-home.html').read_text(encoding='utf-8'), 'html.parser')
urls = [urljoin(base, x) for x in re.findall(r'data-bg-image="url\((.*?)\)', str(soup))]
urls += [urljoin(base, i.get('data-src') or i.get('src')) for i in soup.select('img') if not (i.get('data-src') or i.get('src','')).startswith('data:')]
manifest = []
for i, url in enumerate(dict.fromkeys(urls)):
    if not any(ext in url.lower() for ext in ['.jpg','.png','.webp']): continue
    try:
        r=requests.get(url, timeout=25); r.raise_for_status()
        im=Image.open(BytesIO(r.content)); im.load()
        name = url.rsplit('/',1)[-1].rsplit('.',1)[0]
        im.thumbnail((1920,1920))
        im.save(OUT/f'{name}.webp', 'WEBP', quality=85)
        small=im.copy(); small.thumbnail((800,800)); small.save(OUT/f'{name}-800.webp','WEBP',quality=82)
        manifest.append({'name':name,'source':url,'size':im.size})
    except Exception as e: print(url, str(e)[:100])
for section in ['indoor_lights','outdoor_lights','decorative_lights','industrial_lights','professional_lights']:
    url=f'https://ncctdxb.com/en/Real/{section}.html'
    r=requests.get(url,timeout=25)
    (ROOT/f'docs/source-{section}.html').write_text(r.text,encoding='utf-8')
    b=BeautifulSoup(r.text,'html.parser')
    print(section, [(x.get('src'), x.get('alt')) for x in b.select('img')][:15])
(ROOT/'docs/assets.json').write_text(json.dumps(manifest,indent=2))
thumbs=Image.new('RGB',(1000, ((len(manifest)+3)//4)*180),'white')
d=ImageDraw.Draw(thumbs)
for n,a in enumerate(manifest):
    im=Image.open(OUT/f"{a['name']}.webp").convert('RGB'); im.thumbnail((245,150))
    x=(n%4)*250;y=(n//4)*180;thumbs.paste(im,(x,y));d.text((x,y+151),a['name'][:32],fill='black')
thumbs.save(ROOT/'docs/contact-sheet.jpg')
print(json.dumps(manifest,indent=2))
