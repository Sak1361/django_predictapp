from django import template
from django.urls import reverse

register = template.Library()


@register.filter(name="surplus")
def surplus(value, args):
    return value % args
