from django import template

register = template.Library()

@register.filter
def split_by_comma(value):
    return value.split(",") if value else []

@register.filter
def trim(value):
    return value.strip() if isinstance(value, str) else value


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')
