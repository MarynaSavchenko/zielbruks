"""module for custom template tags"""
from django import template

register = template.Library()


@register.simple_tag
def get_color_tag(counter):
    """returns color tag based on parity of the counter"""
    if counter % 2 == 0:
        return 'warning'
    return 'info'


@register.simple_tag
def get_danger_tag():
    """returns color tag 'danger'"""
    return 'danger'
