from django.shortcuts import render
from sec.decorators import login_required
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q
from api import models
import environ
import json
import os
import re
from sec import settings
from num2words import num2words
from datetime import datetime, timedelta
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

# -----old getajaxFrom Type------

# def getAjaxFormType(request):
#     if request.method == "POST":
#         print(request.POST,'123')
#         form_type = request.POST['form_type']
#         selector = request.POST['selector']
#         if form_type == "addItemCategory":
#             context.update({'request': request, 'selector': selector})
#             return JsonResponse({
#                 'status': 200,
#                 'formType': render_to_string('ajaxFormType/addItemCategory.html', context)
#             })
#         elif form_type == "addItemType":
#             itemCategories = models.Item_Category.objects.filter(
#                 status=1, deleted=0)
#             context.update(
#                 {'request': request, 'selector': selector, 'itemCategories': itemCategories})
#             return JsonResponse({
#                 'status': 200,
#                 'formType': render_to_string('ajaxFormType/addItemType.html', context)
#             })
#         elif form_type == "addItemColor":
#             context.update({'request': request, 'selector': selector})
#             return JsonResponse({
#                 'status': 200,
#                 'formType': render_to_string('ajaxFormType/addItemColor.html', context)
#             })
#         elif form_type == "addUom":
#             context.update({'request': request, 'selector': selector})
#             return JsonResponse({
#                 'status': 200,
#                 'formType': render_to_string('ajaxFormType/addUom.html', context)
#             })
#         elif form_type == "addStore":
#             context.update({'request': request, 'selector': selector})
#             return JsonResponse({
#                 'status': 200,
#                 'formType': render_to_string('ajaxFormType/addStore.html', context)
#             })
#         elif form_type == "addItem":
#             itemTypes = models.Item_Type.objects.filter(status=1, deleted=0)
#             uoms = models.Uom.objects.filter(status=1, deleted=0)
#             context.update({'request': request, 'selector': selector,
#                            'itemTypes': itemTypes, 'uoms': uoms})
#             return JsonResponse({
#                 'status': 200,
#                 'formType': render_to_string('ajaxFormType/addItem.html', context)
# #             })
#         elif form_type == "addVendor":
#                 countries = models.Country.objects.all()
#                 context.update({'request': request, 'selector': selector, 'countries': countries})
#                 return JsonResponse({
#                     'status': 200,
#                     'formType': render_to_string('ajaxFormType/addVendor.html', context)
#                 })
#     else:
#         return JsonResponse({
#             'status': 500,
#             'message': "There should be ajax method"
#         })


# -----new getajaxFrom Type------

def getAjaxFormType(request):
    if request.method == "POST":
        form_type = request.POST.get('form_type')
        selector = request.POST.get('selector')
        data_id = request.POST.get('data-id', None)  # Use .get to avoid KeyError if data-id is missing

        context = {}  # Ensure context is initialized before using it

        try:
            if form_type == "addItemCategory":
                context.update({'request': request, 'selector': selector})
                return JsonResponse({
                    'status': 200,
                    'formType': render_to_string('ajaxFormType/addItemCategory.html', context)
                })
            elif form_type == "addItemType":
                itemCategories = models.Item_Category.objects.filter(status=1, deleted=0)
                context.update({'request': request, 'selector': selector, 'itemCategories': itemCategories})
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
            elif form_type == "addStore":
                context.update({'request': request, 'selector': selector})
                return JsonResponse({
                    'status': 200,
                    'formType': render_to_string('ajaxFormType/addStore.html', context)
                })
            elif form_type == "addItem":
                itemTypes = models.Item_Type.objects.filter(status=1, deleted=0)
                uoms = models.Uom.objects.filter(status=1, deleted=0)
                context.update({'request': request, 'selector': selector, 'itemTypes': itemTypes, 'uoms': uoms})
                return JsonResponse({
                    'status': 200,
                    'formType': render_to_string('ajaxFormType/addItem.html', context)
                })
            elif form_type == "addVendor":
                countries = models.Country.objects.all()
                context.update({'request': request, 'selector': selector, 'countries': countries})
                return JsonResponse({
                    'status': 200,
                    'formType': render_to_string('ajaxFormType/addVendor.html', context)
                })
            elif form_type == "addVechile":
                data_id = request.POST.get('data-id', None)  # Ensure the correct retrieval of data-id                
                if data_id:
                    try:
                        purchaseBill = models.Purchase_Bill.objects.get(pk=data_id)
                        context.update({'request': request, 'selector': selector, 'purchaseBill': purchaseBill})
                        return JsonResponse({
                            'status': 200,
                            'formType': render_to_string('ajaxFormType/updateVechicleMOut.html', context)
                        })
                    except models.Purchase_Bill.DoesNotExist:
                        return JsonResponse({'status': 404, 'message': "Purchase Bill not found."})
                else:
                    return JsonResponse({'status': 400, 'message': "Data ID is missing."})

        except Exception as e:
            print(f"An error occurred: {e}")
            return JsonResponse({'status': 500, 'message': "An unexpected error occurred."})
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
        app_label='api').exclude(model__in=['user', 'role', 'role_permission', 'country', 'state', 'city', 'customer_type', 'kyc_type', 'child_uom', 'bill_of_material_detail', 'purchase_order_detail', 'transaction_type', 'store_transaction_detail','test_corn_job','user_log_details','outgoing_incoming_ratio','outgoing_incoming_ratio_details','purchase_bill_details','grn_inspection_transaction_detail','physical_inspection_details','on_transit_transaction_details','item_stock_report_details','invoice_details','job_order_detail','job_order_detail_sent'])
    context.update({
        'content_types': content_types,
        'page_title': "Role Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Role", 'url': reverse('superuser:roleList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Role/add.html', context)


@login_required
def roleEdit(request, id):
    content_types = ContentType.objects.prefetch_related('permission_set').filter(
        app_label='api').exclude(model__in=['user', 'role', 'role_permission', 'country', 'state', 'city', 'customer_type', 'kyc_type', 'child_uom', 'bill_of_material_detail', 'purchase_order_detail', 'transaction_type', 'store_transaction_detail','test_corn_job','user_log_details','outgoing_incoming_ratio','outgoing_incoming_ratio_details','purchase_bill_details','grn_inspection_transaction_detail','physical_inspection_details','on_transit_transaction_details','item_stock_report_details','invoice_details','job_order_detail','job_order_detail_sent'])
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
        app_label='api').exclude(model__in=['user', 'role', 'role_permission', 'country', 'state', 'city', 'customer_type', 'kyc_type', 'child_uom', 'bill_of_material_detail', 'purchase_order_detail', 'transaction_type', 'store_transaction_detail','test_corn_job','user_log_details','outgoing_incoming_ratio','outgoing_incoming_ratio_details','purchase_bill_details','grn_inspection_transaction_detail','physical_inspection_details','on_transit_transaction_details','item_stock_report_details','invoice_details','job_order_detail','job_order_detail_sent'])
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
def clientConfigList(request):
    configList = models.Configuration_User.objects.all()
   
    context.update({
        'configList': configList,
        'page_title': "Client Config ",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "ClientConfig", 'url': reverse('superuser:clientConfigList')}, {'name': "List"}]
    })
    return render(request, 'portal/client config/list.html', context)

