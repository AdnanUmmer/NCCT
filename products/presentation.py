"""Reviewed static-only variants; uploaded/admin replacements remain authoritative."""
import json
import hashlib
from functools import lru_cache
from django.conf import settings
from pathlib import Path
from django.templatetags.static import static
VARIANTS = json.loads(Path(__file__).with_name('image_variants.json').read_text(encoding='utf-8'))
@lru_cache(maxsize=256)
def source_matches(path, stamp, size, expected):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected

def product_image_url(obj, original):
    if obj.image:
        return original
    variant = VARIANTS.get(obj.static_image)
    if not variant:
        return original
    source = settings.BASE_DIR / 'static' / 'images' / (obj.static_image + '.webp')
    try:
        stat = source.stat()
        valid = source_matches(str(source), stat.st_mtime_ns, stat.st_size, variant['source_sha256'])
    except OSError:
        valid = False
    return static(variant['path']) if valid else original
