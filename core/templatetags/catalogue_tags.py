from django import template
register = template.Library()

@register.filter
def lookup(mapping, key):
    return mapping.get(key, '')

@register.filter
def field_label(value):
    return {'ip_rating': 'IP rating'}.get(value, value.replace('_', ' ').capitalize())


from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import re as _re

@register.filter
def accent(value):
    """Escape text, then turn *words* into <em>words</em> for the italic accent in headings."""
    return mark_safe(_re.sub(r'\*(.+?)\*', r'<em>\1</em>', conditional_escape(value)))


from functools import lru_cache
from pathlib import Path
from django.conf import settings
from django.core.files.images import get_image_dimensions


@lru_cache(maxsize=256)
def _bundled_image_size(basename):
    # Cache immutable bundled assets; never allow a filename to escape static/images.
    if not basename or Path(basename).name != basename:
        return None, None
    try:
        return get_image_dimensions(settings.BASE_DIR / 'static' / 'images' / (basename + '.webp'))
    except (OSError, ValueError):
        return None, None


@register.simple_tag
def project_image_size(project):
    """Reserve the real image shape before loading, capping portraits at 7:5 height."""
    try:
        width, height = (project.image.width, project.image.height) if project.image else _bundled_image_size(project.static_image)
    except (OSError, ValueError):
        width, height = None, None
    width, height = (width, height) if width and height and width > 0 and height > 0 else (800, 600)
    # Normal landscapes/portraits retain their ratio. Only extreme portraits crop.
    return {'width': width, 'height': height, 'aspect': format(max(width / height, 5 / 7), '.6f')}
