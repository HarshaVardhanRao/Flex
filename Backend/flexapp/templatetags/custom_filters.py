from django import template

register = template.Library()

@register.filter
def split_by_comma(value):
    return value.split(",") if value else []

@register.filter
def trim(value):
    return value.strip() if isinstance(value, str) else value


@register.filter
def get_item(value, key):
    try:
        if isinstance(value, str):
            value = json.loads(value)  # parse JSON string into a dictionary
        return value.get(key)
    except Exception:
        return None
