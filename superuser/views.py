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
    content_types = ContentType.objects.prefetch_related('permission_set').filter(
        app_label='api').exclude(model__in=['user', 'role', 'role_permission', 'country', 'state', 'city', 'customer_type', 'kyc_type'])
    context.update({
        'content_types': content_types,
        'page_title': "Role Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Role", 'url': reverse('superuser:roleList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Role/add.html', context)


@login_required
def roleEdit(request, id):
    content_types = ContentType.objects.prefetch_related('permission_set').filter(
        app_label='api').exclude(model__in=['user', 'role', 'role_permission', 'country', 'state', 'city', 'customer_type', 'kyc_type'])
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
    user = models.User.objects.get(pk=id)
    roles = models.Role.objects.filter(status=1, deleted=0)
    context.update({
        'user': user,
        'roles': roles,
        'page_title': "User Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "User", 'url': reverse('superuser:userList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/User/edit.html', context)


@login_required
def vendorList(request):
    context.update({
        'page_title': "Vendor List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Vendor", 'url': reverse('superuser:vendorList')}, {'name': "List"}]
    })
    return render(request, 'portal/Vendor/list.html', context)


@login_required
def vendorAdd(request):
    countries = models.Country.objects.all()
    context.update({
        'countries': countries,
        'page_title': "Vendor Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Vendor", 'url': reverse('superuser:vendorList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Vendor/add.html', context)


@login_required
def vendorEdit(request, id):
    vendor = models.Vendor.objects.get(pk=id)
    countries = models.Country.objects.all()
    states = models.State.objects.filter(country_id=vendor.country_id)
    cities = models.City.objects.filter(state_id=vendor.state_id)
    context.update({
        'vendor': vendor,
        'countries': countries,
        'states': states,
        'cities': cities,
        'page_title': "Vendor Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Vendor", 'url': reverse('superuser:vendorList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Vendor/edit.html', context)


@login_required
def customerList(request):
    context.update({
        'page_title': "Customer List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Customer", 'url': reverse('superuser:customerList')}, {'name': "List"}]
    })
    return render(request, 'portal/Customer/list.html', context)


@login_required
def customerAdd(request):
    customer_types = models.Customer_Type.objects.all()
    kyc_types = models.KYC_Type.objects.all()
    countries = models.Country.objects.all()
    context.update({
        'countries': countries,
        'customer_types': customer_types,
        'kyc_types': kyc_types,
        'page_title': "Customer Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Customer", 'url': reverse('superuser:customerList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Customer/add.html', context)


@login_required
def customerEdit(request, id):
    customer = models.Customer.objects.get(pk=id)
    customer_types = models.Customer_Type.objects.all()
    kyc_types = models.KYC_Type.objects.all()
    countries = models.Country.objects.all()
    states = models.State.objects.filter(country_id=customer.country_id)
    cities = models.City.objects.filter(state_id=customer.state_id)
    context.update({
        'customer': customer,
        'customer_types': customer_types,
        'kyc_types': kyc_types,
        'countries': countries,
        'states': states,
        'cities': cities,
        'page_title': "Customer Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Customer", 'url': reverse('superuser:customerList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Customer/edit.html', context)


@login_required
def uomList(request):
    context.update({
        'page_title': "Uom List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Uom", 'url': reverse('superuser:uomList')}, {'name': "List"}]
    })
    return render(request, 'portal/Uom/list.html', context)


@login_required
def uomAdd(request):
    context.update({
        'page_title': "Uom Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Uom", 'url': reverse('superuser:uomList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Uom/add.html', context)


@login_required
def uomEdit(request, id):
    uom = models.Uom.objects.get(pk=id)
    context.update({
        'uom': uom,
        'page_title': "Uom Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Uom", 'url': reverse('superuser:uomList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Uom/edit.html', context)


@login_required
def childUomList(request):
    context.update({
        'page_title': "Child Uom List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Child Uom", 'url': reverse('superuser:childUomList')}, {'name': "List"}]
    })
    return render(request, 'portal/Child Uom/list.html', context)


@login_required
def childUomAdd(request):
    uoms = models.Uom.objects.filter(status=1, deleted=0)
    context.update({
        'uoms': uoms,
        'page_title': "Child Uom Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Child Uom", 'url': reverse('superuser:childUomList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Child Uom/add.html', context)


@login_required
def childUomEdit(request, id):
    childUom = models.Child_Uom.objects.get(pk=id)
    uoms = models.Uom.objects.filter(status=1, deleted=0)
    context.update({
        'childUom': childUom,
        'uoms': uoms,
        'page_title': "Child Uom Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Child Uom", 'url': reverse('superuser:childUomList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Child Uom/edit.html', context)


@login_required
def itemCategoryList(request):
    context.update({
        'page_title': "Item Category List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Item Category", 'url': reverse('superuser:itemCategoryList')}, {'name': "List"}]
    })
    return render(request, 'portal/Item Category/list.html', context)


@login_required
def itemCategoryAdd(request):
    context.update({
        'page_title': "Item Category Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Item Category", 'url': reverse('superuser:itemCategoryList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Item Category/add.html', context)


@login_required
def itemCategoryEdit(request, id):
    itemCategory = models.Item_Category.objects.get(pk=id)
    context.update({
        'itemCategory': itemCategory,
        'page_title': "Item Category Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Item Category", 'url': reverse('superuser:itemCategoryList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Item Category/edit.html', context)


@login_required
def itemTypeList(request):
    context.update({
        'page_title': "Item Type List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Item Type", 'url': reverse('superuser:itemTypeList')}, {'name': "List"}]
    })
    return render(request, 'portal/Item Type/list.html', context)


@login_required
def itemTypeAdd(request):
    itemCategories = models.Item_Category.objects.filter(status=1, deleted=0)
    context.update({
        'itemCategories': itemCategories,
        'page_title': "Item Type Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Item Type", 'url': reverse('superuser:itemTypeList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Item Type/add.html', context)


@login_required
def itemTypeEdit(request, id):
    itemType = models.Item_Type.objects.get(pk=id)
    itemCategories = models.Item_Category.objects.filter(status=1, deleted=0)
    context.update({
        'itemType': itemType,
        'itemCategories': itemCategories,
        'page_title': "Item Type Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Item Type", 'url': reverse('superuser:itemTypeList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Item Type/edit.html', context)


@login_required
def itemColorList(request):
    context.update({
        'page_title': "Item Color List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Item Color", 'url': reverse('superuser:itemColorList')}, {'name': "List"}]
    })
    return render(request, 'portal/Item Color/list.html', context)


@login_required
def itemColorAdd(request):
    context.update({
        'page_title': "Item Color Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Item Color", 'url': reverse('superuser:itemColorList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Item Color/add.html', context)


@login_required
def itemColorEdit(request, id):
    itemColor = models.Item_Color.objects.get(pk=id)
    context.update({
        'itemColor': itemColor,
        'page_title': "Item Color Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Item Color", 'url': reverse('superuser:itemColorList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Item Color/edit.html', context)