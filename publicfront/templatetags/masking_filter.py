import re
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@stringfilter
def mask(val):
    return val[-4:].rjust(len(val), "*")


register.filter('mask', mask)