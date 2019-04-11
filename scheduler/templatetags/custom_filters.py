from django import template

register = template.Library()

@register.simple_tag
def set_color(counter):
  if counter%2 == 0:
      return 'warning'
  else:
      return 'info'