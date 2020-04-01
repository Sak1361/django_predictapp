from django import template
from django.urls import reverse

register = template.Library()


@register.filter(name="sub")
def surplus(value, args):
    return value - args
