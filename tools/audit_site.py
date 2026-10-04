"""Read-only audit against the configured local database. Requires requirements-dev."""
import json
import os
import sys
from collections import deque
from pathlib import Path
from urllib.parse import urlsplit, unquote

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import Client, override_settings
from core.models import Application, ContentPage, Resource
from products.models import Product, Category
from projects.models import Project

client = Client()
queue = deque(['/'])
pages, assets, errors = {}, set(), []
with override_settings(ALLOWED_HOSTS=['testserver'], SECURE_SSL_REDIRECT=False):
    while queue:
        path = queue.popleft()
        if path in pages:
            continue
        response = client.get(path)
        pages[path] = {'status': response.status_code}
        if response.status_code != 200:
            errors.append(f'{path}: HTTP {response.status_code}')
            continue
        if response.get('Content-Type', '').startswith('application/pdf'):
            if not b''.join(response.streaming_content).startswith(b'%PDF-'):
                errors.append(f'{path}: invalid PDF')
            response.close()
            continue
        soup = BeautifulSoup(response.content, 'html.parser')
        pages[path]['title'] = soup.title.get_text() if soup.title else None
        if len(soup.select('h1')) != 1:
            errors.append(f'{path}: H1 count')
        for block in soup.select('script[type="application/ld+json"]'):
            json.loads(block.string)
        for element in soup.select('[src], link[rel="stylesheet"], link[rel="icon"]'):
            value = element.get('src') or element.get('href')
            if value and value.startswith('/static/'):
                assets.add(value)
                if not finders.find(unquote(urlsplit(value).path.removeprefix('/static/'))):
                    errors.append(f'{path}: missing asset {value}')
        for anchor in soup.select('a[href]'):
            href = anchor['href']
            if href.startswith('#'):
                if not soup.find(id=href[1:]): errors.append(f'{path}: missing anchor {href}')
            elif href.startswith('/') and not href.startswith('//'):
                parsed = urlsplit(href)
                if not parsed.query and parsed.path not in pages:
                    queue.append(parsed.path)
counts = {'products': Product.objects.count(), 'verified_model_products': Product.objects.exclude(model_reference='').filter(verified=True).count(),
          'categories': Category.objects.count(), 'verified_projects': Project.objects.filter(attribution_verified=True, published=True).count(),
          'unverified_editorial_images': Project.objects.filter(attribution_verified=False).count(),
          'resources': Resource.objects.filter(published=True).count(), 'solutions': Application.objects.count()}
report = {'counts': counts, 'pages': pages, 'assets_checked': len(assets), 'errors': sorted(set(errors))}
Path('docs/qa/site-audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'counts': counts, 'urls_checked': len(pages), 'assets_checked': len(assets), 'errors': report['errors']}, indent=2))
sys.exit(bool(errors))
