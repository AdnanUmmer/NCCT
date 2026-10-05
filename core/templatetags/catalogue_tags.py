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