@login_required
def clientConfigAdd(request):
    context.update({
        'page_title': "Client Config Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "ClientConfig", 'url': reverse('superuser:clientConfigList')}, {'name': "Add"}]
    })
    return render(request, 'portal/client config/add.html', context)

@login_required
def clientConfigEdit(request,id):
    configUser = models.Configuration_User.objects.get(pk=id)
    context.update({
        'configUser':configUser,
        'page_title': "Client Config Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "ClientConfig", 'url': reverse('superuser:clientConfigList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/client config/edit.html', context)

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
def userTransactionLog(request):
    context.update({       
        'page_title': "User Transaction Log",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "User Transaction Log", 'url': reverse('superuser:userTransactionLog')}, {'name': "List"}]
    })
    return render(request, 'portal/User Transaction log/list.html', context)

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
    context ={}
    vendor = models.Vendor.objects.get(pk=id)
    countries = models.Country.objects.all()
    states = models.State.objects.filter(country_id=vendor.country_id)
    cities = models.City.objects.filter(state_id=vendor.state_id)
    if vendor.store_present == 1 :
        store = models.Store.objects.get(vendor_id = id)
        context.update({
            'store_manager': store.manager_name	,
        })
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
    vendors = models.Vendor.objects.all().exclude(id__in=list(models.Store.objects.filter(vendor_id__isnull=False).values_list("vendor_id", flat="True")))
    countries = models.Country.objects.all()
    context.update({
        'vendors':vendors,
        'countries': countries,
        'page_title': "Store Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store", 'url': reverse('superuser:storeList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Store/add.html', context)


@login_required
def storeEdit(request, id):
    store = models.Store.objects.get(pk=id)
    vendors = models.Vendor.objects.all()
    countries = models.Country.objects.all()
    states = models.State.objects.filter(country_id=store.country_id)
    cities = models.City.objects.filter(state_id=store.state_id)
    context.update({
        'store': store,
        'vendors': vendors,
        'countries': countries,
        'states': states,
        'cities': cities,
        'page_title': "Store Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store", 'url': reverse('superuser:storeList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Store/edit.html', context)

@login_required
def gstList(request):
    context.update({
        'page_title': "Gst List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Gst", 'url': reverse('superuser:gstList')}, {'name': "List"}]
    })
    return render(request, 'portal/GST/list.html', context)


@login_required
def gstAdd(request):
    context.update({
        'page_title': "Gst Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Gst", 'url': reverse('superuser:gstList')}, {'name': "Add"}]
    })
    return render(request, 'portal/GST/add.html', context)

@login_required
def billOfMaterialMasterList(request):
    context.update({
        'page_title': "Bill Of Material Master List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Bill Of Material Master", 'url': reverse('superuser:billOfMaterialMasterList')}, {'name': "MasterList"}]
    })
    return render(request, 'portal/Bill Of Material/listMaster.html', context)

@login_required
def billOfMaterialList(request):
    id = request.GET['id']
    context.update({
        'page_title': "Bill Of Material List",
        'Page_id' : id,
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},{'name': "Bill Of Material Master", 'url': reverse('superuser:billOfMaterialMasterList')}, {'name': "Bill Of Material", 'url': reverse('superuser:billOfMaterialList')}, {'name': "List"}]
    })
    return render(request, 'portal/Bill Of Material/list.html', context)


@login_required
def billOfMaterialAdd(request):
    bom_items_id_list = list(models.Bill_Of_Material.objects.all().values_list('bom_item_id', flat=True))
    # max_value = models.Bill_Of_Material.objects.aggregate(max_bom_type=Max('bom_type'))['bom_type'] +1
    context.update({
        'bom_items_id_list': bom_items_id_list,
        'page_title': "Bill Of Material Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Bill Of Material Master", 'url': reverse('superuser:billOfMaterialMasterList')},  {'name': "Add"}]
    })
    return render(request, 'portal/Bill Of Material/add.html', context)


@login_required
def billOfMaterialEdit(request, id):
    billOfMaterial = models.Bill_Of_Material.objects.prefetch_related('bill_of_material_detail_set').get(pk=id)
    bom_items_id_list = list(models.Bill_Of_Material.objects.filter(level__lte=billOfMaterial.level - 1).values_list('bom_item_id', flat=True))
    bomLevels = models.Bill_Of_Material.objects.filter(level__lte=billOfMaterial.level - 1).filter(status=1, deleted=0)
    items = models.Item.objects.filter(status=1, deleted=0)
    uoms = models.Uom.objects.filter(status=1, deleted=0)
    context.update({
        'billOfMaterial': billOfMaterial,
        'bom_items_id_list': bom_items_id_list,
        'bomLevels': bomLevels,
        'items': items,
        'uoms': uoms,
        'page_title': "Bill Of Material Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Bill Of Material Master", 'url': reverse('superuser:billOfMaterialMasterList')},  {'name': "Edit"}]
    })
    return render(request, 'portal/Bill Of Material/edit.html', context)


