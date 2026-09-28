from pathlib import Path
from io import BytesIO
import json
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
root=Path(__file__).parent
manifest=json.loads((root/'docs/assets.json').read_text())
for name in ['ind_p1','ind_p2','ind_p3','indus_p1','prof_p1']:
    url=f'https://ncctdxb.com/wp-content/uploads/{name}.PNG'
    r=requests.get(url,timeout=20);r.raise_for_status()
    im=Image.open(BytesIO(r.content));im.thumbnail((1200,1200))
    im.save(root/f'static/images/{name}.webp','WEBP',quality=90)
    small=im.copy();small.thumbnail((800,800));small.save(root/f'static/images/{name}-800.webp','WEBP',quality=85)
    manifest.append({'name':name,'source':url,'size':im.size})
for name in ['Outdoor_lights','Decorative_lights']:
    r=requests.get(f'https://ncctdxb.com/en/Real/{name}.html',timeout=20)
    (root/f'docs/source-{name}.html').write_text(r.text,encoding='utf-8')
(root/'docs/assets.json').write_text(json.dumps(manifest,indent=2))
sheet=Image.new('RGB',(1250,270),'#eee')
for i,name in enumerate(['ind_p1','ind_p2','ind_p3','indus_p1','prof_p1']):
    im=Image.open(root/f'static/images/{name}.webp').convert('RGB');im.thumbnail((245,240));sheet.paste(im,(i*250,0))
    ImageDraw.Draw(sheet).text((i*250,245),name,fill='black')
sheet.save(root/'docs/products-sheet.jpg')
