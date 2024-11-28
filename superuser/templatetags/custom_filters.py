from django import template

register = template.Library()

@register.filter
def filter_incoming(details_set):
    return details_set.filter(direction='incoming')

@register.filter
def filter_outgoing(details_set):
    return details_set.filter(direction='outgoing')