def getStructureOfBOM(bom_id):
    billOfMaterial = list(models.Bill_Of_Material.objects.filter(pk=bom_id)[
                          :1].values('pk', 'bom_item_name', 'uom__name', 'quantity', 'price'))[0]
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
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Bill Of Material Master", 'url': reverse('superuser:billOfMaterialMasterList')},  {'name': "View"}]
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

    if request.GET.get('id', None):
        id = request.GET.get('id', None)
        purchaseOrder = models.Purchase_Order.objects.prefetch_related('purchase_order_detail_set').get(pk=id)
        vendors = models.Vendor.objects.filter(status=1, deleted=0)
        items = models.Item.objects.filter(status=1, deleted=0)
        context.update({
            'purchaseOrder': purchaseOrder,
            'vendors': vendors,
            'items': items,
            'page_title': "Purchase Order Add",
            'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Purchase Order", 'url': reverse('superuser:purchaseOrderList')}, {'name': "Add"}]
        })
        return render(request, 'portal/Purchase Order/edit.html', context)
    else:

        context.update({
            'page_title': "Purchase Order Add",
            'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Purchase Order", 'url': reverse('superuser:purchaseOrderList')}, {'name': "Add"}]
        })
        return render(request, 'portal/Purchase Order/add.html', context)


@login_required
def purchaseOrderEdit(request, id):
    purchaseOrder = models.Purchase_Order.objects.prefetch_related('purchase_order_detail_set').get(pk=id)
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
    configList = models.Configuration_User.objects.first()
    
    purchaseOrder = models.Purchase_Order.objects.prefetch_related(
        'purchase_order_detail_set').get(pk=id)
    purchaseOrder.amount_with_gst = purchaseOrder.total_amount + \
        purchaseOrder.discounted_value
    context.update({
        'page_title': "Purchase Order Print",
        'purchaseOrder': purchaseOrder,
        'config': configList
    })
    return render(request, 'portal/Purchase Order/print.html', context)


@login_required
def transactionTypeList(request):
    context.update({
        'page_title': "Transaction Type List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Transaction Type ", 'url': reverse('superuser:transactionTypeList')}, {'name': "List"}]
    })
    return render(request, 'portal/Transaction Type/list.html', context)


@login_required
def transactionTypeAdd(request):
    
    context.update({
        'page_title': "Transaction Type Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Transaction Type ", 'url': reverse('superuser:transactionTypeList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Transaction Type/add.html', context)


@login_required
def transactionTypeEdit(request, id):
    transactionType = models.Transaction_Type.objects.get(pk=id)
    context.update({
        'transactionType': transactionType,
        'page_title': "Transaction Type Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Transaction Type ", 'url': reverse('superuser:transactionTypeList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Transaction Type/edit.html', context)


@login_required
def storeItemList(request):
    context.update({
        'page_title': "Store Item List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store Item", 'url': reverse('superuser:storeItemList')}, {'name': "List"}]
    })
    return render(request, 'portal/Store Item/list.html', context)

@login_required
def storeItemTrackingList(request):
    context.update({
        'page_title': "Store Item Tracking List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store Item", 'url': reverse('superuser:storeItemList')}, {'name': "Tracking List"}]
    })
    return render(request, 'portal/Store Item/list2.html', context)

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


@login_required
def storeTransactionList(request):
    context.update({
        'page_title': "Material Receipt",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Material Receipt", 'url': reverse('superuser:storeTransactionList')}, {'name': "List"}]
    })
    return render(request, 'portal/Store Transaction/list.html', context)


@login_required
def stockTransfer(request):
    stores =models.Store.objects.filter(store_item__isnull=False,).distinct()
    context.update({
        'page_title': "Stock Transfer",
        'stores': stores,
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store Item", 'url': reverse('superuser:storeItemList')}, {'name': "Stock Transfer"}]
    })
    return render(request, 'portal/Store Item/stockTransfer.html', context)

