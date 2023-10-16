from django import template
from django.contrib.sessions.models import Session

register = template.Library()


@register.filter
def permission_text(value):
    return value.split('_', 1)[0]


@register.filter
def get_session_permission(codename, request):
    return next((sub for sub in request.session['role_permissions'] if sub['permission__codename'] in codename), None)

# @register.simple_tag(takes_context=True)
# def param_replace(context, **kwargs):
#     d = context['request'].GET.copy()
#     for k, v in kwargs.items():
#         d[k] = v
#     for k in [k for k, v in d.items() if not v]:
#         del d[k]
#     return d.urlencode()


@register.filter
def path_in_list(path, path_list):
    path_parts = path.split('/')
    for item in path_parts:
        if item in path_list:
            return True
    return False


@register.filter
def quote_replace(value):
    return value.replace('_', " ")
