import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def json_ld(data):
    # Escape HTML delimiters so admin copy cannot terminate a script element.
    value = json.dumps(data).translate(str.maketrans({'<':r'\u003C','>':r'\u003E','&':r'\u0026'}))
    return mark_safe('<script type="application/ld+json">' + value + '</script>')