@login_required
def storeTransactionAdd(request):
    
    context.update({
        'transaction_type': "2",
        'page_title': "Material Receipt Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store Transaction", 'url': reverse('superuser:storeTransactionList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Store Transaction/add.html', context)


@login_required
def storeTransactionEdit(request, id):
    storeTransaction = models.Store_Transaction.objects.get(pk=id)

    vendors = models.Vendor.objects.filter(status=1, deleted=0)
    purchaseOrderHeaders = models.Purchase_Order.objects.filter(status=1, deleted=0)
    purchaseOrderDetails = models.Purchase_Order_Detail.objects.filter(status=1, deleted=0, purchase_order_header=storeTransaction.purchase_order_header_id) if storeTransaction.purchase_order_header_id else None

    storeTransactionDetails = models.Store_Transaction_Detail.objects.filter(status=1, deleted=0, store_transaction_header=storeTransaction.id)
    items = models.Item.objects.filter(status=1, deleted=0)
    stores = models.Store.objects.filter(status=1, deleted=0)

    max_quantity={}

    if storeTransaction.purchase_order_header_id:
        for storeTransactionDetail in storeTransactionDetails:
            purchaseOrderDetail = purchaseOrderDetails.get(item_id=storeTransactionDetail.item_id)
            max_quantity[storeTransactionDetail.id] = float(purchaseOrderDetail.quantity - purchaseOrderDetail.delivered_quantity + storeTransactionDetail.quantity)

    context.update({
        'storeTransaction': storeTransaction,
        'vendors': vendors,
        'transaction_type': "1",
        'purchaseOrderHeaders': purchaseOrderHeaders,
        'max_quantity': max_quantity,
        'storeTransactionDetails': storeTransactionDetails,
        'items': items,
        'stores': stores,
        'page_title': "Store Transaction Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store Transaction", 'url': reverse('superuser:storeTransactionList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Store Transaction/edit.html', context)


@login_required
def storeTransactionView(request, id):
    storeTransaction = models.Store_Transaction.objects.prefetch_related('store_transaction_detail_set').get(pk=id)
    context.update({
        'storeTransaction': storeTransaction,
        'page_title': "Store Transaction View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store Transaction", 'url': reverse('superuser:storeTransactionList')}, {'name': "View"}]
    })
    return render(request, 'portal/Store Transaction/view.html', context)

@login_required
def storeTransactionPrint(request, id):
    configList = models.Configuration_User.objects.first()
    storeTransaction = models.Store_Transaction.objects.prefetch_related('store_transaction_detail_set').get(pk=id)
    storeTransactionDetail = models.Store_Transaction_Detail.objects.filter(store_transaction_header=id,logical_grn_store=1).first()
    storeTransactionDetailsumAmoutnt = sum(item.amount for item in storeTransaction.store_transaction_detail_set.filter(logical_grn_store=1))
    storeTransactionDetailsumGstAmoutnt = sum(item.amount_with_gst for item in storeTransaction.store_transaction_detail_set.filter(logical_grn_store=1))
    context.update({
        'config': configList,
        'storeTransaction': storeTransaction,
        'storeTransactionDetailsumAmoutnt': storeTransactionDetailsumAmoutnt,
        'storeTransactionDetailsumGstAmoutnt': storeTransactionDetailsumGstAmoutnt,
        'storeTransactionDetail':storeTransactionDetail,
        'page_title': "Material Out Challan Print",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store Transaction", 'url': reverse('superuser:storeTransactionList')}]
    })
    return render(request, 'portal/Store Transaction/print.html', context)

@login_required
def storeTransactionLogicalGrnEdit(request, id):
    storeTransaction = models.Store_Transaction.objects.prefetch_related('store_transaction_detail_set').get(pk=id)
    context.update({
        
        'storeTransaction': storeTransaction,
        'page_title': "Logical Grn delivery Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Store Transaction", 'url': reverse('superuser:storeTransactionList')}]
    })
    return render(request, 'portal/Store Transaction/logicalGrnEdit.html', context)


@login_required
def jobOrderList(request):
    context.update({
        'page_title': "Job Order List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Job Order", 'url': reverse('superuser:jobOrderList')}, {'name': "List"}]
    })
    return render(request, 'portal/Job Order/list.html', context)


@login_required
def jobOrderAdd(request):
    # item_id_n_bom_id={}
    # for bom in models.Bill_Of_Material.objects.all():
    #     item_id_n_bom_id[str(bom.bom_item_id)]=bom.id
    # bom_items_id_list = list(models.Bill_Of_Material.objects.all().values_list('bom_item_id', flat=True))
    item_ids = list(models.Bill_Of_Material_Master.objects.values_list('item_id', flat=True))
   
    if request.GET.get('id', None):
        id = request.GET.get('id', None)
        # print(id)
        jobOrder = models.Job_Order.objects.prefetch_related('job_order_detail_set').get(pk=id)
        jobOrderlast = models.Job_Order.objects.filter(manufacturing_type=jobOrder.manufacturing_type).last()
        jobOrderCount_match = re.search(r'SEC/(?:TPM|SLF)/(\d{3})/', jobOrderlast.order_number)  # Assuming order_number is the field name
        jobOrderCount = int(jobOrderCount_match.group(1)) if jobOrderCount_match else 0
        vendorShort = 'SLF' if jobOrder.manufacturing_type == 'Self' else 'TPM'
        jobOrderNumber =  env("JOB_ORDER_NUMBER_SEQ").replace("${VENDOR_SHORT}", vendorShort).replace(
                "${AI_DIGIT_3}", str(jobOrderCount + 1).zfill(3)).replace("${FINANCE_YEAR}", datetime.today().strftime('%y') + "-" + (datetime(datetime.today().year + 1, 1, 1).strftime('%y')))
        jobOrder.order_number =jobOrderNumber
        # print(jobOrder.order_number)
        stores = models.Store.objects.filter(status=1, deleted=0)
        vendors = models.Vendor.objects.filter(status=1, deleted=0)
        items = models.Item.objects.filter(status=1, deleted=0)

        outgoing_details = jobOrder.job_order_detail_set.filter(direction='outgoing')
        incoming_details = jobOrder.job_order_detail_set.filter(direction='incoming')

        context.update({
            'jobOrder': jobOrder,
            'items': items,
            'vendors': vendors,
            'item_ids': item_ids,
            'outgoing_details': outgoing_details,
            'incoming_details': incoming_details,
            'page_title': "Job Order Add",
            'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Job Order", 'url': reverse('superuser:jobOrderList')}, {'name': "Add"}]
        })
        return render(request, 'portal/Job Order/edit.html', context)

    else:
        # item_ids = list(models.Bill_Of_Material_Master.objects.values_list('item_id', flat=True))
        context.update({
            'page_title': "Job Order Add",
            'item_ids': item_ids,
            'breadcrumbs': [
                {
                    'name': "Dashboard", 
                    'url': reverse('superuser:dashboard')
                }, 
                {
                    'name': "Job Order", 
                    'url': reverse('superuser:jobOrderList')
                }, 
                {
                    'name': "Add"
                }
            ]
        })
        return render(request, 'portal/Job Order/add.html', context)

        

