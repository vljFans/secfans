from django.shortcuts import render
from sec.decorators import login_required
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q
from api import models
import environ
import os
from sec import settings
env = environ.Env()
environ.Env.read_env()

context = {}
context['project_name'] = env("PROJECT_NAME")
context['client_name'] = env("CLIENT_NAME")
context['client_add ress'] = env("CLIENT_ADDRESS")
context['client_work_address'] = env("CLIENT_WORK_ADDRESS")
context['client_contact'] = env("CLIENT_CONTACT")
context['client_gst_number'] = env("CLIENT_GST_NUMBER")

# Create your views here.


def getAjaxFormType(request):
    if request.method == "POST":
        form_type = request.POST['form_type']
        selector = request.POST['selector']
        if form_type == "addItemCategory":
            context.update({'request': request, 'selector': selector})
            return JsonResponse({
                'status': 200,
                'formType': render_to_string('ajaxFormType/addItemCategory.html', context)
            })
        elif form_type == "addItemType":
            itemCategories = models.Item_Category.objects.filter(
                status=1, deleted=0)
            context.update(
                {'request': request, 'selector': selector, 'itemCategories': itemCategories})
            return JsonResponse({
                'status': 200,
                'formType': render_to_string('ajaxFormType/addItemType.html', context)
            })
        elif form_type == "addItemColor":
            context.update({'request': request, 'selector': selector})
            return JsonResponse({
                'status': 200,
                'formType': render_to_string('ajaxFormType/addItemColor.html', context)
            })
        elif form_type == "addUom":
            context.update({'request': request, 'selector': selector})
            return JsonResponse({
                'status': 200,
                'formType': render_to_string('ajaxFormType/addUom.html', context)
            })
    else:
        return JsonResponse({
            'status': 500,
            'message': "There should be ajax method"
        })


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
        app_label='api').exclude(model__in=['user', 'role', 'role_permission', 'country', 'state', 'city', 'customer_type', 'kyc_type', 'child_uom', 'bill_of_material_detail', 'purchase_order_detail'])
    context.update({
        'content_types': content_types,
        'page_title': "Role Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Role", 'url': reverse('superuser:roleList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Role/add.html', context)


@login_required
def roleEdit(request, id):
    content_types = ContentType.objects.prefetch_related('permission_set').filter(
        app_label='api').exclude(model__in=['user', 'role', 'role_permission', 'country', 'state', 'city', 'customer_type', 'kyc_type', 'child_uom', 'bill_of_material_detail', 'purchase_order_detail'])
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
def roleView(request, id):
    content_types = ContentType.objects.prefetch_related('permission_set').filter(
        app_label='api').exclude(model__in=['user', 'role', 'role_permission', 'country', 'state', 'city', 'customer_type', 'kyc_type', 'child_uom', 'bill_of_material_detail', 'purchase_order_detail'])
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
        'page_title': "Role View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Role", 'url': reverse('superuser:roleList')}, {'name': "View"}]
    })
    return render(request, 'portal/Role/view.html', context)


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
def vendorView(request, id):
    vendor = models.Vendor.objects.get(pk=id)
    context.update({
        'vendor': vendor,
        'page_title': "Vendor View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Vendor", 'url': reverse('superuser:vendorList')}, {'name': "View"}]
    })
    return render(request, 'portal/Vendor/view.html', context)


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
def customerView(request, id):
    customer = models.Customer.objects.get(pk=id)
    context.update({
        'customer': customer,
        'page_title': "Customer View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Customer", 'url': reverse('superuser:customerList')}, {'name': "View"}]
    })
    return render(request, 'portal/Customer/view.html', context)


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
    item_categories = models.Item_Category.objects.filter(status=1, deleted=0)
    context.update({
        'item_categories': item_categories,
        'page_title': "Item Type Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Item Type", 'url': reverse('superuser:itemTypeList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Item Type/add.html', context)


@login_required
def itemTypeEdit(request, id):
    itemType = models.Item_Type.objects.get(pk=id)
    item_categories = models.Item_Category.objects.filter(status=1, deleted=0)
    context.update({
        'itemType': itemType,
        'item_categories': item_categories,
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


@login_required
def itemList(request):
    context.update({
        'page_title': "Item List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Item", 'url': reverse('superuser:itemList')}, {'name': "List"}]
    })
    return render(request, 'portal/Item/list.html', context)


@login_required
def itemAdd(request):
    context.update({
        'page_title': "Item Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Item", 'url': reverse('superuser:itemList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Item/add.html', context)


@login_required
def itemEdit(request, id):
    item = models.Item.objects.get(pk=id)
    item_types = models.Item_Type.objects.filter(status=1, deleted=0)
    item_colors = models.Item_Color.objects.filter(status=1, deleted=0)
    uoms = models.Uom.objects.filter(status=1, deleted=0)
    context.update({
        'item': item,
        'item_types': item_types,
        'item_colors': item_colors,
        'uoms': uoms,
        'page_title': "Item Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Item", 'url': reverse('superuser:itemList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Item/edit.html', context)


@login_required
def storeList(request):
    context.update({
        'page_title': "Store List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store", 'url': reverse('superuser:storeList')}, {'name': "List"}]
    })
    return render(request, 'portal/Store/list.html', context)


@login_required
def storeAdd(request):
    context.update({
        'page_title': "Store Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store", 'url': reverse('superuser:storeList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Store/add.html', context)


@login_required
def storeEdit(request, id):
    store = models.Store.objects.get(pk=id)
    countries = models.Country.objects.all()
    states = models.State.objects.filter(country_id=store.country_id)
    cities = models.City.objects.filter(state_id=store.state_id)
    context.update({
        'store': store,
        'countries': countries,
        'states': states,
        'cities': cities,
        'page_title': "Store Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store", 'url': reverse('superuser:storeList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Store/edit.html', context)


@login_required
def billOfMaterialList(request):
    context.update({
        'page_title': "Bill Of Material List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Bill Of Material", 'url': reverse('superuser:billOfMaterialList')}, {'name': "List"}]
    })
    return render(request, 'portal/Bill Of Material/list.html', context)


@login_required
def billOfMaterialAdd(request):
    context.update({
        'page_title': "Bill Of Material Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Bill Of Material", 'url': reverse('superuser:billOfMaterialList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Bill Of Material/add.html', context)


@login_required
def billOfMaterialEdit(request, id):
    billOfMaterial = models.Bill_Of_Material.objects.prefetch_related(
        'bill_of_material_detail_set').get(pk=id)
    bomLevels = models.Bill_Of_Material.objects.filter(
        level__lte=billOfMaterial.level - 1).filter(status=1, deleted=0)
    items = models.Item.objects.filter(status=1, deleted=0)
    uoms = models.Uom.objects.filter(status=1, deleted=0)
    context.update({
        'billOfMaterial': billOfMaterial,
        'bomLevels': bomLevels,
        'items': items,
        'uoms': uoms,
        'page_title': "Bill Of Material Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Bill Of Material", 'url': reverse('superuser:billOfMaterialList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Bill Of Material/edit.html', context)


def getStructureOfBOM(bom_id):
    billOfMaterial = list(models.Bill_Of_Material.objects.filter(pk=bom_id)[
                          :1].values('pk', 'name', 'uom__name', 'quantity', 'price'))[0]
    childBOMS = models.Bill_Of_Material_Detail.objects.filter(
        status=1, deleted=0, bill_of_material_header_id=bom_id)
    id_lists = []
    for each in childBOMS:
        id_lists.append(each.id)
    structure = []
    for id in id_lists:
        childDetail = models.Bill_Of_Material_Detail.objects.get(pk=id)
        each_child_structure = {}
        each_child_structure['pk'] = id
        each_child_structure['quantity'] = childDetail.quantity
        each_child_structure['price'] = childDetail.price
        if childDetail.item_id is not None:
            each_child_structure['item'] = list(models.Item.objects.filter(pk=childDetail.item_id)[:1].values(
                'pk', 'name', 'item_type__name', 'item_type__item_category__name', 'uom__name', 'price'))[0]
        if childDetail.bom_level_id is not None:
            each_child_structure['bom'] = getStructureOfBOM(
                childDetail.bom_level_id)
        structure.append(each_child_structure)
    billOfMaterial['structure'] = structure
    return billOfMaterial


@login_required
def billOfMaterialView(request, id):
    billOfMaterial = models.Bill_Of_Material.objects.prefetch_related(
        'bill_of_material_detail_set').get(pk=id)
    # billOfMaterial = getStructureOfBOM(id)
    context.update({
        'billOfMaterial': billOfMaterial,
        'page_title': "Bill Of Material View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Bill Of Material", 'url': reverse('superuser:billOfMaterialList')}, {'name': "View"}]
    })
    return render(request, 'portal/Bill Of Material/view.html', context)


@login_required
def billOfMaterialPrint(request, id):
    billOfMaterial = models.Bill_Of_Material.objects.prefetch_related(
        'bill_of_material_detail_set').get(pk=id)
    context.update({
        'page_title': "Bill Of Material Print",
        'billOfMaterial': billOfMaterial,
    })
    return render(request, 'portal/Bill Of Material/print.html', context)


@login_required
def purchaseOrderList(request):
    context.update({
        'page_title': "Purchase Order List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Purchase Order", 'url': reverse('superuser:purchaseOrderList')}, {'name': "List"}]
    })
    return render(request, 'portal/Purchase Order/list.html', context)


@login_required
def purchaseOrderAdd(request):
    context.update({
        'page_title': "Purchase Order Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Purchase Order", 'url': reverse('superuser:purchaseOrderList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Purchase Order/add.html', context)


@login_required
def purchaseOrderEdit(request, id):
    purchaseOrder = models.Purchase_Order.objects.prefetch_related(
        'purchase_order_detail_set').get(pk=id)
    vendors = models.Vendor.objects.filter(status=1, deleted=0)
    items = models.Item.objects.filter(status=1, deleted=0)
    context.update({
        'purchaseOrder': purchaseOrder,
        'vendors': vendors,
        'items': items,
        'page_title': "Purchase Order Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Purchase Order", 'url': reverse('superuser:purchaseOrderList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Purchase Order/edit.html', context)


@login_required
def purchaseOrderView(request, id):
    purchaseOrder = models.Purchase_Order.objects.prefetch_related(
        'purchase_order_detail_set').get(pk=id)
    purchaseOrder.amount_with_gst = purchaseOrder.total_amount + \
        purchaseOrder.discounted_value
    context.update({
        'purchaseOrder': purchaseOrder,
        'page_title': "Purchase Order View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Purchase Order", 'url': reverse('superuser:purchaseOrderList')}, {'name': "View"}]
    })
    return render(request, 'portal/Purchase Order/view.html', context)


@login_required
def purchaseOrderPrint(request, id):
    purchaseOrder = models.Purchase_Order.objects.prefetch_related(
        'purchase_order_detail_set').get(pk=id)
    purchaseOrder.amount_with_gst = purchaseOrder.total_amount + \
        purchaseOrder.discounted_value
    context.update({
        'page_title': "Purchase Order Print",
        'purchaseOrder': purchaseOrder
    })
    return render(request, 'portal/Purchase Order/print.html', context)


@login_required
def storeItemList(request):
    context.update({
        'page_title': "Store Item List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store Item", 'url': reverse('superuser:storeItemList')}, {'name': "List"}]
    })
    return render(request, 'portal/Store Item/list.html', context)


@login_required
def storeItemAdd(request):
    context.update({
        'page_title': "Store Item Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store Item", 'url': reverse('superuser:storeItemList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Store Item/add.html', context)


@login_required
def storeItemEdit(request, id):
    storeItem = models.Store_Item.objects.get(pk=id)
    stores = models.Store.objects.all()
    items = models.Item.objects.all()
    context.update({
        'storeItem': storeItem,
        'stores': stores,
        'items': items,
        'page_title': "Store Item Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store Item", 'url': reverse('superuser:storeItemList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Store Item/edit.html', context)