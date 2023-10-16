from django.shortcuts import render
from sec.decorators import login_required
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from api import models
import environ
env = environ.Env()
environ.Env.read_env()

context = {}
context['project_name'] = env("PROJECT_NAME")
context['client_name'] = env("CLIENT_NAME")

# Create your views here.


@login_required
def dashboard(request):
    context.update({
        'page_title': "Dashboard",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}]
    })
    return render(request, 'portal/dashboard.html', context)


@login_required
def roleList(request):
    context.update({
        'page_title': "Role List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Role", 'url': reverse('superuser:roleList')}, {'name': "List"}]
    })
    return render(request, 'portal/Role/list.html', context)


@login_required
def roleAdd(request):
    # content_types = ContentType.objects.prefetch_related('permission_set').filter(app_label='api').exclude(model__in=['user', 'role', 'role_permission'])
    content_types = ContentType.objects.prefetch_related('permission_set').filter(
        app_label='api').exclude(model__in=['role_permission'])
    context.update({
        'content_types': content_types,
        'page_title': "Role Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Role", 'url': reverse('superuser:roleList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Role/add.html', context)


@login_required
def roleEdit(request, id):
    content_types = ContentType.objects.prefetch_related('permission_set').filter(
        app_label='api').exclude(model__in=['role_permission'])
    role = models.Role.objects.prefetch_related(
        'role_permission_set').get(pk=id)
    selected_permissions = []
    for permissionDetail in role.role_permission_set.all():
        if permissionDetail.permitted == 1:
            selected_permissions.append(permissionDetail.permission_id)
    context.update({
        'role': role,
        'content_types': content_types,
        'selected_permissions': selected_permissions,
        'page_title': "Role Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Role", 'url': reverse('superuser:roleList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Role/edit.html', context)


@login_required
def userList(request):
    context.update({
        'page_title': "User List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "User", 'url': reverse('superuser:userList')}, {'name': "List"}]
    })
    return render(request, 'portal/User/list.html', context)


@login_required
def userAdd(request):
    roles = models.Role.objects.filter(status=1, deleted=0)
    context.update({
        'roles': roles,
        'page_title': "User Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "User", 'url': reverse('superuser:userList')}, {'name': "Add"}]
    })
    return render(request, 'portal/User/add.html', context)


@login_required
def userEdit(request, id):
    content_types = ContentType.objects.prefetch_related('permission_set').filter(
        app_label='api').exclude(model__in=['role_permission'])
    role = models.Role.objects.prefetch_related(
        'role_permission_set').get(pk=id)
    selected_permissions = []
    for permissionDetail in role.role_permission_set.all():
        if permissionDetail.permitted == 1:
            selected_permissions.append(permissionDetail.permission_id)
    context.update({
        'role': role,
        'content_types': content_types,
        'selected_permissions': selected_permissions,
        'page_title': "Role Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Role", 'url': reverse('superuser:roleList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Role/edit.html', context)
