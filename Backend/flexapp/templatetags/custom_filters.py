from django import template
import json

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
            value = json.loads(value)
        if isinstance(key, str) and ":" in key:
            rid, fname = key.split(":", 1)
            return value.get((int(rid), fname))
        return value.get(key)
    except Exception:
        return None

@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter"""
    if value:
        return value.split(delimiter)
    return []

@register.filter
def replace(value, args):
    """Replace old_string:new_string in value"""
    if args and ':' in args:
        old, new = args.split(':', 1)
        return value.replace(old, new)
    return value

@register.filter
def stringformat(value, arg):
    """Format string"""
    try:
        if arg == "s":
            return str(value)
        return value
    except:
        return value

@register.filter
def mul(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide value by arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
