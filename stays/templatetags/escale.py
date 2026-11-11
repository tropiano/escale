from django import template
from django.utils.formats import number_format

register = template.Library()


@register.filter
def rub(value):
    """24900 -> '24 900 ₽' (digit grouping follows the active language)."""
    if value in (None, ""):
        return ""
    return f"{number_format(value, force_grouping=True)} ₽"


@register.filter
def stars(value):
    return "★" * int(value or 0)
