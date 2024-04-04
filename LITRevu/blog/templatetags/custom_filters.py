from django import template

register = template.Library()


@register.filter
def get_range(value):
    return range(1, value + 1)


@register.filter
def get_range_two_values(value1, value2):
    return range(value2 - value1)
