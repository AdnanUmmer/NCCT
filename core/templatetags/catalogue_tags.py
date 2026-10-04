from django import template
register = template.Library()

@register.filter
def lookup(mapping, key):
    return mapping.get(key, '')

@register.filter
def field_label(value):
    return {'ip_rating': 'IP rating'}.get(value, value.replace('_', ' ').capitalize())
