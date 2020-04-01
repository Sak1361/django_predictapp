from django import template
from django.urls import reverse

register = template.Library()
@register.filter(name='lookup')
def lookup(value, arg, default=""):
    if arg in value:
        return value[arg]
    else:
        return default