@login_required
def jobOrderEdit(request, id):
    jobOrder = models.Job_Order.objects.prefetch_related('job_order_detail_set').get(pk=id)
    stores = models.Store.objects.filter(status=1, deleted=0)
    vendors = models.Vendor.objects.filter(status=1, deleted=0)
    items = models.Item.objects.filter(status=1, deleted=0)
    time_unit = ''.join(filter(str.isalpha, jobOrder.estimated_time_day))
    time_value = ''.join(filter(str.isdigit, jobOrder.estimated_time_day))
    outgoing_details = jobOrder.job_order_detail_set.filter(direction='outgoing')
    incoming_details = jobOrder.job_order_detail_set.filter(direction='incoming')
    item_ids = list(models.Bill_Of_Material_Master.objects.values_list('item_id', flat=True))

    context.update({
        'jobOrder': jobOrder,
        'items': items,
        'item_ids': item_ids,
        'vendors': vendors,
        'time_unit':time_unit,
        'time_value':time_value,
        'outgoing_details': outgoing_details,
        'incoming_details': incoming_details,
        'page_title': "Job Order Edit",
        'breadcrumbs': [
            {'name': "Dashboard", 'url': reverse('superuser:dashboard')},
            {'name': "Job Order", 'url': reverse('superuser:jobOrderList')},
            {'name': "Edit"}
        ]
    })
    return render(request, 'portal/Job Order/edit.html', context)


@login_required
def jobOrderView(request, id):
    jobOrder = models.Job_Order.objects.prefetch_related('job_order_detail_set').get(pk=id)
    print(jobOrder.job_order_detail_set.all())
    context.update({
        'jobOrder': jobOrder,
        'page_title': "Job Order View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Job Order", 'url': reverse('superuser:jobOrderList')}, {'name': "View"}]
    })
    return render(request, 'portal/Job Order/view.html', context)


@login_required
def jobOrderPrint(request, id):
    configList = models.Configuration_User.objects.first()
    jobOrder = models.Job_Order.objects.prefetch_related('job_order_detail_set').get(pk=id)
    print(jobOrder.job_order_detail_set.all())
    context.update({
        'config': configList,
        'jobOrder': jobOrder,
        'page_title': "Job Order",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Job Order", 'url': reverse('superuser:jobOrderList')}, {'name': "View"}]
    })
    return render(request, 'portal/Job Order/print.html', context)

#--- developed by saswata

@login_required
def materialIssueList(request):
    context.update({
        'page_title': "Material Issue List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Material Issue ", 'url': reverse('superuser:materialIssueList')}, {'name': "List"}]
    })
    return render(request, 'portal/Material Issue/list.html', context)


@login_required
def materialIssueAdd(request):
    items = models.Item.objects.filter(status=1, deleted=0)
    context.update({
        'page_title': " Material Issue Add",
        'items': items,
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Material Issue ", 'url': reverse('superuser:materialIssueList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Material Issue/add.html', context)


@login_required
def materialIssueEdit(request,id):
    materialIssue = models.Store_Transaction.objects.prefetch_related('store_transaction_detail_set').get(pk=id)
    jobOrders = models.Job_Order.objects.filter(status=1, deleted=0)
    jobOrder = models.Job_Order.objects.get(id=materialIssue.job_order_id,status=1, deleted=0)
    items = models.Item.objects.filter(status=1, deleted=0)
    vendor = models.Vendor.objects.filter(id=materialIssue.vendor_id)[0] if len(models.Vendor.objects.filter(id=materialIssue.vendor_id)) else None
    store = materialIssue.store_transaction_detail_set.first().store
    context.update({
        'materialIssue': materialIssue,
        'store': store,
        'jobOrder': jobOrder,
        'items': items,
        'vendor':vendor,
        'page_title': "Material Issue Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},{'name': "Material Issue", 'url': reverse('superuser:materialIssueList')}, {'name': "Edit"}]
    })
    return render(request, 'portal/Material Issue/edit.html', context)


@login_required
def materialIssueView(request,id):
    context = returnMaterialListView(id,2)

    return render(request, 'portal/Material Issue/view.html', context)


@login_required
def materialIssuePrint(request, id):
    print(1111)
    materialIssue = models.Store_Transaction.objects.prefetch_related(
        'store_transaction_detail_set').get(pk=id)
    print(materialIssue)
    total_amount = 0
    configList = models.Configuration_User.objects.first()
    
    materialIssuestores = list(models.Store_Transaction_Detail.objects.filter(store_transaction_header = id).values('pk','store__name',
    'store__address','store__country__name',
    'store__state__name',
    'store__city__name',
    'store__pin'))
    
    materialIssueNumToword = num2words(float(materialIssue.total_amount))
    context.update({
        'page_title': "Delivery Challan",
        'materialIssue': materialIssue,
        'materialIssuestore':materialIssuestores[0],
        'materialIssueNumToword': materialIssueNumToword,
        'config': configList
    })
   
    return render(request, 'portal/Material Issue/print.html', context)


# @login_required
def returnMaterialListView(id,type_id):
    context = {}
    material_issue = models.Store_Transaction.objects.filter(pk=id).values('pk','transaction_number','transaction_date','vendor_id','vendor__name','transaction_type_id','job_order__order_number','total_amount','vehicle')
    material_issue_details = list(models.Store_Transaction_Detail.objects.filter(store_transaction_header_id=id).values('pk','item_id', 'item__name','store_id','store__name','quantity','rate','amount'))
    if(type_id == 1):
        context.update({
            'material_issue':  material_issue,
            'store_name': material_issue_details[0]['store__name'],
            'store_id' : material_issue_details[0]['store_id'],
            'material_issue_details':  material_issue_details,
            'page_title': " Material Issue edit",
            'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Material Issue ", 'url': reverse('superuser:materialIssueList')}, {'name': "Edit"}]
        })
    else:
        context.update({
            'material_issue' :  material_issue,
            'store_name': material_issue_details[0]['store__name'],
            'material_issue_details':  material_issue_details,
            'page_title': " Material Issue view",
            'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Material Issue ", 'url': reverse('superuser:materialIssueList')}, {'name': "view"}]
        })

    return context

#  grn inspection --- developed by saswata
@login_required
def grnInspectionListView(request):
    context.update({
        'page_title': "Grn Inspection List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Grn Inspection", 'url': reverse('superuser:grnInspectionListView')}, {'name': "List"}]
    })
    return render(request, 'portal/Grn Inspection/list.html', context)


