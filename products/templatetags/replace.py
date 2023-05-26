from django import template

register = template.Library()


@register.filter(name="replace")
def replace(value, arg):
    """Replaces all values of arg with space"""
    return value.replace(arg, " ")