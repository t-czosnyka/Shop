from django import template

register = template.Library()


@register.simple_tag(name="checked")
def checked(dictionary, key, value):
    if str(value) in dictionary.getlist(key):
        return "checked"
    return ""


@register.simple_tag(name="selected")
def checked(dictionary, key, value):
    if str(value) in dictionary.getlist(key):
        return "selected"
    return ""


@register.filter(name="get_dict")
def get_dict(dictionary, key):
    return dictionary.get(key)