@login_required
def grnInspectionAdd(request):
    context.update({
        'page_title': "Grn Inspection Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Grn Inspection", 'url': reverse('superuser:grnInspectionListView')}, {'name': "Add"}]
    })
    return render(request, 'portal/Grn Inspection/add.html', context)


@login_required
def grnInspectionEdit(request,id):
    context = returnMaterialListView(id,1)

    return render(request, 'portal/Grn Inspection/edit.html', context)


@login_required
def grnInspectionView(request,id):
    context = {}
    # print("928")
    grn_inspection_head = models.Grn_Inspection_Transaction.objects.filter(pk=id).get()
    # grn_inspection_head = list(models.Grn_Inspection_Transaction.objects.filter(pk=id).values('pk',
    # 'vendor__name',
    # 'transaction_number',
    # 'purchase_order_header__order_number',
    # ))

    # grn_inspection_det = list(models.Grn_Inspection_Transaction_Detail.objects.filter(grn_inspection_transaction_header_id=id , ins_done =1).values('pk',
    # 'item__name',
    # 'store__name',
    # 'accepted_quantity',
    # 'reject_quantity',
    # 'inspection_date',
    # 'rate',
    # 'amount',
    # 'gst_percentage'

    # ))
    # grn_inspection_det = (models.Grn_Inspection_Transaction_Detail.objects.filter(grn_inspection_transaction_header_id=id , ins_done =1)
    context.update ({
        'grn_inspection_heads' : grn_inspection_head,
        'page_title': "Grn Inspection View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Grn Inspection", 'url': reverse('superuser:grnInspectionListView')}, {'name': "view"}]
    })

    return render(request, 'portal/Grn Inspection/view.html', context)


@login_required
def materialReturnList(request):
    context.update({
        'page_title': "Material Return List",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Material Return ", 'url': reverse('superuser:materialReturnList')}, {'name': "List"}]
    })
    return render(request, 'portal/Material Return/list.html', context)


@login_required
def materialReturnAdd(request):
    job_orders= models.Job_Order.objects.filter(
        id__in=list(models.Store_Transaction.objects.filter(transaction_type__name="MIS").values_list('job_order', flat=True))
    )
    grn_inspections=models.Grn_Inspection_Transaction.objects.exclude(ins_done=0,ins_completed=0)
    context.update({
        'job_orders': job_orders,
        'grn_inspections':grn_inspections,
        'page_title': " Material Return Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Material Return ", 'url': reverse('superuser:materialReturnList')}, {'name': "Add"}]
    })
    return render(request, 'portal/Material Return/add.html', context)


@login_required
def materialReturnEdit(request,id):
    context = None

    return render(request, 'portal/Material Return/edit.html', context)


@login_required
def materialReturnView(request,id):
    material_return = models.Store_Transaction.objects.prefetch_related('store_transaction_detail_set').get(pk=id)
    context.update({
        'material_return': material_return,
        'page_title': "Material Return View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Material Return", 'url': reverse('superuser:materialReturnList')},
                        {'name': "View"}]
    })

    return render(request, 'portal/Material Return/view.html', context)

@login_required
def materialReturnPrint(request,id):
    configList = models.Configuration_User.objects.first()
    material_return = models.Store_Transaction.objects.prefetch_related('store_transaction_detail_set').get(pk=id)
    context.update({
        'material_return': material_return,
        'config': configList,
        'page_title': "Material Return",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Material Return", 'url': reverse('superuser:materialReturnList')},
                        {'name': "View"}]
    })

    return render(request, 'portal/Material Return/print.html', context)

# on transit transaction --- developed by saswata

# material out
@login_required
def materialOutList(request):
    context.update({
        'page_title': "Material Out ",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Material Out", 'url': reverse('superuser:materialOutList')},
                        {'name': "List"}]
    })

    return render(request, 'portal/Material Out/list.html', context)

@login_required
def materialOutAdd(request):
    stores = list(models.Store.objects.filter(status= 1,deleted=0).values('pk' ,'name','vendor_id','vendor__name'))
    context.update({
        'store_list' : stores,
        'page_title': "Material Out Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Material Out", 'url': reverse('superuser:materialOutList')},
                        {'name': "Add"}]
    })


    return render(request, 'portal/Material Out/add.html', context)


@login_required
def materialOutEdit(request,id):

    materialOut =  models.On_Transit_Transaction.objects.filter(pk=id).get()
    # print(materialOut.source_store__name)
    context.update({
        'material_out': materialOut,
        'page_title': "Material Out Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Material Out", 'url': reverse('superuser:materialOutList')},
                        {'name': "Edit"}]
    })

    return render(request, 'portal/Material Out/edit.html', context)
   
@login_required
def materialOutView(request,id):
    materialOut =  models.On_Transit_Transaction.objects.filter(pk=id).get()
    context.update({
        'material_out': materialOut,
        'page_title': "Material Out View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Material Out", 'url': reverse('superuser:materialOutList')},
                        {'name': "view"}]
    })

    return render(request, 'portal/Material Out/view.html', context)

@login_required
def materialOutPrint(request, id):
    materialOut = models.On_Transit_Transaction.objects.prefetch_related(
        'on_transit_transaction_details_set').get(pk=id)
    total_amount = 0
    total_quantity = 0
    materialOutDets = list(models.On_Transit_Transaction_Details.objects.filter(on_transit_transaction_header_id = id).values('quantity','amount'))
    configList = models.Configuration_User.objects.first()

    for index in range (0,len(materialOutDets)):
        total_quantity += float(materialOutDets[index]['quantity'])
        total_amount += float(materialOutDets[index]['amount'])


    context.update({
        'config': configList,
        'page_title': "DELIVERY CHALLAN",
        'materialOut': materialOut,
        'total_amount' : total_amount,
        'total_quantity': total_quantity
    })
    return render(request, 'portal/Material Out/print.html', context)


