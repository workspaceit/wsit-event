from django import template

register = template.Library()


@register.filter
def index(list,i):
    if len(list)>0:
        return list[int(i)]
    else:
        return ''

