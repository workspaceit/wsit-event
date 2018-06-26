import re
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@stringfilter
def format_thousands(val):
    output = ' '.join(re.findall('((?:\d+\.)?\d{1,3})', val[::-1]))[::-1]
    return "-" + output if "-" in val else output


register.filter('format_thousands', format_thousands)