# material in
@login_required
def materialInList(request):
    context.update({
        'page_title': "Material In ",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Material In", 'url': reverse('superuser:materialInList')},
                        {'name': "List"}]
    })

    return render(request, 'portal/Material In/list.html', context)


@login_required
def materialInAdd(request):

    onTrasitTrasactionList = list(models.On_Transit_Transaction.objects.filter(flag=0).values('pk','transaction_number'))
    context.update({
        'transit_transaction_list': onTrasitTrasactionList,
        'page_title': "Material In Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Material In", 'url': reverse('superuser:materialInList')},
                        {'name': "Add"}]
    })

    return render(request, 'portal/Material In/add.html', context)


@login_required
def materialInView(request,id):

    materialIn =  models.On_Transit_Transaction.objects.filter(pk=id).get()
    # print(materialOut.source_store__name)
    context.update({
        'material_In': materialIn,
        'page_title': "Material In View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Material In", 'url': reverse('superuser:materialInList')},
                        {'name': "view"}]
    })
    return render(request, 'portal/Material In/view.html', context)



# physical Inspection on Store Items --- developed by saswata

@login_required
def physicalInspectionList(request):
    context.update({
        'page_title': "Physical Verification/Reconciliation",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Physical Verification/Reconciliation", 'url': reverse('superuser:physicalInspectionList')},
                        {'name': "List"}] 
    })

    return render(request, 'portal/Physcial Inspection Store/list.html', context)


@login_required
def physicalInspectionAdd(request):

    stores = list(models.Store.objects.filter(status=1, deleted=0).values('pk','name'))
    itemCategories = list(models.Item_Category.objects.filter(status=1, deleted=0).values('pk','name'))
    context.update({
        'store_list': stores,
        'item_catagories' : itemCategories,
        'page_title': "Physical Verification/Reconciliation Add",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Physical Verification/Reconciliation", 'url': reverse('superuser:physicalInspectionList')},
                        {'name': "Add"}]
    })

    return render(request, 'portal/Physcial Inspection Store/add.html', context)


@login_required
def physicalInspectionView(request,id):

    physicalInspDet = models.Physical_Inspection.objects.get(pk=id)
    context.update({
        'physical_inspection': physicalInspDet,
        'page_title': "Physical Verification/Reconciliation View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Physical Verification/Reconciliation", 'url': reverse('superuser:physicalInspectionList')},
                        {'name': "View"}]
    })

    return render(request, 'portal/Physcial Inspection Store/view.html', context)


# purchase bill ---developed by Saswata
@login_required
def purchaseBillList(request):
    context.update({
        'page_title': "Purchase Bill",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Purchase Bill", 'url': reverse('superuser:purchaseBillList')},
                        {'name': "List"}] 
    })

    return render(request, 'portal/Purchase Bill/list.html', context)


@login_required
def purchaseBillAdd(request):
    vendor_list = list(models.Vendor.objects.filter(status = 1, deleted =0).values('pk','name'))
    gst_list =  models.Gst.objects.filter(status = 1, deleted =0)
    if request.GET.get('id', None):
        id = request.GET.get('id', None)
        items = models.Item.objects.all()
        purchaseBill = models.Purchase_Bill.objects.get(pk=id)
        context.update({
            'gst_list' : gst_list,
            'purchase_bill': purchaseBill,
            'items': items,
            'Vendor_list': vendor_list,
            'page_title': "Purchase Bill Add",
            'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                            {'name': "Purchase Bill", 'url': reverse('superuser:purchaseBillList')},
                            {'name': "Add"}]
        })

        return render(request, 'portal/Purchase Bill/copy.html', context)

    else:
        context.update({
            'Vendor_list': vendor_list,
            'page_title': "Purchase Bill Add",
            'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                            {'name': "Purchase Bill", 'url': reverse('superuser:purchaseBillList')},
                            {'name': "Add"}]
        })

        return render(request, 'portal/Purchase Bill/add.html', context)


@login_required
def purchaseBillEdit(request,id):
    gst_list = models.Gst.objects.filter(status = 1, deleted =0)
    print()
    purchaseBill = models.Purchase_Bill.objects.get(pk=id)
    context.update({
        'gst_list': gst_list,
        'purchase_bill': purchaseBill,
        'page_title': "Purchase Bill Edit",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Purchase Bill", 'url': reverse('superuser:purchaseBillList')},
                        {'name': "Edit"}]
    })

    return render(request, 'portal/Purchase Bill/edit.html', context)


@login_required
def purchaseBillView(request,id):

    purchaseBill = models.Purchase_Bill.objects.get(pk=id)
    context.update({
        'purchase_bill': purchaseBill,
        'page_title': "Purchase Bill View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Purchase Bill", 'url': reverse('superuser:purchaseBillList')},
                        {'name': "View"}]
    })

    return render(request, 'portal/Purchase Bill/view.html', context)

@login_required
def purchaseBillTallyReport(request):
    context.update({
        'page_title': "Purchase Bill To Tally",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Purchase Bill To Tally", 'url': reverse('superuser:purchaseBillTallyReport')},
                        {'name': "Process"}]
    })

    return render(request, 'portal/process/tally.html', context)

@login_required
def fgMigrationTallyReport(request):
    store = models.Store.objects.filter(vendor_id__isnull=True).distinct()
    context.update({
        'stores': store,
        'page_title': "Finished goods Migration To Tally",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Finished goods Migration To Tally", 'url': reverse('superuser:fgMigrationTallyReport')},
                        {'name': "Process"}]
    })

    return render(request, 'portal/process/fgTally.html', context)


@login_required
def reportItemTrackingReport(request):
    stores = models.Store.objects.filter(Q(store_item__isnull=False)).distinct()
    store_items=models.Store_Item.objects.all()
    context.update({
        'stores': stores,
        'store_items':store_items,
        'page_title': "Item Tracking Report",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Reports"}, {'name': "Item Tracking Report", 'url': reverse('superuser:reportItemTrackingReport')}]
    })
    return render(request, 'portal/Report/ItemTrackingReport.html', context)


@login_required
def reportInventorySummary(request):
    context.update({
        'page_title': "Inventory Summary",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Reports"}, {'name': "Inventory"}, {'name': "Inventory Summary", 'url': reverse('superuser:reportInventorySummary')}]
    })
    return render(request, 'portal/Report/Inventory/InventorySummary.html', context)


@login_required
def reportInventoryStorewise(request):
    vendors = models.Vendor.objects.all()
    context.update({
        'vendors': vendors,
        'page_title': "Inventory Storewise",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Reports"}, {'name': "Inventory"}, {'name': "Inventory Storewise", 'url': reverse('superuser:reportInventoryStorewise')}]
    })
    return render(request, 'portal/Report/Inventory/InventoryStorewise.html', context)


@login_required
def reportStockTransfer(request):
    context.update({
        'page_title': "Stock Transfer",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Reports"}, {'name': "Stock Transfer", 'url': reverse('superuser:reportStockTransfer')}]
    })
    return render(request, 'portal/Report/StockTransfer.html', context)


@login_required
def reportPurchaseOrderByVendor(request):
    context.update({
        'page_title': "Purchase Order By Vendor",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Reports"}, {'name': "Purchase Orders"}, {'name': "Purchase Order By Vendor", 'url': reverse('superuser:reportPurchaseOrderByVendor')}]
    })
    return render(request, 'portal/Report/Purchase Order/PurchaseOrderByVendor.html', context)


@login_required
def reportPurchaseOrderByItem(request):
    context.update({
        'page_title': "Purchase Order By Item",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Reports"}, {'name': "Purchase Orders"}, {'name': "Purchase Order By Item", 'url': reverse('superuser:reportPurchaseOrderByItem')}]
    })
    return render(request, 'portal/Report/Purchase Order/PurchaseOrderByItem.html', context)


@login_required
def reportActivePurchaseOrder(request):
    context.update({
        'page_title': "Active Purchase Order",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Reports"}, {'name': "Purchase Orders"}, {'name': "Active Purchase Order", 'url': reverse('superuser:reportActivePurchaseOrder')}]
    })
    return render(request, 'portal/Report/Purchase Order/ActivePurchaseOrder.html', context)

@login_required
def reportActivePurchaseMaterialIssue(request):
    stores = models.Store.objects.filter(Q(store_item__isnull=False),Q(vendor_id__isnull=True)).distinct()
    config = models.Configuration_User.objects.first()
    context.update({
        'config': config,
        'stores': stores,
        'page_title': "Purchase and Material Issue ",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Reports"}, {'name': "Purchase and Material Issue"}, {'name': "Active Purchase and Material Issue", 'url': reverse('superuser:reportActivePurchaseMaterialIssue')}]
    })
    return render(request, 'portal/Report/purchaseAndMaterialSendForJob.html', context)

@login_required
def reportActiveVendorIssueReciept(request):
    stores = models.Store.objects.filter(Q(store_item__isnull=False),Q(vendor_id__isnull=False)).distinct()
    config = models.Configuration_User.objects.first()
    context.update({
        'stores': stores,
        'config': config,
        'page_title': "Vendor JobOrder Material Issue and Reciept ",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Reports"}, {'name': "VendorJobOrderIssueReciept"}, {'name': "Active VendorJobOrderIssueReciept", 'url': reverse('superuser:reportActiveVendorIssueReciept')}]
    })
    return render(request, 'portal/Report/vendorJobOrderIssueRecep.html', context)

@login_required
def invoiceStoreTransactionMaigration(request):
    stores = models.Store.objects.filter(Q(store_item__isnull=False),Q(vendor_id__isnull=True)).distinct()
    context.update({
        'stores': stores,
        'page_title': "Invoice to Store Transaction Migration",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')},
                        {'name': "Invoice to Store Transaction Migration", 'url': reverse('superuser:invoiceStoreTransactionMaigration')},
                        {'name': "Migration Process"}]
    })

    return render(request, 'portal/process/inoviceStoreTransact.html', context)

@login_required
def reportProduction(request):
    context.update({
        'page_title': "Production Report For SFG and FG ",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Production Report",'url': reverse('superuser:reportProduction')}]
    })
    return render(request, 'portal/Report/Production/list.html', context)

@login_required
def reportProductionView(request,id):
    storeTransactionHeader = models.Store_Transaction.objects.prefetch_related(
        'store_transaction_detail_set').get(pk=id)
    print(storeTransactionHeader.job_order)
    job_order = models.Job_Order.objects.prefetch_related('job_order_detail_set').get(pk = storeTransactionHeader.job_order_id)
    context.update({
        'storeTranasction' : storeTransactionHeader,
        'page_title': "Production Report For SFG and FG View",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "Production Report",'url': reverse('superuser:reportProduction')}, {'name': "Transaction View"}]
    })
    return render(request, 'portal/Report/Production/view.html', context)

@login_required
def storeItemCurrentMigrate(request):
    transaction_type = models.Transaction_Type.objects.filter(status=1, deleted=0)
    print(transaction_type)
    context.update({
        'transaction_types': transaction_type,
        'page_title': "Current Store Item Migration",
        'breadcrumbs': [{'name': "Dashboard", 'url': reverse('superuser:dashboard')}, {'name': "store ItemCurrent Tracking",'url': reverse('superuser:storeItemTrackingList')}, {'name': "Migration"}]
    })
    return render(request, 'portal/Store Item/stockMigration.html', context)