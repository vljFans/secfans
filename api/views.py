from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from . import models
from django.contrib.messages import get_messages
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
from django.utils.timezone import now
from openpyxl import Workbook
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from pathlib import Path
from decimal import Decimal
import os
import math
import environ

env = environ.Env()
environ.Env.read_env()


class CustomPaginator:
    def __init__(self, items, per_page):
        self.items = items
        self.per_page = per_page

    def get_page(self, page_number):
        page_number = int(page_number)  # Convert to integer
        start = (page_number - 1) * self.per_page
        end = start + self.per_page
        page_items = self.items[start:end]
        return page_items

    def get_total_pages(self):
        return math.ceil(len(self.items) / self.per_page)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def loginUser(request):
    context = {}
    user = models.User.objects.get(pk=request.user.id)
    if user is not None:
        login(request, user)
        context.update({'status': 200, 'message': ""})
    else:
        context.update({'status': 501, 'message': "User Not Found."})
    return Response(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logoutUser(request):
    context = {}
    logout(request)
    try:
        del request.session
    except:
        pass
    try:
        storage = get_messages(request)
        for message in storage:
            message = ''
        storage.used = False
    except:
        pass
    context.update({'status': 200, 'message': "Logged Out Successfully."})
    return Response(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserDetails(request):
    context = {}
    context.update({'status': 200, 'message': "User Details Fetched Successfully.",
                   'userDetails': serializers.serialize('json', [request.user])})
    return JsonResponse(context, safe=False)


@api_view(['GET'])
def getContentTypes(request):
    context = {}
    page_items = ContentType.objects.prefetch_related('permission_set').filter(app_label='api').exclude(
        model__in=['user', 'role', 'role_permission', 'country', 'state', 'city', 'customer_type', 'kyc_type', 'child_uom', 'bill_of_material_detail', 'purchase_order_detail', 'transaction_type', 'store_transaction_detail'])
    context.update(
        {'status': 200, 'message': "Content Types Fetched Successfully", 'page_items': serializers.serialize('json', page_items)})
    return JsonResponse(context)


@api_view(['GET'])
def getCustomerTypes(request):
    context = {}
    page_items = models.Customer_Type.objects.all()
    context.update(
        {'status': 200, 'message': "Customer Types Fetched Successfully", 'page_items': serializers.serialize('json', page_items)})
    return JsonResponse(context)


@api_view(['GET'])
def getKycTypes(request):
    context = {}
    page_items = models.KYC_Type.objects.all()
    context.update(
        {'status': 200, 'message': "KYC Types Fetched Successfully", 'page_items': serializers.serialize('json', page_items)})
    return JsonResponse(context)


@api_view(['GET'])
def getCountries(request):
    context = {}
    page_items = models.Country.objects.all()
    context.update(
        {'status': 200, 'message': "Countries Fetched Successfully", 'page_items': serializers.serialize('json', page_items)})
    return JsonResponse(context)


@api_view(['POST'])
def getCountryStates(request):
    context = {}
    country_id = request.POST['country_id']
    page_items = models.State.objects.filter(country_id=country_id)
    context.update(
        {'status': 200, 'message': "States Fetched Successfully", 'page_items': serializers.serialize('json', page_items)})
    return JsonResponse(context)


@api_view(['POST'])
def getStateCities(request):
    context = {}
    state_id = request.POST['state_id']
    page_items = models.City.objects.filter(state_id=state_id)
    context.update(
        {'status': 200, 'message': "Cities Fetched Successfully", 'page_items': serializers.serialize('json', page_items)})
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def roleList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        role = list(models.Role.objects.filter(pk=id)[:1].values('pk', 'name'))
        context.update({
            'status': 200,
            'message': "Role Fetched Successfully.",
            'page_items': role,
        })
    else:
        if keyword is not None and keyword != "":
            roles = list(models.Role.objects.filter(
                name__icontains=keyword, status=1, deleted=0).values('pk', 'name'))
        else:
            roles = list(models.Role.objects.filter(
                status=1, deleted=0).values('pk', 'name'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Roles Fetched Successfully.",
                'page_items': roles,
            })
            return JsonResponse(context)
        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(roles, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Roles Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def roleAdd(request):
    context = {}
    if not request.POST['name']:
        context.update({
            'status': 502,
            'message': "Name has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Role.objects.filter(
        name__iexact=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 503,
            'message': "Role with this name already exists."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            role = models.Role()
            role.name = request.POST['name']
            role.save()
            role_permission_details = []
            for index, elem in enumerate(request.POST.getlist('permission')):
                role_permission_details.append(models.Role_Permission(
                    permission_id=elem, role_id=role.id, permitted=1))
            models.Role_Permission.objects.bulk_create(role_permission_details)
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Role Created Successfully."
        })
    except Exception:
        context.update({
            'status': 504,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def roleEdit(request):
    context = {}
    if not request.POST['name']:
        context.update({
            'status': 505,
            'message': "Name has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Role.objects.filter(
        name__iexact=request.POST['name']).exclude(id=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 506,
            'message': "Role with this name already exists."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            role = models.Role.objects.prefetch_related(
                'role_permission_set').get(pk=request.POST['id'])
            role.name = request.POST['name']
            role.updated_at = datetime.now()
            role.save()
            role.role_permission_set.all().delete()
            role_permission_details = []
            for index, elem in enumerate(request.POST.getlist('permission')):
                role_permission_details.append(models.Role_Permission(
                    permission_id=elem, role_id=role.id, permitted=1))
            models.Role_Permission.objects.bulk_create(role_permission_details)
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Role Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 507,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def roleDelete(request):
    context = {}
    role = models.Role.objects.prefetch_related(
        'role_permission_set', 'user_set').get(pk=request.POST['id'])
    if len(role.user_set.all()) > 0:
        context.update({
            'status': 507,
            'message': "Can not delete as " + str(len(role.user_set.all())) + " user(s) exist with this role."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            role.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Role Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 508,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        user = list(models.User.objects.filter(pk=id)[:1].values(
            'pk', 'name', 'email', 'phone', 'role__name'))
        context.update({
            'status': 200,
            'message': "User Fetched Successfully.",
            'page_items': user,
        })
    else:
        if keyword is not None and keyword != "":
            users = list(models.User.objects.filter(
                Q(name__icontains=keyword) | Q(email__icontains=keyword) | Q(
                    phone__icontains=keyword) | Q(role__name__icontains=keyword)
            ).filter(status=1, deleted=0).exclude(is_superuser=1).values('pk', 'name', 'email', 'phone', 'role__name'))
        else:
            users = list(models.User.objects.filter(status=1, deleted=0).exclude(
                is_superuser=1).values('pk', 'name', 'email', 'phone', 'role__name'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Users Fetched Successfully.",
                'page_items': users,
            })
            return JsonResponse(context)
        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(users, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Users Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def userAdd(request):
    context = {}
    if not request.POST['name'] or not request.POST['role_id'] or not request.POST['email'] or not request.POST['phone'] or not request.POST['password'] or not request.POST['confirm_password']:
        context.update({
            'status': 508,
            'message': "Name/Role/Email/Phone/Password/Confirmed Password has not been provided."
        })
        return JsonResponse(context)
    if request.POST['password'] != request.POST['confirm_password']:
        context.update({
            'status': 509,
            'message': "Passwords do not match."
        })
        return JsonResponse(context)
    exist_data = models.User.objects.filter(
        Q(email__iexact=request.POST['email']) | Q(phone__iexact=request.POST['phone'])).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 510,
            'message': "User with this email or phone number already exists."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            user = models.User()
            user.username = request.POST['email']
            user.email = request.POST['email']
            user.phone = request.POST['phone']
            user.name = request.POST['name']
            user.pswd_token = request.POST['password']
            user.password = make_password(request.POST['password'])
            user.role_id = request.POST['role_id']
            user.is_superuser = 0
            user.status = 1
            user.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "User Created Successfully."
        })
    except Exception:
        context.update({
            'status': 511,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def userEdit(request):
    context = {}
    if not request.POST['name'] or not request.POST['role_id'] or not request.POST['email'] or not request.POST['phone'] or \
            request.POST['password'] or not request.POST['confirm_password']:
        context.update({
            'status': 512,
            'message': "Name/Role/Email/Phone/Password/Confirmed Password has not been provided."
        })
        return JsonResponse(context)
    if request.POST['password'] != "" or not request.POST['confirm_password'] != "":
        if request.POST['password'] != request.POST['confirm_password']:
            context.update({
                'status': 513,
                'message': "Passwords do not match."
            })
            return JsonResponse(context)
    exist_data = models.User.objects.filter(Q(email__iexact=request.POST['email']) | Q(
        phone__iexact=request.POST['phone'])).exclude(id=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 514,
            'message': "User with this email or phone number already exists."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            user = models.User.objects.get(pk=request.POST['id'])
            user.username = request.POST['email']
            user.email = request.POST['email']
            user.phone = request.POST['phone']
            user.name = request.POST['name']
            if request.POST['password'] != "":
                user.pswd_token = request.POST['password']
                user.password = make_password(request.POST['password'])
            user.role_id = request.POST['role_id']
            user.updated_at = datetime.now()
            user.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "User Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 515,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def userDelete(request):
    context = {}
    user = models.User.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            user.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "User Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 516,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendorList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        vendor = list(models.Vendor.objects.filter(pk=id)[:1].values('pk', 'name', 'address', 'country__pk', 'state__pk', 'city__pk',
                      'country__name', 'state__name', 'city__name', 'pin', 'gst_no', 'contact_no', 'contact_name', 'contact_email'))
        if len(vendor) > 0:
            purchase_order_count = models.Purchase_Order.objects.filter(
                vendor_id=vendor[0]['pk']).count()
            vendor[0]['next_purchase_order_number'] = env("PURCHASE_ORDER_NUMBER_SEQ").replace("${VENDOR_SHORT}", ''.join(word[0] for word in vendor[0]['name'].split())).replace(
                "${AI_DIGIT_3}", str(purchase_order_count + 1).zfill(3)).replace("${FINANCE_YEAR}", datetime.today().strftime('%y') + "-" + (datetime(datetime.today().year + 1, 1, 1).strftime('%y')))
        context.update({
            'status': 200,
            'message': "Vendor Fetched Successfully.",
            'page_items': vendor,
        })
    else:
        if keyword is not None and keyword != "":
            vendors = list(models.Vendor.objects.filter(Q(name__icontains=keyword) | Q(contact_name__icontains=keyword) | Q(contact_email__icontains=keyword) | Q(contact_no__icontains=keyword) | Q(pin__icontains=keyword) | Q(city__name__icontains=keyword)).filter(status=1, deleted=0).values(
                'pk', 'name', 'address', 'country__pk', 'state__pk', 'city__pk', 'country__name', 'state__name',
                'city__name', 'pin', 'gst_no', 'contact_no', 'contact_name', 'contact_email'))
        else:
            vendors = list(
                models.Vendor.objects.filter(status=1, deleted=0).values('pk', 'name', 'address', 'country__pk', 'state__pk', 'city__pk', 'country__name', 'state__name', 'city__name', 'pin', 'gst_no', 'contact_no', 'contact_name', 'contact_email'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Vendors Fetched Successfully.",
                'page_items': vendors,
            })
            return JsonResponse(context)
        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(vendors, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Vendors Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vendorAdd(request):
    context = {}
    if not request.POST['name'] or not request.POST['contact_name'] or not request.POST['contact_email'] or not request.POST['contact_no'] or not request.POST['gst_no'] or not request.POST['pin'] or not request.POST['address'] or not request.POST['country_id'] or not request.POST['state_id'] or not request.POST['city_id']:
        context.update({
            'status': 517,
            'message': "Name/Contact Name/Contact Email/Contact No/GST Number/Pin/Address/Country/State/City has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Vendor.objects.filter(Q(contact_email__iexact=request.POST['contact_email']) | Q(
        contact_no__iexact=request.POST['contact_no'])).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 518,
            'message': "Vendor with this email or phone number already exists."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            vendor = models.Vendor()
            vendor.name = request.POST['name']
            vendor.contact_name = request.POST['contact_name']
            vendor.contact_email = request.POST['contact_email']
            vendor.contact_no = request.POST['contact_no']
            vendor.gst_no = request.POST['gst_no']
            vendor.pin = request.POST['pin']
            vendor.address = request.POST['address']
            vendor.country_id = request.POST['country_id']
            vendor.state_id = request.POST['state_id']
            vendor.city_id = request.POST['city_id']
            vendor.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Vendor Created Successfully."
        })
    except Exception:
        context.update({
            'status': 519,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vendorEdit(request):
    context = {}
    if not request.POST['name'] or not request.POST['contact_name'] or not request.POST['contact_email'] or not request.POST['contact_no'] or not request.POST['gst_no'] or not request.POST['pin'] or not request.POST['address'] or not request.POST['country_id'] or not request.POST['state_id'] or not request.POST['city_id']:
        context.update({
            'status': 520,
            'message': "Name/Contact Name/Contact Email/Contact No/GST Number/Pin/Address/Country/State/City has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Vendor.objects.filter(Q(contact_email__iexact=request.POST['contact_email']) | Q(
        contact_no__iexact=request.POST['contact_no'])).exclude(id=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 521,
            'message': "Vendor with this email or phone number already exists."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            vendor = models.Vendor.objects.get(pk=request.POST['id'])
            vendor.name = request.POST['name']
            vendor.contact_name = request.POST['contact_name']
            vendor.contact_email = request.POST['contact_email']
            vendor.contact_no = request.POST['contact_no']
            vendor.gst_no = request.POST['gst_no']
            vendor.pin = request.POST['pin']
            vendor.address = request.POST['address']
            vendor.country_id = request.POST['country_id']
            vendor.state_id = request.POST['state_id']
            vendor.city_id = request.POST['city_id']
            vendor.updated_at = datetime.now()
            vendor.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Vendor Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 522,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vendorDelete(request):
    context = {}
    vendor = models.Vendor.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            vendor.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Vendor Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 523,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
def vendorExport(request):
    keyword = request.GET.get('keyword')
    if keyword is not None and keyword != "":
        page_items = models.Vendor.objects.filter(Q(name__icontains=keyword) | Q(contact_name__icontains=keyword) | Q(contact_email__icontains=keyword) | Q(
            contact_no__icontains=keyword) | Q(pin__icontains=keyword) | Q(city__name__icontains=keyword)).filter(status=1, deleted=0)
    else:
        page_items = models.Vendor.objects.filter(status=1, deleted=0)

    directory_path = settings.MEDIA_ROOT + '/reports/'
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)

    for f in os.listdir(settings.MEDIA_ROOT + '/reports/'):
        if not f.endswith(".xlsx"):
            continue
        os.remove(os.path.join(settings.MEDIA_ROOT + '/reports/', f))

    # tmpname = str(datetime.now().microsecond) + ".xlsx"
    tmpname = "Vendor" + ".xlsx"
    wb = Workbook()

    # grab the active worksheet
    ws = wb.active

    # Data can be assigned directly to cells
    ws['A1'] = "Name"
    ws['B1'] = "Address"
    ws['C1'] = "Contact Name"
    ws['D1'] = "Contact Number"
    ws['E1'] = "Contact Email"
    ws['F1'] = "GST Number"
    ws['G1'] = "Country"
    ws['H1'] = "State"
    ws['I1'] = "City"
    ws['J1'] = "Pin"

    # Rows can also be appended
    for each in page_items:
        ws.append([each.name, each.address, each.contact_name, each.contact_no,
                  each.contact_email, each.gst_no, each.country.name, each.state.name, each.city.name, each.pin])

    # Save the file
    wb.save(settings.MEDIA_ROOT + '/reports/' + tmpname)
    os.chmod(settings.MEDIA_ROOT + '/reports/' + tmpname, 0o777)
    return JsonResponse({
        'code': 200,
        'filename': settings.MEDIA_URL + 'reports/' + tmpname,
        'name':  tmpname
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customerList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        customer = list(models.Customer.objects.filter(pk=id)[:1].values('pk', 'name', 'address', 'landmark', 'country__pk', 'state__pk',
                        'country__name', 'state__name', 'city', 'pin', 'contact_no', 'contact_name', 'contact_email', 'customer_type__name', 'photo', 'kyc_image'))
        context.update({
            'status': 200,
            'message': "Customer Fetched Successfully.",
            'page_items': customer,
        })
    else:
        if keyword is not None and keyword != "":
            customers = list(models.Customer.objects.filter(Q(name__icontains=keyword) | Q(contact_name__icontains=keyword) | Q(contact_email__icontains=keyword) | Q(contact_no__icontains=keyword) | Q(customer_type__name__icontains=keyword) | Q(pin__icontains=keyword) | Q(city__icontains=keyword)).filter(
                status=1, deleted=0).values('pk', 'name', 'address', 'landmark', 'country__pk', 'state__pk', 'country__name', 'state__name', 'city', 'pin', 'contact_no', 'contact_name', 'contact_email', 'customer_type__name', 'photo', 'kyc_image'))
        else:
            customers = list(models.Customer.objects.filter(status=1, deleted=0).values('pk', 'name', 'address', 'landmark', 'country__pk', 'state__pk',
                             'country__name', 'state__name', 'city', 'pin', 'contact_no', 'contact_name', 'contact_email', 'customer_type__name', 'photo', 'kyc_image'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Customers Fetched Successfully.",
                'page_items': customers,
            })
            return JsonResponse(context)
        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(customers, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Customers Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customerAdd(request):
    context = {}
    if not request.POST['name'] or not request.POST['contact_name'] or not request.POST['contact_email'] or not request.POST['contact_no'] or not request.POST['landmark'] or not request.POST['pin'] or not request.POST['customer_type_id'] or not request.POST['kyc_type_id'] or not request.POST['kyc_detail'] or not request.POST['address'] or not request.POST['country_id'] or not request.POST['state_id'] or not request.POST['city']:
        context.update({
            'status': 524,
            'message': "Name/Contact Name/Contact Email/Contact No/Landmark/Pin/Customer Type/KYC Type/KYC Detail/Address/Country/State/City has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Customer.objects.filter(Q(contact_email__iexact=request.POST['contact_email']) | Q(
        contact_no__iexact=request.POST['contact_no'])).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 525,
            'message': "Customer with this email or phone number already exists."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            customer = models.Customer()
            customer.name = request.POST['name']
            customer.contact_name = request.POST['contact_name']
            customer.contact_email = request.POST['contact_email']
            customer.contact_no = request.POST['contact_no']
            customer.contact_no_std = request.POST['contact_no_std']
            customer.landmark = request.POST['landmark']
            customer.pin = request.POST['pin']
            customer.customer_type_id = request.POST['customer_type_id']
            customer.kyc_type_id = request.POST['kyc_type_id']
            customer.kyc_detail = request.POST['kyc_detail']
            customer.date_of_birth = request.POST['date_of_birth'] if request.POST['date_of_birth'] != "" else None
            customer.date_of_anniversary = request.POST['date_of_anniversary']
            customer.weekly_closing_day = ", ".join(request.POST.getlist(
                'weekly_closing_day')) if 'weekly_closing_day' in request.POST.keys() else None
            customer.morning_from_time = request.POST[
                'morning_from_time'] if request.POST['date_of_birth'] != "" else None
            customer.morning_to_time = request.POST['morning_to_time'] if request.POST['date_of_birth'] != "" else None
            customer.evening_from_time = request.POST[
                'evening_from_time'] if request.POST['date_of_birth'] != "" else None
            customer.evening_to_time = request.POST['evening_to_time'] if request.POST['date_of_birth'] != "" else None
            customer.address = request.POST['address']
            customer.country_id = request.POST['country_id']
            customer.state_id = request.POST['state_id']
            customer.city = request.POST['city']
            customer.save()

            if 'photo' in request.FILES.keys():
                photo = request.FILES['photo']
                directory_path = settings.MEDIA_ROOT + "/" + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/photo/"
                path = Path(directory_path)
                path.mkdir(parents=True, exist_ok=True)
                fs = FileSystemStorage(location=settings.MEDIA_ROOT + "/" + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/photo/")
                saved_file = fs.save(photo.name, photo)
                photo_path = settings.MEDIA_URL + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/photo/" + saved_file
                customer.photo = photo_path
                customer.save()
            if 'kyc_image' in request.FILES.keys():
                kyc_image = request.FILES['kyc_image']
                directory_path = settings.MEDIA_ROOT + "/" + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/kyc/"
                path = Path(directory_path)
                path.mkdir(parents=True, exist_ok=True)
                fs = FileSystemStorage(location=settings.MEDIA_ROOT + "/" + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/kyc/")
                saved_file = fs.save(kyc_image.name, kyc_image)
                kyc_image_path = settings.MEDIA_URL + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/kyc/" + saved_file
                customer.kyc_image = kyc_image_path
                customer.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Customer Created Successfully."
        })
    except Exception:
        context.update({
            'status': 526,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customerEdit(request):
    context = {}
    if not request.POST['name'] or not request.POST['contact_name'] or not request.POST['contact_email'] or not request.POST['contact_no'] or not request.POST['landmark'] or not request.POST['pin'] or not request.POST['customer_type_id'] or not request.POST['kyc_type_id'] or not request.POST['kyc_detail'] or not request.POST['address'] or not request.POST['country_id'] or not request.POST['state_id'] or not request.POST['city']:
        context.update({
            'status': 527,
            'message': "Name/Contact Name/Contact Email/Contact No/Landmark/Pin/Customer Type/KYC Type/KYC Detail/Address/Country/State/City has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Customer.objects.filter(Q(contact_email__iexact=request.POST['contact_email']) | Q(
        contact_no__iexact=request.POST['contact_no'])).exclude(id=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 528,
            'message': "Customer with this email or phone number already exists."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            customer = models.Customer.objects.get(pk=request.POST['id'])
            customer.name = request.POST['name']
            customer.contact_name = request.POST['contact_name']
            customer.contact_email = request.POST['contact_email']
            customer.contact_no = request.POST['contact_no']
            customer.contact_no_std = request.POST['contact_no_std']
            customer.landmark = request.POST['landmark']
            customer.pin = request.POST['pin']
            customer.customer_type_id = request.POST['customer_type_id']
            customer.kyc_type_id = request.POST['kyc_type_id']
            customer.kyc_detail = request.POST['kyc_detail']
            customer.date_of_birth = request.POST['date_of_birth'] if request.POST['date_of_birth'] != "" else None
            customer.date_of_anniversary = request.POST['date_of_anniversary']
            customer.weekly_closing_day = ", ".join(request.POST.getlist(
                'weekly_closing_day')) if 'weekly_closing_day' in request.POST.keys() else None
            customer.morning_from_time = request.POST[
                'morning_from_time'] if request.POST['date_of_birth'] != "" else None
            customer.morning_to_time = request.POST['morning_to_time'] if request.POST['date_of_birth'] != "" else None
            customer.evening_from_time = request.POST[
                'evening_from_time'] if request.POST['date_of_birth'] != "" else None
            customer.evening_to_time = request.POST['evening_to_time'] if request.POST['date_of_birth'] != "" else None
            customer.address = request.POST['address']
            customer.country_id = request.POST['country_id']
            customer.state_id = request.POST['state_id']
            customer.city = request.POST['city']
            customer.updated_at = datetime.now()
            customer.save()

            if 'photo' in request.FILES.keys():
                photo = request.FILES['photo']
                directory_path = settings.MEDIA_ROOT + "/" + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/photo/"
                path = Path(directory_path)
                path.mkdir(parents=True, exist_ok=True)
                fs = FileSystemStorage(location=settings.MEDIA_ROOT + "/" + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/photo/")
                saved_file = fs.save(photo.name, photo)
                photo_path = settings.MEDIA_URL + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/photo/" + saved_file
                customer.photo = photo_path
                customer.save()
            if 'kyc_image' in request.FILES.keys():
                kyc_image = request.FILES['kyc_image']
                directory_path = settings.MEDIA_ROOT + "/" + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/kyc/"
                path = Path(directory_path)
                path.mkdir(parents=True, exist_ok=True)
                fs = FileSystemStorage(location=settings.MEDIA_ROOT + "/" + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/kyc/")
                saved_file = fs.save(kyc_image.name, kyc_image)
                kyc_image_path = settings.MEDIA_URL + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/kyc/" + saved_file
                customer.kyc_image = kyc_image_path
                customer.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Customer Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 529,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customerDelete(request):
    context = {}
    customer = models.Customer.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            customer.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Customer Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 530,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
def customerExport(request):
    keyword = request.GET.get('keyword')
    if keyword is not None and keyword != "":
        page_items = models.Customer.objects.filter(Q(name__icontains=keyword) | Q(contact_name__icontains=keyword) | Q(email__icontains=keyword) | Q(
            phone__icontains=keyword) | Q(customer_type__name__icontains=keyword) | Q(pin__icontains=keyword) | Q(city__icontains=keyword)).filter(status=1, deleted=0)
    else:
        page_items = models.Customer.objects.filter(status=1, deleted=0)

    directory_path = settings.MEDIA_ROOT + '/reports/'
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)

    for f in os.listdir(settings.MEDIA_ROOT + '/reports/'):
        if not f.endswith(".xlsx"):
            continue
        os.remove(os.path.join(settings.MEDIA_ROOT + '/reports/', f))

    # tmpname = str(datetime.now().microsecond) + ".xlsx"
    tmpname = "Customer" + ".xlsx"
    wb = Workbook()

    # grab the active worksheet
    ws = wb.active

    # Data can be assigned directly to cells
    ws['A1'] = "Name"
    ws['B1'] = "Address"
    ws['C1'] = "Contact Name"
    ws['D1'] = "Contact Number"
    ws['E1'] = "Contact Email"
    ws['F1'] = "Customer Type"
    ws['G1'] = "Country"
    ws['H1'] = "State"
    ws['I1'] = "City"
    ws['J1'] = "Pin"

    # Rows can also be appended
    for each in page_items:
        ws.append([each.name, each.address, each.contact_name, each.contact_no, each.contact_email,
                  each.customer_type.name, each.country.name, each.state.name, each.city.name, each.pin])

    # Save the file
    wb.save(settings.MEDIA_ROOT + '/reports/' + tmpname)
    os.chmod(settings.MEDIA_ROOT + '/reports/' + tmpname, 0o777)
    return JsonResponse({
        'code': 200,
        'filename': settings.MEDIA_URL + 'reports/' + tmpname,
        'name':  tmpname
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def uomList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        uom = list(models.Uom.objects.filter(pk=id)[:1].values('pk', 'name'))
        context.update({
            'status': 200,
            'message': "UOM Fetched Successfully.",
            'page_items': uom,
        })
    else:
        if keyword is not None and keyword != "":
            uoms = list(models.Uom.objects.filter(
                name__icontains=keyword, status=1, deleted=0).values('pk', 'name'))
        else:
            uoms = list(models.Uom.objects.filter(
                status=1, deleted=0).values('pk', 'name'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Uoms Fetched Successfully.",
                'page_items': uoms,
            })
            return JsonResponse(context)
        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(uoms, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "UOMs Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def uomAdd(request):
    context = {}
    if not request.POST['name']:
        context.update({
            'status': 531,
            'message': "Name has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Uom.objects.filter(
        name=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 532,
            'message': "Uom with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            uom = models.Uom()
            uom.name = request.POST['name']
            uom.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "UOM Created Successfully."
        })
    except Exception:
        context.update({
            'status': 533,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def uomEdit(request):
    context = {}
    if not request.POST['name']:
        context.update({
            'status': 534,
            'message': "Name has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Uom.objects.filter(
        name=request.POST['name']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 535,
            'message': "Uom with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            uom = models.Uom.objects.get(pk=request.POST['id'])
            uom.name = request.POST['name']
            uom.updated_at = datetime.now()
            uom.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "UOM Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 536,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def uomDelete(request):
    context = {}
    uom = models.Uom.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            uom.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "UOM Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 537,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def childUomList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        childUom = list(models.Child_Uom.objects.filter(pk=id)[:1].values(
            'pk', 'name', 'uom__name', 'conversion_rate'))
        context.update({
            'status': 200,
            'message': "UOM Fetched Successfully.",
            'page_items': childUom,
        })
    else:
        if keyword is not None and keyword != "":
            childUoms = list(models.Child_Uom.objects.filter(name__icontains=keyword, status=1, deleted=0).values(
                'pk', 'name', 'uom__name', 'conversion_rate'))
        else:
            childUoms = list(models.Child_Uom.objects.filter(status=1, deleted=0).values(
                'pk', 'name', 'uom__name', 'conversion_rate'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Child Uoms Fetched Successfully.",
                'page_items': childUoms,
            })
            return JsonResponse(context)

        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(childUoms, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "UOMs Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def childUomAdd(request):
    context = {}
    if not request.POST['name'] or not request.POST['uom_id'] or not request.POST['conversion_rate']:
        context.update({
            'status': 538,
            'message': "Name/Uom/Conversion Rate has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Child_Uom.objects.filter(
        name=request.POST['name'], uom_id=request.POST['uom_id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 539,
            'message': "Child Uom with this name and Uom already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            childUom = models.Child_Uom()
            childUom.name = request.POST['name']
            childUom.uom_id = request.POST['uom_id']
            childUom.conversion_rate = request.POST['conversion_rate']
            childUom.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Child UOM Created Successfully."
        })
    except Exception:
        context.update({
            'status': 540,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def childUomEdit(request):
    context = {}
    if not request.POST['name'] or not request.POST['uom_id'] or not request.POST['conversion_rate']:
        context.update({
            'status': 541,
            'message': "Name/Uom/Conversion Rate has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Child_Uom.objects.filter(
        name=request.POST['name'], uom_id=request.POST['uom_id']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 542,
            'message': "Child Uom with this name and Uom already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            childUom = models.Child_Uom.objects.get(pk=request.POST['id'])
            childUom.name = request.POST['name']
            childUom.uom_id = request.POST['uom_id']
            childUom.conversion_rate = request.POST['conversion_rate']
            childUom.updated_at = datetime.now()
            childUom.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Child UOM Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 543,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def childUomDelete(request):
    context = {}
    childUom = models.Child_Uom.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            childUom.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Child UOM Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 544,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def itemCategoryList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        itemCategory = list(models.Item_Category.objects.get(
            pk=id).values('pk', 'name'))
        context.update({
            'status': 200,
            'message': "Item Category Fetched Successfully.",
            'page_items': itemCategory,
        })
    else:
        if keyword is not None and keyword != "":
            itemCategories = list(models.Item_Category.objects.filter(
                name__icontains=keyword, status=1, deleted=0).values('pk', 'name'))
        else:
            itemCategories = list(models.Item_Category.objects.filter(
                status=1, deleted=0).values('pk', 'name'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Item Categories Fetched Successfully.",
                'page_items': itemCategories,
            })
            return JsonResponse(context)
        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(itemCategories, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Item Categories Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemCategoryAdd(request):
    context = {}
    if not request.POST['name']:
        context.update({
            'status': 545,
            'message': "Name has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Item_Category.objects.filter(
        name=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 546,
            'message': "Item Category with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            itemCategory = models.Item_Category()
            itemCategory.name = request.POST['name']
            itemCategory.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Category Created Successfully."
        })
    except Exception:
        context.update({
            'status': 547,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemCategoryEdit(request):
    context = {}
    if not request.POST['name']:
        context.update({
            'status': 548,
            'message': "Name has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Item_Category.objects.filter(
        name=request.POST['name']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 549,
            'message': "Item Category with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            itemCategory = models.Item_Category.objects.get(
                pk=request.POST['id'])
            itemCategory.name = request.POST['name']
            itemCategory.updated_at = datetime.now()
            itemCategory.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Category Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 550,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemCategoryDelete(request):
    context = {}
    itemCategory = models.Item_Category.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            itemCategory.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Category Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 551,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def itemTypeList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        itemType = list(models.Item_Type.objects.filter(pk=id)[:1].values(
            'pk', 'name', 'item_category__name', 'hsn_code', 'gst_percentage'))
        context.update({
            'status': 200,
            'message': "Item Type Fetched Successfully.",
            'page_items': itemType,
        })
    else:
        if keyword is not None and keyword != "":
            itemTypes = list(models.Item_Type.objects.filter(
                Q(name__icontains=keyword) | Q(item_category__name__icontains=keyword) | Q(
                    hsn_code__icontains=keyword)
            ).filter(status=1, deleted=0).values(
                'pk', 'name', 'item_category__name', 'hsn_code', 'gst_percentage'))
        else:
            itemTypes = list(models.Item_Type.objects.filter(status=1, deleted=0).values(
                'pk', 'name', 'item_category__name', 'hsn_code', 'gst_percentage'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Item Types Fetched Successfully.",
                'page_items': itemTypes,
            })
            return JsonResponse(context)
        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(itemTypes, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Item Types Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemTypeAdd(request):
    context = {}
    if not request.POST['name'] or not request.POST['item_category_id'] or not request.POST['hsn_code'] or not request.POST['gst_percentage']:
        context.update({
            'status': 552,
            'message': "Name/Item Category/HSN Code/GST Percentage has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Item_Type.objects.filter(
        name=request.POST['name'], item_category_id=request.POST['item_category_id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 553,
            'message': "Item Type with this name and item category already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            itemType = models.Item_Type()
            itemType.name = request.POST['name']
            itemType.item_category_id = request.POST['item_category_id']
            itemType.hsn_code = request.POST['hsn_code']
            itemType.gst_percentage = request.POST['gst_percentage']
            itemType.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Type Created Successfully."
        })
    except Exception:
        context.update({
            'status': 554,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemTypeEdit(request):
    context = {}
    if not request.POST['name'] or not request.POST['item_category_id'] or not request.POST['hsn_code'] or not request.POST['gst_percentage']:
        context.update({
            'status': 555,
            'message': "Name/Item Category/HSN Code/GST Percentage has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Item_Type.objects.filter(
        name=request.POST['name'], item_category_id=request.POST['item_category_id']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 556,
            'message': "Item Type with this name and item category already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            itemType = models.Item_Type.objects.get(pk=request.POST['id'])
            itemType.name = request.POST['name']
            itemType.item_category_id = request.POST['item_category_id']
            itemType.hsn_code = request.POST['hsn_code']
            itemType.gst_percentage = request.POST['gst_percentage']
            itemType.updated_at = datetime.now()
            itemType.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Type Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 557,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemTypeDelete(request):
    context = {}
    itemType = models.Item_Type.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            itemType.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Type Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 558,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def itemColorList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        itemColor = list(models.Item_Color.objects.get(
            pk=id).values('pk', 'name', 'color_code'))
        context.update({
            'status': 200,
            'message': "Item Color Fetched Successfully.",
            'page_items': itemColor,
        })
    else:
        if keyword is not None and keyword != "":
            itemColors = list(models.Item_Color.objects.filter(
                name__icontains=keyword, status=1, deleted=0).values('pk', 'name', 'color_code'))
        else:
            itemColors = list(models.Item_Color.objects.filter(
                status=1, deleted=0).values('pk', 'name', 'color_code'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Item Colors Fetched Successfully.",
                'page_items': itemColors,
            })
            return JsonResponse(context)
        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(itemColors, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Item Colors Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemColorAdd(request):
    context = {}
    if not request.POST['name'] or not request.POST['color_code']:
        context.update({
            'status': 559,
            'message': "Name/Color Code has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Item_Color.objects.filter(
        name=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 560,
            'message': "Item Color with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            itemColor = models.Item_Color()
            itemColor.name = request.POST['name']
            itemColor.color_code = request.POST['color_code']
            itemColor.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Color Created Successfully."
        })
    except Exception:
        context.update({
            'status': 561,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemColorEdit(request):
    context = {}
    if not request.POST['name'] or not request.POST['color_code']:
        context.update({
            'status': 562,
            'message': "Name/Color Code has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Item_Color.objects.filter(
        name=request.POST['name']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 563,
            'message': "Item Color with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            itemColor = models.Item_Color.objects.get(pk=request.POST['id'])
            itemColor.name = request.POST['name']
            itemColor.color_code = request.POST['color_code']
            itemColor.updated_at = datetime.now()
            itemColor.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Color Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 564,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemColorDelete(request):
    context = {}
    itemColor = models.Item_Color.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            itemColor.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Color Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 565,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def itemList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        item = list(models.Item.objects.filter(pk=id)[:1].values(
            'pk', 'name', 'item_type__name', 'item_type__item_category__name', 'item_type__gst_percentage', 'uom__name', 'price'))
        context.update({
            'status': 200,
            'message': "Item Fetched Successfully.",
            'page_items': item,
        })
    else:
        if keyword is not None and keyword != "":
            items = list(models.Item.objects.filter(Q(name__icontains=keyword) | Q(item_type__name__icontains=keyword) | Q(uom__name__icontains=keyword)).filter(
                status=1, deleted=0).values('pk', 'name', 'item_type__name', 'item_type__item_category__name', 'item_type__gst_percentage', 'uom__name', 'price'))
        else:
            items = list(models.Item.objects.filter(status=1, deleted=0).values(
                'pk', 'name', 'item_type__name', 'item_type__item_category__name', 'item_type__gst_percentage', 'uom__name', 'price'))

        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Items Fetched Successfully.",
                'page_items': items,
            })
            return JsonResponse(context)

        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(items, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Items Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemAdd(request):
    context = {}
    if not request.POST['name'] or not request.POST['uom_id'] or not request.POST['item_type_id']:
        context.update({
            'status': 566,
            'message': "Name/UOM/Item Type/Price has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Item.objects.filter(
        name__iexact=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 567,
            'message': "Item with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            item = models.Item()
            item.name = request.POST['name']
            item.uom_id = request.POST['uom_id']
            item.item_type_id = request.POST['item_type_id']
            if request.POST['price']:
                item.price = request.POST['price']
            item.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Created Successfully."
        })
    except Exception:
        context.update({
            'status': 568,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemEdit(request):
    context = {}
    if not request.POST['name'] or not request.POST['uom_id'] or not request.POST['item_type_id'] or not request.POST['price']:
        context.update({
            'status': 569,
            'message': "Name/UOM/Item Type/Price has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Item.objects.filter(name__iexact=request.POST['name']).exclude(
        pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 570,
            'message': "Item with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            item = models.Item.objects.get(pk=request.POST['id'])
            item.name = request.POST['name']
            item.item_type_id = request.POST['item_type_id']
            item.uom_id = request.POST['uom_id']
            item.price = request.POST['price']
            item.updated_at = datetime.now()
            item.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 571,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemDelete(request):
    context = {}
    item = models.Item.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            item.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 572,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
def itemExport(request):
    keyword = request.GET.get('keyword')
    if keyword is not None and keyword != "":
        page_items = models.Item.objects.filter(Q(name__icontains=keyword) | Q(
            item_type__name__icontains=keyword) | Q(uom__name__icontains=keyword)).filter(status=1, deleted=0)
    else:
        page_items = models.Item.objects.filter(status=1, deleted=0)

    directory_path = settings.MEDIA_ROOT + '/reports/'
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)

    for f in os.listdir(settings.MEDIA_ROOT + '/reports/'):
        if not f.endswith(".xlsx"):
            continue
        os.remove(os.path.join(settings.MEDIA_ROOT + '/reports/', f))

    # tmpname = str(datetime.now().microsecond) + ".xlsx"
    tmpname = "Item" + ".xlsx"
    wb = Workbook()

    # grab the active worksheet
    ws = wb.active

    # Data can be assigned directly to cells
    ws['A1'] = "Name"
    ws['B1'] = "Item Type"
    ws['C1'] = "Item Category"
    ws['D1'] = "UOM"
    ws['E1'] = "Price"

    # Rows can also be appended
    for each in page_items:
        ws.append([each.name, each.item_type.name,
                  each.item_type.item_category.name, each.uom.name, each.price])

    # Save the file
    wb.save(settings.MEDIA_ROOT + '/reports/' + tmpname)
    os.chmod(settings.MEDIA_ROOT + '/reports/' + tmpname, 0o777)
    return JsonResponse({
        'code': 200,
        'filename': settings.MEDIA_URL + 'reports/' + tmpname,
        'name':  tmpname
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def storeList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    store_type=request.GET.get('store_type', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        store = list(models.Store.objects.filter(pk=id)[:1].values(
            'pk', 'name', 'address', 'contact_name', 'contact_no', 'contact_email', 'manager_name', 'pin', 'city__name', 'state__name', 'country__name'))
        context.update({
            'status': 200,
            'message': "Store Fetched Successfully.",
            'page_items': store,
        })
    else:
        if keyword is not None and keyword != "":
            stores = list(models.Store.objects.filter(Q(name__icontains=keyword) | Q(address__icontains=keyword) | Q(contact_name__icontains=keyword) | Q(contact_no__icontains=keyword) | Q(contact_email__icontains=keyword) | Q(manager_name__icontains=keyword) | Q(pin__icontains=keyword)).filter(
                status=1, deleted=0).values('pk', 'name', 'address', 'contact_name', 'contact_no', 'contact_email', 'manager_name', 'pin', 'city__name', 'state__name', 'country__name'))
        else:
            stores = list(models.Store.objects.filter(status=1, deleted=0).values('pk', 'name', 'address', 'contact_name',
                          'contact_no', 'contact_email', 'manager_name', 'pin', 'city__name', 'state__name', 'country__name'))

        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Stores Fetched Successfully.",
                'page_items': stores,
            })
            return JsonResponse(context)

        if store_type is not None :
            if store_type=="InHouse":
                stores = list(models.Store.objects.filter(status=1, deleted=0,vendor_id=None).values('pk', 'name', 'address', 'contact_name',
                              'contact_no', 'contact_email', 'manager_name', 'pin', 'city__name', 'state__name', 'country__name'))
                context.update({
                    'status': 200,
                    'message': "Stores Fetched Successfully.",
                    'page_items': stores,
                })
                return JsonResponse(context)

            if store_type=="Vendor":
                stores = list(models.Store.objects.filter(status=1, deleted=0,vendor_id__isnull=False).values('pk', 'name', 'address', 'contact_name',
                              'contact_no', 'contact_email', 'manager_name', 'pin', 'vendor_id', 'city__name', 'state__name', 'country__name'))
                context.update({
                    'status': 200,
                    'message': "Stores Fetched Successfully.",
                    'page_items': stores,
                })
                return JsonResponse(context)

        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(stores, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Stores Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def storeAdd(request):
    context = {}
    if not request.POST['name'] or not request.POST['address'] or not request.POST['contact_name'] or not request.POST['contact_no'] or not request.POST['contact_email'] or not request.POST['pin'] or not request.POST['city_id'] or not request.POST['state_id'] or not request.POST['country_id']:
        context.update({
            'status': 566,
            'message': "Name/Address/Contact Name/Contact Number/Contact Email/Pin/City/State/Country has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Store.objects.filter(
        name__iexact=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 567,
            'message': "Store with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            store = models.Store()
            store.name = request.POST['name']
            store.address = request.POST['address']
            store.country_id = request.POST['country_id']
            store.state_id = request.POST['state_id']
            store.city_id = request.POST['city_id']
            store.pin = request.POST['pin']
            store.contact_name = request.POST['contact_name']
            store.contact_no = request.POST['contact_no']
            store.contact_email = request.POST['contact_email']
            store.manager_name = request.POST['manager_name']
            store.vendor_id = request.POST['vendor_id'] if 'vendor_id' in request.POST.keys() else None
            store.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Store Created Successfully."
        })
    except Exception:
        context.update({
            'status': 568,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def storeEdit(request):
    context = {}
    if not request.POST['name'] or not request.POST['address'] or not request.POST['contact_name'] or not request.POST['contact_no'] or not request.POST['contact_email'] or not request.POST['pin'] or not request.POST['city_id'] or not request.POST['state_id'] or not request.POST['country_id']:
        context.update({
            'status': 566,
            'message': "Name/Address/Contact Name/Contact Number/Contact Email/Pin/City/State/Country has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Store.objects.filter(name__iexact=request.POST['name']).exclude(
        pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 570,
            'message': "Store with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            store = models.Store.objects.get(pk=request.POST['id'])
            store.name = request.POST['name']
            store.address = request.POST['address']
            store.country_id = request.POST['country_id']
            store.state_id = request.POST['state_id']
            store.city_id = request.POST['city_id']
            store.pin = request.POST['pin']
            store.contact_name = request.POST['contact_name']
            store.contact_no = request.POST['contact_no']
            store.contact_email = request.POST['contact_email']
            store.manager_name = request.POST['manager_name']
            store.vendor_id = request.POST['vendor_id'] if 'vendor_id' in request.POST.keys() else None
            store.updated_at = datetime.now()
            store.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Store Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 571,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def storeDelete(request):
    context = {}
    store = models.Store.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            store.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Store Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 572,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
def storeExport(request):
    keyword = request.GET.get('keyword')
    if keyword is not None and keyword != "":
        page_items = models.Store.objects.filter(Q(name__icontains=keyword) | Q(address__icontains=keyword) | Q(contact_name__icontains=keyword) | Q(
            contact_no__icontains=keyword) | Q(contact_email__icontains=keyword) | Q(manager_name__icontains=keyword) | Q(pin__icontains=keyword)).filter(status=1, deleted=0)
    else:
        page_items = models.Store.objects.filter(status=1, deleted=0)

    directory_path = settings.MEDIA_ROOT + '/reports/'
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)

    for f in os.listdir(settings.MEDIA_ROOT + '/reports/'):
        if not f.endswith(".xlsx"):
            continue
        os.remove(os.path.join(settings.MEDIA_ROOT + '/reports/', f))

    # tmpname = str(datetime.now().microsecond) + ".xlsx"
    tmpname = "Store" + ".xlsx"
    wb = Workbook()

    # grab the active worksheet
    ws = wb.active

    # Data can be assigned directly to cells
    ws['A1'] = "Name"
    ws['B1'] = "Address"
    ws['C1'] = "Contact Name"
    ws['D1'] = "Contact Number"
    ws['E1'] = "Contact Email"
    ws['F1'] = "Manager"
    ws['G1'] = "Pin"
    ws['H1'] = "City"
    ws['I1'] = "State"
    ws['J1'] = "Country"

    # Rows can also be appended
    for each in page_items:
        ws.append([each.name, each.address, each.contact_name, each.contact_no, each.contact_email,
                  each.manager_name, each.pin, each.city.name, each.state.name, each.country.name])

    # Save the file
    wb.save(settings.MEDIA_ROOT + '/reports/' + tmpname)
    os.chmod(settings.MEDIA_ROOT + '/reports/' + tmpname, 0o777)
    return JsonResponse({
        'code': 200,
        'filename': settings.MEDIA_URL + 'reports/' + tmpname,
        'name':  tmpname
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billOfMaterialList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    level = request.GET.get('level', None)
    keyword = request.GET.get('keyword', None)
    item_id = request.GET.get('item_id', None)
    if id is not None and id != "":
        billOfMaterial = list(models.Bill_Of_Material.objects.filter(
            pk=id)[:1].values('pk', 'bom_item__name', 'uom__name', 'quantity', 'price'))
        context.update({
            'status': 200,
            'message': "Bill Of Material Fetched Successfully.",
            'page_items': billOfMaterial,
        })
    if item_id is not None and item_id != "":
        billOfMaterial = list(models.Bill_Of_Material.objects.filter(
            pk=id)[:1].values('pk', 'bom_item__name', 'uom__name', 'quantity', 'price'))
        context.update({
            'status': 200,
            'message': "Bill Of Material Fetched Successfully.",
            'page_items': billOfMaterial,
        })
    else:
        if keyword is not None and keyword != "":
            billOfMaterials = models.Bill_Of_Material.objects.filter(
                Q(bom_item__name__icontains=keyword) | Q(uom__name__icontains=keyword) | Q(price__icontains=keyword)).filter(status=1, deleted=0)
        else:
            billOfMaterials = models.Bill_Of_Material.objects.filter(
                status=1, deleted=0)
        if level is not None:
            billOfMaterials = billOfMaterials.filter(level__lte=level)
        billOfMaterials = list(billOfMaterials.values(
            'pk', 'bom_item__name', 'uom__name', 'quantity', 'price'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Bill Of Materials Fetched Successfully.",
                'page_items': billOfMaterials,
            })
            return JsonResponse(context)

        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(billOfMaterials, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "BOM Levels Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def billOfMaterialAdd(request):
    context = {}
    if not request.POST['bom_item_id'] or not request.POST['uom_id'] or not request.POST['total_amount'] or not request.POST['level']:
        context.update({
            'status': 573,
            'message': "BOM Item/UOM/Total Amount/Level has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Bill_Of_Material.objects.filter(
        bom_item_id=request.POST['bom_item_id'], level=request.POST['level']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 574,
            'message': "Bill Of Material with this item as BOM and level already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            billOfMaterialHeader = models.Bill_Of_Material()
            billOfMaterialHeader.bom_item_id = request.POST['bom_item_id']
            billOfMaterialHeader.uom_id = request.POST['uom_id']
            billOfMaterialHeader.quantity = 1
            billOfMaterialHeader.price = request.POST['total_amount']
            billOfMaterialHeader.level = request.POST['level']
            billOfMaterialHeader.save()
            if len(models.Bill_Of_Material_Detail.objects.filter(bom_level_id=billOfMaterialHeader.id)) == 0:
                billOfMaterialHeader.is_final = 1
                billOfMaterialHeader.save()
            bom_item=models.Item.objects.get(pk=billOfMaterialHeader.bom_item_id)
            bom_item.price=billOfMaterialHeader.price
            bom_item.save()
            bill_of_material_details = []
            for index, elem in enumerate(request.POST.getlist('bom_level_id')):
                billOfMaterialDetail = models.Bill_Of_Material.objects.get(
                    pk=elem)
                billOfMaterialDetail.is_final = 0
                billOfMaterialDetail.save()
                bill_of_material_details.append(models.Bill_Of_Material_Detail(bill_of_material_header_id=billOfMaterialHeader.id,
                                                bom_level_id=elem, quantity=request.POST.getlist('bom_level_quantity')[index], price=request.POST.getlist('bom_level_price')[index]))
            for index, elem in enumerate(request.POST.getlist('item_id')):
                bill_of_material_details.append(models.Bill_Of_Material_Detail(
                    bill_of_material_header_id=billOfMaterialHeader.id,
                    item_id=elem,
                    quantity=request.POST.getlist('item_quantity')[index],
                    price=request.POST.getlist('item_price')[index])
                )
            models.Bill_Of_Material_Detail.objects.bulk_create(bill_of_material_details)
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Bill Of Material Created Successfully."
        })
    except Exception:
        context.update({
            'status': 575,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def billOfMaterialEdit(request):
    context = {}
    if not request.POST['bom_item_id'] or not request.POST['uom_id'] or not request.POST['total_amount'] or not request.POST['level']:
        context.update({
            'status': 576,
            'message': "BOM Item/UOM/Total Amount/Level has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Bill_Of_Material.objects.filter(
        bom_item_id=request.POST['bom_item_id'], level=request.POST['level']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 577,
            'message': "Bill Of Material with this item as bom already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            billOfMaterialHeader = models.Bill_Of_Material.objects.prefetch_related(
                'bill_of_material_detail_set').get(pk=request.POST['id'])
            billOfMaterialHeader.bom_item_id = request.POST['bom_item_id']
            billOfMaterialHeader.uom_id = request.POST['uom_id']
            billOfMaterialHeader.quantity = 1
            billOfMaterialHeader.price = request.POST['total_amount']
            billOfMaterialHeader.level = request.POST['level']
            billOfMaterialHeader.updated_at = datetime.now()
            billOfMaterialHeader.save()
            bom_item = models.Item.objects.get(pk=billOfMaterialHeader.bom_item_id)
            bom_item.price = billOfMaterialHeader.price
            bom_item.save()

            for bom_detail in models.Bill_Of_Material_Detail.objects.filter(bom_level_id=request.POST['id']):
                bom_detail.price=float(bom_detail.quantity) * float(request.POST['total_amount'])
                bom_detail.save()

            if len(models.Bill_Of_Material_Detail.objects.filter(bom_level_id=billOfMaterialHeader.id)) == 0:
                billOfMaterialHeader.is_final = 1
                billOfMaterialHeader.save()
            billOfMaterialHeader.bill_of_material_detail_set.all().delete()
            bill_of_material_details = []
            for index, elem in enumerate(request.POST.getlist('bom_level_id')):
                billOfMaterialDetail = models.Bill_Of_Material.objects.get(pk=elem)
                billOfMaterialDetail.is_final = 0
                billOfMaterialDetail.save()
                bill_of_material_details.append(models.Bill_Of_Material_Detail(bill_of_material_header_id=billOfMaterialHeader.id,
                                                bom_level_id=elem, quantity=request.POST.getlist('bom_level_quantity')[index], price=request.POST.getlist('bom_level_price')[index]))
            for index, elem in enumerate(request.POST.getlist('item_id')):
                bill_of_material_details.append(models.Bill_Of_Material_Detail(bill_of_material_header_id=billOfMaterialHeader.id,
                                                item_id=elem, quantity=request.POST.getlist('item_quantity')[index], price=request.POST.getlist('item_price')[index]))
            models.Bill_Of_Material_Detail.objects.bulk_create(
                bill_of_material_details)
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Bill Of Material Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 578,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def billOfMaterialDelete(request):
    context = {}
    bomLevel = models.Bill_Of_Material.objects.get(
        pk=request.POST['id'])
    try:
        with transaction.atomic():
            bomLevel.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Bill Of Material Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 579,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


def getStructureOfBOM(bom_id):
    billOfMaterial = list(models.Bill_Of_Material.objects.filter(pk=bom_id)[:1].values('pk', 'bom_item_id' , 'bom_item__name', 'uom__name', 'quantity', 'price'))[0]
    childBOMS = models.Bill_Of_Material_Detail.objects.filter(
        status=1, deleted=0, bill_of_material_header_id=bom_id).order_by('bom_level_id')
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


def getBillOfMaterialStructure(request):
    context = {}
    bom_id = request.GET.get('bom_id', None)
    if bom_id is not None and bom_id != "":
        billOfMaterial = getStructureOfBOM(bom_id)
        context.update({
            'status': 200,
            'message': "BOM Structure fetched successfully",
            'page_items': billOfMaterial,
        })
    else:
        context.update({
            'status': 580,
            'message': "Please Provide valid BOM id."
        })
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchaseOrderList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    vendor_id = request.GET.get('vendor_id', None)
    delivery_status = request.GET.get('delivery_status', None)
    if id is not None and id != "":
        purchaseOrder = list(models.Purchase_Order.objects.filter(pk=id)[:1].values('pk', 'order_number', 'order_date', 'quotation_number', 'quotation_date', 'reference_number', 'business_terms', 'discount_type',
                             'discount_value', 'discounted_value', 'excise_duty_percentage', 'insurance', 'octroi', 'freight', 'packing', 'payment_terms', 'delivery_schedule', 'delivery_at', 'notes', 'total_amount', 'vendor__name'))
        context.update({
            'status': 200,
            'message': "Purchase Order Fetched Successfully.",
            'page_items': purchaseOrder,
        })
    else:
        if vendor_id is not None and vendor_id != "":
            purchaseOrders = models.Purchase_Order.objects.filter(
                vendor_id=vendor_id).filter(status=1, deleted=0)
        else:
            purchaseOrders = models.Purchase_Order.objects.filter(
                status=1, deleted=0)
        if delivery_status is not None and delivery_status != "":
            purchaseOrders = purchaseOrders.filter(
                delivery_status__in=delivery_status.split(","))
        if keyword is not None and keyword != "":
            purchaseOrders = purchaseOrders.filter(Q(vendor__name__icontains=keyword) | Q(order_number__icontains=keyword) | Q(
                order_date__icontains=keyword) | Q(total_amount__icontains=keyword)).filter(status=1, deleted=0)
        purchaseOrders = list(purchaseOrders.values('pk', 'order_number', 'order_date', 'quotation_number', 'quotation_date', 'reference_number', 'business_terms', 'discount_type', 'discount_value',
                              'discounted_value', 'excise_duty_percentage', 'insurance', 'octroi', 'freight', 'packing', 'payment_terms', 'delivery_schedule', 'delivery_at', 'notes', 'total_amount', 'vendor__name'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Purchase Orders Fetched Successfully.",
                'page_items': purchaseOrders,
            })
            return JsonResponse(context)

        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(purchaseOrders, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Purchase Orders Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def purchaseOrderAdd(request):
    context = {}
    if not request.POST['vendor_id'] or not request.POST['order_number'] or not request.POST['order_date'] or not request.POST['quotation_number'] or not request.POST['quotation_date'] or not request.POST['total_amount']:
        context.update({
            'status': 581,
            'message': "Vendor/Order Number/Order Date/Quotation Number/Quotation Date/Total Amount has not been provided."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            purchaseOrderHeader = models.Purchase_Order()
            purchaseOrderHeader.vendor_id = request.POST['vendor_id']
            purchaseOrderHeader.order_number = request.POST['order_number']
            purchaseOrderHeader.order_date = request.POST['order_date']
            purchaseOrderHeader.quotation_number = request.POST['quotation_number']
            purchaseOrderHeader.quotation_date = request.POST['quotation_date']
            purchaseOrderHeader.reference_number = request.POST['reference_number']
            purchaseOrderHeader.business_terms = request.POST['business_terms']
            purchaseOrderHeader.discount_type = request.POST['discount_type']
            purchaseOrderHeader.discount_value = request.POST[
                'discount_value'] if request.POST['discount_value'] != "" else 0
            purchaseOrderHeader.discounted_value = request.POST[
                'discounted_value'] if request.POST['discounted_value'] != "" else 0
            purchaseOrderHeader.excise_duty_percentage = request.POST[
                'excise_duty_percentage'] if request.POST['excise_duty_percentage'] != "" else 0
            purchaseOrderHeader.insurance = request.POST['insurance'] if request.POST['insurance'] != "" else 0
            purchaseOrderHeader.octroi = request.POST['octroi'] if request.POST['octroi'] != "" else 0
            purchaseOrderHeader.freight = request.POST['freight'] if request.POST['freight'] != "" else 0
            purchaseOrderHeader.packing = request.POST['packing']
            purchaseOrderHeader.payment_terms = request.POST['payment_terms']
            purchaseOrderHeader.delivery_schedule = request.POST['delivery_schedule']
            purchaseOrderHeader.delivery_at = request.POST['delivery_at']
            purchaseOrderHeader.notes = request.POST['notes']
            purchaseOrderHeader.total_amount = request.POST['total_amount']
            purchaseOrderHeader.save()

            purchase_order_details = []
            for index, elem in enumerate(request.POST.getlist('item_id')):
                purchase_order_details.append(
                    models.Purchase_Order_Detail(
                        purchase_order_header_id=purchaseOrderHeader.id,
                        item_id=elem,
                        quantity=request.POST.getlist('item_quantity')[index],
                        rate=request.POST.getlist('rate')[index],
                        amount=request.POST.getlist('item_price')[index],
                        gst_percentage=request.POST.getlist(
                            'gst_percentage')[index],
                        amount_with_gst=request.POST.getlist(
                            'amount_with_gst')[index]
                    )
                )
            models.Purchase_Order_Detail.objects.bulk_create(
                purchase_order_details)
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Purchase Order Created Successfully."
        })
    except Exception:
        context.update({
            'status': 582,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def purchaseOrderEdit(request):
    context = {}
    if not request.POST['vendor_id'] or not request.POST['order_number'] or not request.POST['order_date'] or not request.POST['quotation_number'] or not request.POST['quotation_date'] or not request.POST['total_amount']:
        context.update({
            'status': 583,
            'message': "Vendor/Order Number/Order Date/Quotation Number/Quotation Date/Total Amount has not been provided."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            purchaseOrderHeader = models.Purchase_Order.objects.prefetch_related(
                'purchase_order_detail_set').get(pk=request.POST['id'])
            purchaseOrderHeader.vendor_id = request.POST['vendor_id']
            purchaseOrderHeader.order_number = request.POST['order_number']
            purchaseOrderHeader.order_date = request.POST['order_date']
            purchaseOrderHeader.quotation_number = request.POST['quotation_number']
            purchaseOrderHeader.quotation_date = request.POST['quotation_date']
            purchaseOrderHeader.reference_number = request.POST['reference_number']
            purchaseOrderHeader.business_terms = request.POST['business_terms']
            purchaseOrderHeader.discount_type = request.POST['discount_type']
            purchaseOrderHeader.discount_value = request.POST[
                'discount_value'] if request.POST['discount_value'] != "" else 0
            purchaseOrderHeader.discounted_value = request.POST[
                'discounted_value'] if request.POST['discounted_value'] != "" else 0
            purchaseOrderHeader.excise_duty_percentage = request.POST[
                'excise_duty_percentage'] if request.POST['excise_duty_percentage'] != "" else 0
            purchaseOrderHeader.insurance = request.POST['insurance'] if request.POST['insurance'] != "" else 0
            purchaseOrderHeader.octroi = request.POST['octroi'] if request.POST['octroi'] != "" else 0
            purchaseOrderHeader.freight = request.POST['freight'] if request.POST['freight'] != "" else 0
            purchaseOrderHeader.packing = request.POST['packing']
            purchaseOrderHeader.payment_terms = request.POST['payment_terms']
            purchaseOrderHeader.delivery_schedule = request.POST['delivery_schedule']
            purchaseOrderHeader.delivery_at = request.POST['delivery_at']
            purchaseOrderHeader.notes = request.POST['notes']
            purchaseOrderHeader.total_amount = request.POST['total_amount']
            purchaseOrderHeader.updated_at = datetime.now()
            purchaseOrderHeader.save()
            purchaseOrderHeader.purchase_order_detail_set.all().delete()

            purchase_order_details = []
            for index, elem in enumerate(request.POST.getlist('item_id')):
                purchase_order_details.append(
                    models.Purchase_Order_Detail(
                        purchase_order_header_id=purchaseOrderHeader.id,
                        item_id=elem,
                        quantity=request.POST.getlist('item_quantity')[index],
                        rate=request.POST.getlist('rate')[index],
                        amount=request.POST.getlist('item_price')[index],
                        gst_percentage=request.POST.getlist(
                            'gst_percentage')[index],
                        amount_with_gst=request.POST.getlist(
                            'amount_with_gst')[index]
                    )
                )
            models.Purchase_Order_Detail.objects.bulk_create(
                purchase_order_details)
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Purchase Order Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 584,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def purchaseOrderDelete(request):
    context = {}
    purchaseOrder = models.Purchase_Order.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            purchaseOrder.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Purchase Order Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 585,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchaseOrderDetails(request):
    context = {}
    header_id = request.GET.get('header_id', None)
    if header_id is not None and header_id != "":
        header_detail = list(models.Purchase_Order.objects.filter(id=header_id).values('pk', 'order_number', 'order_date', 'quotation_number', 'quotation_date', 'reference_number', 'business_terms', 'discount_type',
                             'discount_value', 'discounted_value', 'excise_duty_percentage', 'insurance', 'octroi', 'freight', 'packing', 'payment_terms', 'delivery_schedule', 'delivery_at', 'notes', 'total_amount', 'delivered_total_amount'))
        orderDetails = list(models.Purchase_Order_Detail.objects.filter(purchase_order_header_id=header_id).values('pk', 'quantity', 'rate', 'amount', 'gst_percentage', 'amount_with_gst', 'delivered_quantity',
                            'delivered_rate', 'delivered_amount', 'delivered_gst_percentage', 'delivered_amount_with_gst', 'item_id', 'item__name', 'purchase_order_header_id', 'purchase_order_header__order_number'))
        context.update({
            'status': 200,
            'message': "Purchase Order Details Fetched Successfully.",
            'header_detail': header_detail,
            'page_items': orderDetails,
        })
    else:
        context.update({
            'status': 588,
            'message': "Please Provide Header Id.",
        })
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transactionTypeList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        transactionType = list(models.Transaction_Type.objects.filter(pk=id)[:1].values('pk', 'name'))
        context.update({
            'status': 200,
            'message': "Transaction Type Fetched Successfully.",
            'page_items': transactionType,
        })
    else:
        if keyword is not None and keyword != "":
            transactionTypes = list(models.Transaction_Type.objects.filter(
                name__icontains=keyword, status=1, deleted=0).values('pk', 'name'))
        else:
            transactionTypes = list(models.Transaction_Type.objects.filter(
                status=1, deleted=0).values('pk', 'name'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Transaction Types Fetched Successfully.",
                'page_items': transactionTypes,
            })
            return JsonResponse(context)
        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(transactionTypes, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Transaction Types Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transactionTypeAdd(request):
    context = {}
    if not request.POST['name']:
        context.update({
            'status': 531,
            'message': "Name has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Transaction_Type.objects.filter(
        name=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 532,
            'message': "Transaction Type with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            transactionType = models.Transaction_Type()
            transactionType.name = request.POST['name']
            transactionType.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Transaction Type Created Successfully."
        })
    except Exception:
        context.update({
            'status': 533,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transactionTypeEdit(request):
    context = {}
    if not request.POST['name']:
        context.update({
            'status': 534,
            'message': "Name has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Transaction_Type.objects.filter(
        name=request.POST['name']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 535,
            'message': "Transaction Type with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            transactionType = models.Transaction_Type.objects.get(pk=request.POST['id'])
            transactionType.name = request.POST['name']
            transactionType.updated_at = datetime.now()
            transactionType.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Transaction Type Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 536,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transactionTypeDelete(request):
    context = {}
    transactionType = models.Transaction_Type.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            transactionType.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Transaction Type Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 537,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def storeItemList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        storeItem = list(models.Store_Item.objects.filter(pk=id)[:1].values(
            'pk', 'store__name', 'item__name', 'opening_qty', 'on_hand_qty', 'closing_qty'))
        context.update({
            'status': 200,
            'message': "Store Item Fetched Successfully.",
            'page_items': storeItem,
        })
    else:
        if keyword is not None and keyword != "":
            storeItems = list(
                models.Store_Item.objects.filter(
                    Q(store__name__icontains=keyword) | Q(item__name__icontains=keyword) | Q(
                        opening_qty__icontains=keyword) | Q(on_hand_qty__icontains=keyword) | Q(closing_qty__icontains=keyword)
                ).filter(
                    status=1, deleted=0).values('pk', 'store__name', 'item__name', 'opening_qty', 'on_hand_qty', 'closing_qty')
            )
        else:
            storeItems = list(models.Store_Item.objects.filter(status=1, deleted=0).values(
                'pk', 'store__name', 'item__name', 'opening_qty', 'on_hand_qty', 'closing_qty'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Store Items Fetched Successfully.",
                'page_items': storeItems,
            })
            return JsonResponse(context)

        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(storeItems, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Store Items Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def storeItemAdd(request):
    context = {}
    if not request.POST['store_id'] or not request.POST['item_id'] or not request.POST['opening_qty']:
        context.update({
            'status': 586,
            'message': "Store/Item/Opening Quantity has not been provided."
        })
        return JsonResponse(context)
    exist_data = models.Store_Item.objects.filter(
        store=request.POST['store_id'], item=request.POST['item_id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 587,
            'message': "Item in this Store already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            storeItem = models.Store_Item()
            storeItem.store_id = request.POST['store_id']
            storeItem.item_id = request.POST['item_id']
            storeItem.opening_qty = Decimal(request.POST['opening_qty'])
            storeItem.on_hand_qty = Decimal(request.POST['opening_qty'])
            storeItem.closing_qty = Decimal(request.POST['opening_qty'])
            storeItem.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Store Item Created Successfully."
        })
    except Exception:
        context.update({
            'status': 588,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def storeItemEdit(request):
    context = {}
    if not request.POST['store_id'] or not request.POST['item_id'] or not request.POST['opening_qty']:
        context.update({
            'status': 589,
            'message': "Store/Item/Opening Quantity has not been provided."
        })
        return JsonResponse(context)
        return JsonResponse(context)
    exist_data = models.Store_Item.objects.filter(
        store=request.POST['store_id'], item=request.POST['item_id']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 590,
            'message': "Item in this Store already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            storeItem = models.Store_Item.objects.get(pk=request.POST['id'])
            storeItem.store_id = request.POST['store_id']
            storeItem.item_id = request.POST['item_id']
            storeItem.opening_qty = Decimal(request.POST['opening_qty'])
            storeItem.on_hand_qty = Decimal(request.POST['opening_qty'])
            storeItem.closing_qty = Decimal(request.POST['opening_qty'])
            storeItem.updated_at = datetime.now()
            storeItem.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Store Item Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 591,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def storeItemDelete(request):
    context = {}
    storeItem = models.Store_Item.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            storeItem.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Store Item Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 592,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
def storeItemExport(request):
    keyword = request.GET.get('keyword')
    if keyword is not None and keyword != "":
        page_items = models.Store_Item.objects.filter(Q(store__name__icontains=keyword) | Q(
            item__name__icontains=keyword) | Q(opening_qty__icontains=keyword)).filter(status=1, deleted=0)
    else:
        page_items = models.Store_Item.objects.filter(status=1, deleted=0)

    directory_path = settings.MEDIA_ROOT + '/reports/'
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)

    for f in os.listdir(settings.MEDIA_ROOT + '/reports/'):
        if not f.endswith(".xlsx"):
            continue
        os.remove(os.path.join(settings.MEDIA_ROOT + '/reports/', f))

    # tmpname = str(datetime.now().microsecond) + ".xlsx"
    tmpname = "Store Item" + ".xlsx"
    wb = Workbook()

    # grab the active worksheet
    ws = wb.active

    # Data can be assigned directly to cells
    ws['A1'] = "Store"
    ws['B1'] = "Item"
    ws['C1'] = "Opening quantity"
    ws['D1'] = "On hand quantity"
    ws['E1'] = "Closing quantity"

    # Rows can also be appended
    for each in page_items:
        ws.append([each.store.name, each.item.name, each.opening_qty,
                  each.on_hand_qty, each.closing_qty])

    # Save the file
    wb.save(settings.MEDIA_ROOT + '/reports/' + tmpname)
    os.chmod(settings.MEDIA_ROOT + '/reports/' + tmpname, 0o777)
    return JsonResponse({
        'code': 200,
        'filename': settings.MEDIA_URL + 'reports/' + tmpname,
        'name':  tmpname
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def storeTransactionList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    vendor_id = request.GET.get('vendor_id', None)
    transaction_type = request.GET.get('transaction_type', None)
    if id is not None and id != "":
        storeTransaction = list(models.Store_Transaction.objects.filter(pk=id)[:1].values(
            'pk', 'transaction_number', 'transaction_date', 'total_amount', 'purchase_order_header_id', 'purchase_order_header__order_number', 'vendor__name', 'transaction_type_id', 'transaction_type__name'))
        context.update({
            'status': 200,
            'message': "Store Transaction Fetched Successfully.",
            'page_items': storeTransaction,
        })
    else:
        if transaction_type:
            storeTransactions = models.Store_Transaction.objects.filter(transaction_type__name=transaction_type)
        else:
            storeTransactions = models.Store_Transaction.objects.all()

        if keyword is not None and keyword != "":
            storeTransactions = list(storeTransactions.filter(Q(vendor__name__icontains=keyword) | Q(transaction_number__icontains=keyword) | Q(
                transaction_date__icontains=keyword) | Q(total_amount__icontains=keyword)).filter(status=1, deleted=0))
        else:
            storeTransactions = list(storeTransactions.values('pk', 'transaction_number', 'transaction_date', 'total_amount',
                                 'purchase_order_header_id', 'purchase_order_header__order_number', 'vendor__name', 'transaction_type_id', 'transaction_type__name'))

        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Store Transactions Fetched Successfully.",
                'page_items': storeTransactions,
            })
            return JsonResponse(context)

        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(storeTransactions, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Store Transactions Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def storeTransactionAdd(request):
    context = {}
    check1 = 0
    test =""
    check2 = 0
    if not request.POST['vendor_id'] or not request.POST['transaction_date'] or not request.POST['total_amount']:
        context.update({
            'status': 586,
            'message': "Transaction Type/Vendor/Transaction Date/Total Amount has not been provided."
        })
        return JsonResponse(context)
    try:
        # print("3130")
        inspect = request.POST.getlist('inspect')
        # print(request.POST)
        with transaction.atomic():
            if "1" in inspect:
                # print("3134")
                grn_inspection_transaction_count = models.Grn_Inspection_Transaction.objects.all().count()
                grnTransactionheader = models.Grn_Inspection_Transaction()
                grnTransactionheader.vendor_id = request.POST['vendor_id']
                grnTransactionheader.transaction_type_id = request.POST['transaction_type_id']
                grnTransactionheader.transaction_number = env("GRN_TRANSACTION_INSPECTION_SEQ").replace(
                    "${CURRENT_YEAR}", datetime.today().strftime('%Y')).replace("${AI_DIGIT_5}", str(grn_inspection_transaction_count + 1).zfill(5))
                # print("3143")
                if (request.POST.get('purchase_order_header_id',None)):
                    grnTransactionheader.purchase_order_header_id = request.POST[
                        'purchase_order_header_id']
                # print("3147")
                grnTransactionheader.transaction_date = request.POST['transaction_date']
                grnTransactionheader.total_amount = request.POST['total_amount']
                grnTransactionheader.notes = request.POST['notes']
                grnTransactionheader.save()
                # print("3148")
                order_details = []
                for index, elem in enumerate(request.POST.getlist('item_id')):
                    if inspect[index] == "1":
                        check1 +=1
                        # print( request.POST.getlist(
                        #             'amount_with_gst')[index])
                        order_details.append(
                            models.Grn_Inspection_Transaction_Detail(
                                grn_inspection_transaction_header_id= grnTransactionheader.id,
                                item_id=elem,
                                store_id=request.POST.getlist('store_id')[index],
                                quantity=request.POST.getlist('item_quantity')[index],
                                rate=request.POST.getlist('rate')[index],
                                amount=request.POST.getlist('item_price')[index],
                                gst_percentage=request.POST.getlist(
                                    'gst_percentage')[index],
                                amount_with_gst=request.POST.getlist(
                                    'amount_with_gst')[index]
                            )
                        )
                        # print("3170")
                models.Grn_Inspection_Transaction_Detail.objects.bulk_create(order_details)
                # print("3166")

            if "0" in inspect:
                store_transaction_count = models.Store_Transaction.objects.all().count()
                storeTransactionHeader = models.Store_Transaction()
                storeTransactionHeader.vendor_id = request.POST['vendor_id']
                storeTransactionHeader.transaction_type_id = request.POST['transaction_type_id']
                # print("3182")
                if (request.POST.get('purchase_order_header_id',None)):
                    storeTransactionHeader.purchase_order_header_id = request.POST[
                        'purchase_order_header_id']
                # print("3186")
                storeTransactionHeader.transaction_number = env("STORE_TRANSACTION_NUMBER_SEQ").replace(
                    "${CURRENT_YEAR}", datetime.today().strftime('%Y')).replace("${AI_DIGIT_5}", str(store_transaction_count + 1).zfill(5))
                storeTransactionHeader.transaction_date = request.POST['transaction_date']
                storeTransactionHeader.total_amount = request.POST['total_amount']
                storeTransactionHeader.notes = request.POST['notes']
                storeTransactionHeader.save()

                order_details = []
                for index, elem in enumerate(request.POST.getlist('item_id')):
                    if inspect[index] == "0":
                        check2 +=1
                        order_details.append(
                            models.Store_Transaction_Detail(
                                store_transaction_header_id=storeTransactionHeader.id,
                                item_id=elem,
                                store_id=request.POST.getlist('store_id')[index],
                                quantity=request.POST.getlist('item_quantity')[index],
                                rate=request.POST.getlist('rate')[index],
                                amount=request.POST.getlist('item_price')[index],
                                gst_percentage=request.POST.getlist(
                                    'gst_percentage')[index],
                                amount_with_gst=request.POST.getlist(
                                    'amount_with_gst')[index]
                            )
                        )
                        storeItem = models.Store_Item.objects.filter(
                            item_id=elem, store_id=request.POST.getlist('store_id')[index]).first()
                        if storeItem is None:
                            storeItem = models.Store_Item()
                            storeItem.opening_qty = Decimal(
                                request.POST.getlist('item_quantity')[index])
                            storeItem.on_hand_qty = Decimal(
                                request.POST.getlist('item_quantity')[index])
                            storeItem.closing_qty = Decimal(
                                request.POST.getlist('item_quantity')[index])
                            storeItem.item_id = elem
                            storeItem.store_id = request.POST.getlist('store_id')[
                                index]
                            storeItem.save()
                        else:
                            storeItem.on_hand_qty += Decimal(
                                request.POST.getlist('item_quantity')[index])
                            storeItem.closing_qty += Decimal(
                                request.POST.getlist('item_quantity')[index])
                            storeItem.updated_at = datetime.now()
                            storeItem.save()
                models.Store_Transaction_Detail.objects.bulk_create(order_details)
                if request.POST['with_purchase_order'] != "" and int(request.POST['with_purchase_order']) != 0:
                    for index, elem in enumerate(request.POST.getlist('detail_id')):
                        purchaseOrderItem = models.Purchase_Order_Detail.objects.get(
                            pk=elem)
                        purchaseOrderItem.delivered_quantity += Decimal(
                            request.POST.getlist('item_quantity')[index])
                        purchaseOrderItem.delivered_rate = Decimal(
                            request.POST.getlist('rate')[index])
                        purchaseOrderItem.delivered_amount += Decimal(
                            request.POST.getlist('item_price')[index])
                        purchaseOrderItem.delivered_gst_percentage = Decimal(
                            request.POST.getlist('gst_percentage')[index])
                        purchaseOrderItem.delivered_amount_with_gst += Decimal(
                            request.POST.getlist('amount_with_gst')[index])
                        purchaseOrderItem.updated_at = datetime.now()
                        purchaseOrderItem.save()
                    purchaseOrderHeader = models.Purchase_Order.objects.prefetch_related(
                        'purchase_order_detail_set').get(pk=request.POST['purchase_order_header_id'])
                    flag = True
                    for purchaseOrderDetail in purchaseOrderHeader.purchase_order_detail_set.all():
                        if Decimal(purchaseOrderDetail.quantity) > Decimal(purchaseOrderDetail.delivered_quantity):
                            flag = False
                            break
                    if flag == True:
                        purchaseOrderHeader.delivery_status = 3
                    else:
                        purchaseOrderHeader.delivery_status = 2
                    purchaseOrderHeader.updated_at = datetime.now()
                    purchaseOrderHeader.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Store Transaction Created Successfully."
        })
    except Exception:
        # print(test)
        context.update({
            'status': 588,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def storeTransactionEdit(request):
    context = {}
    data = request.POST
    if not request.POST['vendor_id'] or not request.POST['transaction_date'] or not request.POST['total_amount']:
        context.update({
            'status': 586,
            'message': "Transaction Type/Vendor/Transaction Date/Total Amount has not been provided."
        })
        # return JsonResponse(context)

    og_storeTransactionHeader = models.Store_Transaction.objects.get(
        pk=data['id'])
    og_purchase_order_id = og_storeTransactionHeader.purchase_order_header_id
    og_store_transaction_details = models.Store_Transaction_Detail.objects.filter(store_transaction_header=og_storeTransactionHeader)
    updated_purchase_order_id = int(data['purchase_order_header_id']) if data['purchase_order_header_id'] else None

    try:
        with transaction.atomic():
            storeTransactionHeader = models.Store_Transaction.objects.get(
                pk=data['id'])
            storeTransactionHeader.vendor_id = data['vendor_id']
            storeTransactionHeader.purchase_order_header_id = updated_purchase_order_id
            storeTransactionHeader.transaction_date = data['transaction_date']
            storeTransactionHeader.total_amount = data['total_amount']
            storeTransactionHeader.notes = data['notes']
            storeTransactionHeader.save()

            # BEFORE: With purchase order
            if (og_purchase_order_id):

                # AFTER: With Purchase order
                if (updated_purchase_order_id):

                    # AFTER: With SAME Purchase order
                    if og_purchase_order_id == updated_purchase_order_id:
                        for og_store_transaction_detail in og_store_transaction_details:

                            # Store Transaction Detail is there
                            if (str(og_store_transaction_detail.item_id) in data.getlist('item_id')):
                                # Store Transaction Detail Update
                                updated_store_transaction_detail = models.Store_Transaction_Detail.objects.get(
                                    pk=og_store_transaction_detail.id)
                                index = data.getlist('item_id').index(
                                    str(og_store_transaction_detail.item_id))
                                updated_store_transaction_detail.quantity = Decimal(
                                    data.getlist('item_quantity')[index])
                                updated_store_transaction_detail.amount = Decimal(
                                    data.getlist('item_price')[index])
                                updated_store_transaction_detail.amount_with_gst = Decimal(
                                    data.getlist('amount_with_gst')[index])
                                updated_store_transaction_detail.store_id = Decimal(
                                    data.getlist('store_id')[index])
                                updated_store_transaction_detail.save()

                                # Purchase Order Detail Update
                                updated_purchase_order_detail = models.Purchase_Order_Detail.objects.filter(purchase_order_header_id=updated_purchase_order_id).get(item_id=og_store_transaction_detail.item_id)
                                updated_purchase_order_detail.delivered_quantity -= (og_store_transaction_detail.quantity-updated_store_transaction_detail.quantity)
                                updated_purchase_order_detail.delivered_amount -= ( (og_store_transaction_detail.quantity-updated_store_transaction_detail.quantity)*updated_purchase_order_detail.delivered_rate)
                                updated_purchase_order_detail.delivered_amount_with_gst -= ( ( (og_store_transaction_detail.quantity-updated_store_transaction_detail.quantity)*updated_purchase_order_detail.delivered_rate )* (1+ (updated_purchase_order_detail.delivered_gst_percentage/100)) )
                                updated_purchase_order_detail.save()

                                # Purchase Order Header Delivery Status Update
                                purchaseOrderHeader = models.Purchase_Order.objects.prefetch_related(
                                    'purchase_order_detail_set').get(pk=updated_purchase_order_id)
                                flag = True
                                for purchaseOrderDetail in purchaseOrderHeader.purchase_order_detail_set.all():
                                    if Decimal(purchaseOrderDetail.quantity) > Decimal(purchaseOrderDetail.delivered_quantity):
                                        flag = False
                                        break
                                if flag == True:
                                    purchaseOrderHeader.delivery_status = 3
                                else:
                                    purchaseOrderHeader.delivery_status = 2
                                purchaseOrderHeader.save()

                                # Store Item Update
                                # Same store
                                if og_store_transaction_detail.store_id == updated_store_transaction_detail.store_id:
                                    storeItem = models.Store_Item.objects.filter(
                                        store_id=updated_store_transaction_detail.store_id, item_id=updated_store_transaction_detail.item_id).first()
                                    storeItem.on_hand_qty -= (
                                        og_store_transaction_detail.quantity-updated_store_transaction_detail.quantity)
                                    storeItem.closing_qty -= (
                                        og_store_transaction_detail.quantity-updated_store_transaction_detail.quantity)
                                    storeItem.save()
                                # Different Store
                                else:
                                    og_store_item = models.Store_Item.objects.filter(
                                        store_id=og_store_transaction_detail.store_id, item_id=og_store_transaction_detail.item_id).first()
                                    updated_store_item = models.Store_Item.objects.filter(
                                        store_id=updated_store_transaction_detail.store_id, item_id=updated_store_transaction_detail.item_id).first()

                                    # StoreItem does not exists
                                    if updated_store_item is None:

                                        # Creating new store item
                                        new_store_item = models.Store_Item()
                                        new_store_item.opening_qty = updated_store_transaction_detail.quantity
                                        new_store_item.on_hand_qty = updated_store_transaction_detail.quantity
                                        new_store_item.closing_qty = updated_store_transaction_detail.quantity
                                        new_store_item.item_id = updated_store_transaction_detail.item_id
                                        new_store_item.store_id = updated_store_transaction_detail.store_id
                                        new_store_item.save()

                                        # Removing quantity data from old store item
                                        og_store_item.opening_qty -= og_store_transaction_detail.quantity
                                        og_store_item.on_hand_qty -= og_store_transaction_detail.quantity
                                        og_store_item.closing_qty -= og_store_transaction_detail.quantity
                                        og_store_item.save()

                                    # StoreItem exists
                                    else:
                                        # Updating a new store item
                                        updated_store_item.on_hand_qty += updated_store_transaction_detail.quantity
                                        updated_store_item.closing_qty += updated_store_transaction_detail.quantity
                                        updated_store_item.save()

                                        # Updating an old store item
                                        og_store_item.opening_qty -= og_store_transaction_detail.quantity
                                        og_store_item.on_hand_qty -= og_store_transaction_detail.quantity
                                        og_store_item.closing_qty -= og_store_transaction_detail.quantity
                                        og_store_item.save()

                            # Store Transaction Detail is not there
                            else:

                                # Unused Store Transaction Detail Delete
                                unused_store_transaction_detail = models.Store_Transaction_Detail.objects.get(
                                    pk=og_store_transaction_detail.id).delete()

                                # Purchase Order Detail Update
                                updated_purchase_order_detail = models.Purchase_Order_Detail.objects.filter(purchase_order_header_id=updated_purchase_order_id, item_id=og_store_transaction_detail.item_id).first()
                                updated_purchase_order_detail.delivered_quantity -= og_store_transaction_detail.quantity
                                updated_purchase_order_detail.delivered_amount -= (og_store_transaction_detail.quantity*updated_purchase_order_detail.delivered_rate)
                                updated_purchase_order_detail.delivered_amount_with_gst -= ( ( og_store_transaction_detail.quantity*updated_purchase_order_detail.delivered_rate ) * ( 1 + updated_purchase_order_detail.delivered_gst_percentage/100 ) )
                                updated_purchase_order_detail.save()

                                # Purchase Order Header Delivery Status Update
                                purchaseOrderHeader = models.Purchase_Order.objects.prefetch_related(
                                    'purchase_order_detail_set').get(pk=updated_purchase_order_id)
                                flag = True
                                for purchaseOrderDetail in purchaseOrderHeader.purchase_order_detail_set.all():
                                    if Decimal(purchaseOrderDetail.quantity) > Decimal(purchaseOrderDetail.delivered_quantity):
                                        flag = False
                                        break
                                if flag == True:
                                    purchaseOrderHeader.delivery_status = 3
                                else:
                                    purchaseOrderHeader.delivery_status = 2
                                purchaseOrderHeader.save()

                                # Store Item Update
                                storeItem = models.Store_Item.objects.filter(
                                    store_id=og_store_transaction_detail.store_id, item_id=og_store_transaction_detail.item_id).first()
                                storeItem.on_hand_qty -= og_store_transaction_detail.quantity
                                storeItem.closing_qty -= og_store_transaction_detail.quantity
                                updated_store_item.save()

                    # AFTER: With DIFFERENT Purchase order
                    else:

                        # Deletion of all the previous Store transaction details connected to the store transaction being edited
                        delete_store_transaction_detail = models.Store_Transaction_Detail.objects.filter(
                            store_transaction_header=og_storeTransactionHeader)
                        delete_store_transaction_detail.delete()

                        # Updation of old purchase order details and store items
                        for og_store_transaction_detail in og_store_transaction_details:

                            # Updation of old purchase order details
                            old_purchase_order_detail = models.Purchase_Order_Detail.objects.filter(purchase_order_header_id=updated_purchase_order_id, item_id=og_store_transaction_detail.item_id).first()
                            old_purchase_order_detail.delivered_quantity -= og_store_transaction_detail.quantity
                            old_purchase_order_detail.delivered_amount -= (og_store_transaction_detail.quantity*old_purchase_order_detail.delivered_rate)
                            old_purchase_order_detail.delivered_amount_with_gst -= ( ( og_store_transaction_detail.quantity*old_purchase_order_detail.delivered_rate ) * ( 1 + old_purchase_order_detail.delivered_gst_percentage/100 ) )
                            old_purchase_order_detail.save()

                            # Updation of old Storeitems
                            updated_store_item = models.Store_Item.objects.filter(
                                item_id=og_store_transaction_detail.item_id, store_id=og_store_transaction_detail.store_id).first()
                            updated_store_item.on_hand_qty -= og_store_transaction_detail.quantity
                            updated_store_item.closing_qty -= og_store_transaction_detail.quantity
                            updated_store_item.save()

                        # Creation of store transaction order
                        order_details = []
                        for index, elem in enumerate(request.POST.getlist('item_id')):
                            order_details.append(
                                models.Store_Transaction_Detail(
                                    store_transaction_header_id=storeTransactionHeader.id,
                                    item_id=elem,
                                    store_id=request.POST.getlist('store_id')[
                                        index],
                                    quantity=request.POST.getlist(
                                        'item_quantity')[index],
                                    rate=request.POST.getlist('rate')[index],
                                    amount=request.POST.getlist(
                                        'item_price')[index],
                                    gst_percentage=request.POST.getlist(
                                        'gst_percentage')[index],
                                    amount_with_gst=request.POST.getlist(
                                        'amount_with_gst')[index]
                                )
                            )
                            storeItem = models.Store_Item.objects.filter(
                                item_id=elem, store_id=request.POST.getlist('store_id')[index]).first()
                            if storeItem is None:
                                storeItem = models.Store_Item()
                                storeItem.opening_qty = Decimal(
                                    request.POST.getlist('item_quantity')[index])
                                storeItem.on_hand_qty = Decimal(
                                    request.POST.getlist('item_quantity')[index])
                                storeItem.closing_qty = Decimal(
                                    request.POST.getlist('item_quantity')[index])
                                storeItem.item_id = elem
                                storeItem.store_id = request.POST.getlist('store_id')[
                                    index]
                                storeItem.save()
                            else:
                                storeItem.on_hand_qty += Decimal(
                                    request.POST.getlist('item_quantity')[index])
                                storeItem.closing_qty += Decimal(
                                    request.POST.getlist('item_quantity')[index])
                                storeItem.save()
                        models.Store_Transaction_Detail.objects.bulk_create(
                            order_details)

                        if request.POST['with_purchase_order'] != "" and int(request.POST['with_purchase_order']) != 0:
                            for index, elem in enumerate(request.POST.getlist('detail_id')):
                                purchaseOrderItem = models.Purchase_Order_Detail.objects.get(
                                    pk=elem)
                                purchaseOrderItem.delivered_quantity += Decimal(
                                    request.POST.getlist('item_quantity')[index])
                                purchaseOrderItem.delivered_rate = Decimal(
                                    request.POST.getlist('rate')[index])
                                purchaseOrderItem.delivered_amount += Decimal(
                                    request.POST.getlist('item_price')[index])
                                purchaseOrderItem.delivered_gst_percentage = Decimal(
                                    request.POST.getlist('gst_percentage')[index])
                                purchaseOrderItem.delivered_amount_with_gst += Decimal(
                                    request.POST.getlist('amount_with_gst')[index])
                                purchaseOrderItem.save()
                            purchaseOrderHeader = models.Purchase_Order.objects.prefetch_related(
                                'purchase_order_detail_set').get(pk=request.POST['purchase_order_header_id'])
                            flag = True
                            for purchaseOrderDetail in purchaseOrderHeader.purchase_order_detail_set.all():
                                if Decimal(purchaseOrderDetail.quantity) > Decimal(purchaseOrderDetail.delivered_quantity):
                                    flag = False
                                    break
                            if flag == True:
                                purchaseOrderHeader.delivery_status = 3
                            else:
                                purchaseOrderHeader.delivery_status = 2
                            purchaseOrderHeader.save()

                # AFTER: Without Purchase order
                else:
                    # Deletion of all the previous Store transaction details connected to the store transaction being edited
                    delete_store_transaction_detail = models.Store_Transaction_Detail.objects.filter(
                        store_transaction_header=og_storeTransactionHeader)
                    delete_store_transaction_detail.delete()

                    # Updation of old purchase order details and store items
                    for og_store_transaction_detail in og_store_transaction_details:

                        # Updation of old purchase order details
                        old_purchase_order_detail = models.Purchase_Order_Detail.objects.filter(purchase_order_header_id=updated_purchase_order_id, item_id=og_store_transaction_detail.item_id).first()
                        old_purchase_order_detail.delivered_quantity -= og_store_transaction_detail.quantity
                        old_purchase_order_detail.delivered_amount -= (og_store_transaction_detail.quantity*old_purchase_order_detail.delivered_rate)
                        old_purchase_order_detail.delivered_amount_with_gst -= ( ( og_store_transaction_detail.quantity*old_purchase_order_detail.delivered_rate ) * ( 1 + old_purchase_order_detail.delivered_gst_percentage/100 ) )
                        old_purchase_order_detail.save()

                        # Updation of old Storeitems
                        updated_store_item = models.Store_Item.objects.filter(
                            item_id=og_store_transaction_detail.item_id, store_id=og_store_transaction_detail.store_id).first()
                        updated_store_item.on_hand_qty -= og_store_transaction_detail.quantity
                        updated_store_item.closing_qty -= og_store_transaction_detail.quantity
                        updated_store_item.save()

                        # Creation of store transaction order
                        order_details = []
                        for index, elem in enumerate(request.POST.getlist('item_id')):
                            order_details.append(
                                models.Store_Transaction_Detail(
                                    store_transaction_header_id=storeTransactionHeader.id,
                                    item_id=elem,
                                    store_id=request.POST.getlist('store_id')[
                                        index],
                                    quantity=request.POST.getlist(
                                        'item_quantity')[index],
                                    rate=request.POST.getlist('rate')[index],
                                    amount=request.POST.getlist(
                                        'item_price')[index],
                                    gst_percentage=request.POST.getlist(
                                        'gst_percentage')[index],
                                    amount_with_gst=request.POST.getlist(
                                        'amount_with_gst')[index]
                                )
                            )
                            storeItem = models.Store_Item.objects.filter(
                                item_id=elem, store_id=request.POST.getlist('store_id')[index]).first()
                            if storeItem is None:
                                storeItem = models.Store_Item()
                                storeItem.opening_qty = Decimal(
                                    request.POST.getlist('item_quantity')[index])
                                storeItem.on_hand_qty = Decimal(
                                    request.POST.getlist('item_quantity')[index])
                                storeItem.closing_qty = Decimal(
                                    request.POST.getlist('item_quantity')[index])
                                storeItem.item_id = elem
                                storeItem.store_id = request.POST.getlist('store_id')[
                                    index]
                                storeItem.save()
                            else:
                                storeItem.on_hand_qty += Decimal(
                                    request.POST.getlist('item_quantity')[index])
                                storeItem.closing_qty += Decimal(
                                    request.POST.getlist('item_quantity')[index])
                                storeItem.save()

            # BEFORE: Without purchase order
            else:
                # AFTER: With Purchase order
                if (data['purchase_order_header_id']):

                    # Deletion of all the previous Store transaction details connected to the store transaction being edited
                    delete_store_transaction_detail = models.Store_Transaction_Detail.objects.filter(
                        store_transaction_header=og_storeTransactionHeader)
                    delete_store_transaction_detail.delete()

                    # Updation of StoreItem details
                    for og_store_transaction_detail in og_store_transaction_details:
                        updated_store_item = models.Store_Item.objects.filter(
                            item_id=og_store_transaction_detail.item_id, store_id=og_store_transaction_detail.store_id).first()
                        updated_store_item.on_hand_qty -= og_store_transaction_detail.quantity
                        updated_store_item.closing_qty -= og_store_transaction_detail.quantity
                        updated_store_item.save()

                    # Creation of store transaction order details
                    order_details = []
                    for index, elem in enumerate(request.POST.getlist('item_id')):
                        order_details.append(
                            models.Store_Transaction_Detail(
                                store_transaction_header_id=storeTransactionHeader.id,
                                item_id=elem,
                                store_id=request.POST.getlist('store_id')[
                                    index],
                                quantity=request.POST.getlist(
                                    'item_quantity')[index],
                                rate=request.POST.getlist('rate')[index],
                                amount=request.POST.getlist(
                                    'item_price')[index],
                                gst_percentage=request.POST.getlist(
                                    'gst_percentage')[index],
                                amount_with_gst=request.POST.getlist(
                                    'amount_with_gst')[index]
                            )
                        )
                        storeItem = models.Store_Item.objects.filter(
                            item_id=elem, store_id=request.POST.getlist('store_id')[index]).first()
                        if storeItem is None:
                            storeItem = models.Store_Item()
                            storeItem.opening_qty = Decimal(
                                request.POST.getlist('item_quantity')[index])
                            storeItem.on_hand_qty = Decimal(
                                request.POST.getlist('item_quantity')[index])
                            storeItem.closing_qty = Decimal(
                                request.POST.getlist('item_quantity')[index])
                            storeItem.item_id = elem
                            storeItem.store_id = request.POST.getlist('store_id')[
                                index]
                            storeItem.save()
                        else:
                            storeItem.on_hand_qty += Decimal(
                                request.POST.getlist('item_quantity')[index])
                            storeItem.closing_qty += Decimal(
                                request.POST.getlist('item_quantity')[index])
                            storeItem.save()
                    models.Store_Transaction_Detail.objects.bulk_create(
                        order_details)

                    # Purchase order header and purchase order details updated
                    for index, elem in enumerate(request.POST.getlist('detail_id')):
                        purchaseOrderItem = models.Purchase_Order_Detail.objects.get(
                            pk=elem)
                        purchaseOrderItem.delivered_quantity += Decimal(
                            request.POST.getlist('item_quantity')[index])
                        purchaseOrderItem.delivered_rate = Decimal(
                            request.POST.getlist('rate')[index])
                        purchaseOrderItem.delivered_amount += Decimal(
                            request.POST.getlist('item_price')[index])
                        purchaseOrderItem.delivered_gst_percentage = Decimal(
                            request.POST.getlist('gst_percentage')[index])
                        purchaseOrderItem.delivered_amount_with_gst += Decimal(
                            request.POST.getlist('amount_with_gst')[index])
                        purchaseOrderItem.save()
                    purchaseOrderHeader = models.Purchase_Order.objects.prefetch_related(
                        'purchase_order_detail_set').get(pk=request.POST['purchase_order_header_id'])
                    flag = True
                    for purchaseOrderDetail in purchaseOrderHeader.purchase_order_detail_set.all():
                        if Decimal(purchaseOrderDetail.quantity) > Decimal(purchaseOrderDetail.delivered_quantity):
                            flag = False
                            break
                    if flag == True:
                        purchaseOrderHeader.delivery_status = 3
                    else:
                        purchaseOrderHeader.delivery_status = 2
                    purchaseOrderHeader.save()

                # AFTER: Without Purchase order
                else:

                    old_item_list = [d['item_id'] for d in og_store_transaction_details.values('item_id')]
                    new_item_list = [int(x) for x in data.getlist('item_id')]

                    updated_item_list=list(set(old_item_list)&set(new_item_list))
                    added_item_list=list(set(new_item_list)-set(old_item_list))
                    removed_item_list=list(set(old_item_list)-set(new_item_list))

                    for item_id in updated_item_list:
                        index = data.getlist('item_id').index(str(item_id))
                        og_store_transaction_detail = og_store_transaction_details.filter(item_id=int(data.getlist('item_id')[index])).first()

                        # Store Item Update for Same store
                        if og_store_transaction_details.get(item_id=int(data.getlist('item_id')[index])).store_id == int(data.getlist('store_id')[index]):
                            updated_storeItem = models.Store_Item.objects.filter(item_id=int(data.getlist('item_id')[index]), store_id=int(data.getlist('store_id')[index])).first()
                            updated_storeItem.on_hand_qty -= (og_store_transaction_detail.quantity - Decimal(data.getlist('item_quantity')[index]) )
                            updated_storeItem.on_hand_qty -= (og_store_transaction_detail.quantity - Decimal(data.getlist('item_quantity')[index]) )
                            updated_storeItem.save()

                        # Store Item Update for Different store
                        else:
                            # Update old StoreItem, removal of quantity of old StoreItem
                            old_storeItem = models.Store_Item.objects.filter(item_id=og_store_transaction_detail.item_id,store_id=og_store_transaction_detail.store_id).first()
                            old_storeItem.on_hand_qty -= og_store_transaction_detail.quantity
                            old_storeItem.on_hand_qty -= og_store_transaction_detail.quantity
                            old_storeItem.save()

                            # Update new StoreItem
                            updated_storeItem = models.Store_Item.objects.filter(item_id=int(data.getlist('item_id')[index]), store_id=int(data.getlist('store_id')[index])).first()
                            if updated_storeItem is None:
                                new_storeItem = models.Store_Item()
                                new_storeItem.opening_qty = Decimal(request.POST.getlist('item_quantity')[index])
                                new_storeItem.on_hand_qty = Decimal(request.POST.getlist('item_quantity')[index])
                                new_storeItem.closing_qty = Decimal(request.POST.getlist('item_quantity')[index])
                                new_storeItem.item_id = int(data.getlist('item_id')[index])
                                new_storeItem.store_id = int(data.getlist('store_id')[index])
                                new_storeItem.save()
                            else:
                                updated_storeItem.on_hand_qty += Decimal(request.POST.getlist('item_quantity')[index])
                                updated_storeItem.closing_qty += Decimal(request.POST.getlist('item_quantity')[index])
                                updated_storeItem.updated_at = datetime.now()
                                updated_storeItem.save()

                        # Store Transaction Detail Update
                        updated_store_transaction_detail = models.Store_Transaction_Detail.objects.filter(store_transaction_header=og_storeTransactionHeader, item_id=int(data.getlist('item_id')[index])).first()
                        updated_store_transaction_detail.quantity = Decimal(data.getlist('item_quantity')[index])
                        updated_store_transaction_detail.amount = Decimal(data.getlist('item_price')[index])
                        updated_store_transaction_detail.amount_with_gst = Decimal(data.getlist('amount_with_gst')[index])
                        updated_store_transaction_detail.store_id = int(data.getlist('store_id')[index])
                        updated_store_transaction_detail.save()

                    for item_id in added_item_list:
                        index = data.getlist('item_id').index(str(item_id))

                        # Creating new store transaction detail
                        new_store_transaction_detail = models.Store_Transaction_Detail()
                        new_store_transaction_detail.store_transaction_header_id = og_storeTransactionHeader.id
                        new_store_transaction_detail.item_id = int(data.getlist('item_id')[index])
                        new_store_transaction_detail.store_id = int(data.getlist('store_id')[index])
                        new_store_transaction_detail.quantity = Decimal(data.getlist('item_quantity')[index])
                        new_store_transaction_detail.rate = Decimal(data.getlist('rate')[index])
                        new_store_transaction_detail.amount = Decimal(data.getlist('item_price')[index])
                        new_store_transaction_detail.gst_percentage = Decimal(data.getlist('gst_percentage')[index])
                        new_store_transaction_detail.amount_with_gst = Decimal(data.getlist('amount_with_gst')[index])

                        new_store_transaction_detail.save()

                        # Store Item Creation/Updation
                        storeItem = models.Store_Item.objects.filter(item_id=int(data.getlist('item_id')[index]), store_id=int(data.getlist('store_id')[index])).first()
                        if storeItem is None:
                            storeItem = models.Store_Item()
                            storeItem.opening_qty = Decimal(data.getlist('item_quantity')[index])
                            storeItem.on_hand_qty = Decimal(data.getlist('item_quantity')[index])
                            storeItem.closing_qty = Decimal(data.getlist('item_quantity')[index])
                            storeItem.item_id = int(data.getlist('item_id')[index])
                            storeItem.store_id = int(data.getlist('store_id')[index])
                            storeItem.save()
                        else:
                            storeItem.on_hand_qty += Decimal(data.getlist('item_quantity')[index])
                            storeItem.closing_qty += Decimal(data.getlist('item_quantity')[index])
                            storeItem.save()

                    for item_id in removed_item_list:
                        og_store_transaction_detail = og_store_transaction_details.filter(item_id=item_id).first()

                        # Update old StoreItem, removal of quantity of old StoreItem
                        old_storeItem = models.Store_Item.objects.filter(item_id=item_id,store_id=og_store_transaction_detail.store_id).first()
                        old_storeItem.on_hand_qty -= og_store_transaction_detail.quantity
                        old_storeItem.on_hand_qty -= og_store_transaction_detail.quantity
                        old_storeItem.save()

                        # Store Transaction Detail Delete
                        removed_store_transaction_detail = models.Store_Transaction_Detail.objects.filter(store_transaction_header=og_storeTransactionHeader, item_id=int(data.getlist('item_id')[index])).first()
                        removed_store_transaction_detail.delete()

        transaction.commit()
        context.update({
            'status': 200,
            'message': "Store Transaction Created Successfully."
        })
    except Exception:
        context.update({
            'status': 588,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def storeTransactionDelete(request):
    context = {}
    storeTransaction = models.Store_Transaction.objects.prefetch_related('store_transaction_detail_set').get(
        pk=request.POST['id'])
    try:
        with transaction.atomic():
            if storeTransaction.purchase_order_header_id is not None:
                purchaseOrderHeader = models.Purchase_Order.objects.prefetch_related('purchase_order_detail_set').get(
                    pk=storeTransaction.purchase_order_header_id)
                for purchaseOrderDetail in purchaseOrderHeader.purchase_order_detail_set.all():
                    storeTransactionDetail = models.Store_Transaction_Detail.objects.filter(store_transaction_header_id=storeTransaction.id, item_id=purchaseOrderDetail.item_id).first()
                    if storeTransactionDetail is not None:
                        purchaseOrderDetail.delivered_quantity -= storeTransactionDetail.quantity
                        purchaseOrderDetail.delivered_amount -= storeTransactionDetail.quantity * purchaseOrderDetail.delivered_rate
                        purchaseOrderDetail.delivered_gst_percentage = purchaseOrderDetail.delivered_gst_percentage
                        purchaseOrderDetail.delivered_amount_with_gst -= (storeTransactionDetail.quantity * purchaseOrderDetail.delivered_rate) + (storeTransactionDetail.quantity * purchaseOrderDetail.delivered_rate * purchaseOrderDetail.delivered_gst_percentage / 100)
                        purchaseOrderDetail.updated_at = datetime.now()
                        purchaseOrderDetail.save()
                for storeTransactionDetail in storeTransaction.store_transaction_detail_set.all():
                    storeItem = models.Store_Item.objects.filter(item_id=storeTransactionDetail.item_id,
                                                                 store_id=storeTransactionDetail.store_id).first()
                    if storeItem is not None:
                        storeItem.on_hand_qty -= Decimal(
                            storeTransactionDetail.quantity)
                        storeItem.closing_qty -= Decimal(
                            storeTransactionDetail.quantity)
                        storeItem.updated_at = datetime.now()
                        storeItem.save()
                purchaseOrderHeader.delivery_status = 1
                purchaseOrderHeader.save()
            storeTransaction.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Store Transaction Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 592,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def storeTransactionDetails(request):
    context = {}
    header_id = request.GET.get('header_id', None)
    if header_id is not None and header_id != "":
        header_detail = list(models.Store_Transaction.objects.filter(id=header_id).values('pk', 'transaction_number', 'transaction_date', 'total_amount',
                             'purchase_order_header_id', 'purchase_order_header__order_number', 'vendor__name', 'transaction_type_id', 'transaction_type__name'))
        orderDetails = list(models.Store_Transaction_Detail.objects.filter(store_transaction_header_id=header_id).values('pk', 'quantity', 'rate', 'amount', 'gst_percentage', 'amount_with_gst',
                            'item_id', 'item__name', 'store_id', 'store__name', 'store_transaction_header_id', 'store_transaction_header__transaction_number', 'store_transaction_header__transaction_date'))
        context.update({
            'status': 200,
            'message': "Store Transaction Details Fetched Successfully.",
            'header_detail': header_detail,
            'page_items': orderDetails,
        })
    else:
        context.update({
            'status': 588,
            'message': "Please Provide Header Id.",
        })
    return JsonResponse(context)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def jobOrderList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id is not None and id != "":
        jobOrder = list(models.Job_Order.objects.filter(pk=id)[:1].values('pk', 'order_number', 'order_date', 'manufacturing_type', 'vendor_id', 'vendor__name', 'with_item', 'notes'))
        context.update({
            'status': 200,
            'message': "Job Order Fetched Successfully.",
            'page_items': jobOrder,
        })
    else:
        jobOrders = models.Job_Order.objects.filter(status=1, deleted=0)
        if keyword is not None and keyword != "":
            jobOrders = jobOrders.filter(order_number__icontains=keyword).filter(status=1, deleted=0)
        jobOrders = list(jobOrders.values('pk', 'order_number', 'order_date', 'manufacturing_type', 'vendor', 'with_item', 'notes'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Job Orders Fetched Successfully.",
                'page_items': jobOrders,
            })
            return JsonResponse(context)

        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(jobOrders, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Job Orders Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'per_page': per_page,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jobOrderAdd(request):
    context = {}
    if not request.POST['order_number'] or not request.POST['order_date'] or not request.POST['manufacturing_type'] or not request.POST['notes']:
        context.update({
            'status': 589,
            'message': "Order Number/Order Date/Manufacturing Type/Notes has not been provided."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            jobOrderHeader = models.Job_Order()
            jobOrderHeader.order_number = request.POST['order_number']
            jobOrderHeader.order_date = request.POST['order_date']
            jobOrderHeader.manufacturing_type = request.POST['manufacturing_type']
            if 'vendor_id' in request.POST:
                jobOrderHeader.vendor_id = request.POST['vendor_id']
            if 'with_item' in request.POST:
                jobOrderHeader.with_item = eval(request.POST['with_item'])
            jobOrderHeader.notes = request.POST['notes']
            jobOrderHeader.save()

            job_order_details = []
            for item_id in request.POST.getlist('item_id'):
                job_order_details.append(
                    models.Job_Order_Detail(
                        job_order_header_id=jobOrderHeader.id,
                        item_id=int(item_id)
                    )
                )
            models.Job_Order_Detail.objects.bulk_create(job_order_details)
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Job Order Created Successfully."
        })
    except Exception:
        context.update({
            'status': 590,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jobOrderEdit(request):
    context = {}
    if not request.POST['order_number'] or not request.POST['order_date'] or not request.POST['manufacturing_type'] or not request.POST['notes']:
        context.update({
            'status': 589,
            'message': "Order Number/Order Date/Manufacturing Type/Notes has not been provided."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            jobOrderHeader = models.Job_Order.objects.prefetch_related('job_order_detail_set').get(pk=request.POST['id'])
            jobOrderHeader.order_number = request.POST['order_number']
            jobOrderHeader.order_date = request.POST['order_date']
            jobOrderHeader.manufacturing_type = request.POST['manufacturing_type']
            if 'vendor_id' in request.POST:
                jobOrderHeader.vendor_id = request.POST['vendor_id']
            if 'with_item' in request.POST:
                jobOrderHeader.with_item = eval(request.POST['with_item'])
            else:
                jobOrderHeader.with_item = False
            jobOrderHeader.notes = request.POST['notes']
            jobOrderHeader.updated_at = now()
            jobOrderHeader.save()
            jobOrderHeader.job_order_detail_set.all().delete()
            job_order_details = []
            for item_id in request.POST.getlist('item_id'):
                job_order_details.append(
                    models.Job_Order_Detail(
                        job_order_header_id=jobOrderHeader.id,
                        item_id=int(item_id)
                    )
                )
            models.Job_Order_Detail.objects.bulk_create(job_order_details)
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Job Order Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 592,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jobOrderDelete(request):
    context = {}
    jobOrder = models.Job_Order.objects.get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            jobOrder.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Job Order Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 593,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def jobOrderDetails(request):
    context = {}
    header_id = request.GET.get('header_id', None)
    if header_id is not None and header_id != "":
        header_detail = list(models.Job_Order.objects.filter(pk=header_id)[:1].values('pk', 'order_number', 'order_date', 'manufacturing_type', 'vendor_id', 'vendor__name', 'with_item', 'notes'))
        orderDetails = list(models.Job_Order_Detail.objects.filter(job_order_header_id=header_id).values('pk', 'job_order_header_id', 'job_order_header__order_number','item_id', 'item__name'))
        context.update({
            'status': 200,
            'message': "Job Order Details Fetched Successfully.",
            'job_order_header_detail': header_detail,
            'job_order_details': orderDetails,
        })
    else:
        context.update({
            'status': 594,
            'message': "Please Provide Header Id.",
        })
    return JsonResponse(context)

#for material issue --- developed by saswata


# @api_view(['GET','POST'])
# @permission_classes([IsAuthenticated])
# def materialIssueDetails(request):
#     context = {}
#     id = request.GET.get('id', None)
#     find_all = request.GET.get('find_all', None)
#     keyword = request.GET.get('keyword', None)
#     job_Order_header_id = request.GET.get('job_Order_id',None)
#     store_id = request.GET.get('store_id',None)
#     header_detail_res = list(models.Job_Order_Detail.objects.filter(job_order_header=job_Order_header_id).values('pk','item_id','item__name','job_order_header__vendor__name','job_order_header__vendor_id'))
#     job_order_head = list(models.Job_Order.objects.filter(pk=job_Order_header_id).values('pk','vendor_id','vendor__name'))
#     context.update({
#         'status': 200,
#         'job_order_head': job_order_head,
#         'page_items': header_detail_res
#
#     })
#
#     return JsonResponse(context)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def getActualQuantity(request):
    context = {}
    item_id = request.GET.get('item_id',None)
    store_id = request.GET.get('store_id',None)
    
    try:
        store_item = models.Store_Item.objects.get(store_id=int(store_id), item_id=int(item_id))
        context.update({
            'status': 200,
            'on_hand_qty_res': store_item.on_hand_qty
        })
    except:
        context.update({
            'status': 200,
            'on_hand_qty_res': '0.00'
        })
    
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def materialIssueDetails(request):
    context = {}
    job_order_id = request.GET.get('job_order_id', None)
    if job_order_id is not None and job_order_id != "" :
        if models.Store_Transaction.objects.filter(job_order_id=job_order_id, transaction_type__name="MIS").exists():
            material_issue = list(
                models.Store_Transaction.objects.filter(job_order_id=job_order_id, transaction_type__name="MIS")[:1].values(
                'id', 'vendor_id',
                'vendor__name',
                'transaction_type_id',
                'transaction_type__name',
                'transaction_number',
                'transaction_date',
                'job_order_id',
                'job_order__order_number'
                )
            )
            material_issue_details = list(
                models.Store_Transaction_Detail.objects.filter(
                    store_transaction_header_id=models.Store_Transaction.objects.get(job_order_id=job_order_id, transaction_type__name="MIS").id
                ).values('pk',
                         'store_transaction_header_id',
                         'store_id',
                         'store__name',
                         'item_id',
                         'item__name',
                         'quantity',
                         ))
        else:
            material_issue=material_issue_details=None

        context.update({
            'status': 200,
            'message': "Material Issue Details Fetched Successfully.",
            'material_issue': material_issue,
            'material_issue_details': material_issue_details,
        })
    else:
        context.update({
            'status': 594,
            'message': "Please Provide an Id.",
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def materialIssueAdd(request):
    context = {}
    if not request.POST['job_order_id'] or not request.POST['issue_date'] or not request.POST['store_id']:
        context.update({
            'status': 594,
            'message': "Job Order/Issue Date/Store has not been provided."
        })
        return JsonResponse(context)

    try:
        with transaction.atomic():
            # transation_type = models.Transaction_Type.objects.get(name = 'MIS')
            store_transaction_count = models.Store_Transaction.objects.all().count()
            storeTransactionHeader=models.Store_Transaction()
            if request.POST['vendor_id']:
                storeTransactionHeader.vendor_id = request.POST['vendor_id']
            storeTransactionHeader.transaction_type = models.Transaction_Type.objects.get(name = 'MIS')
            storeTransactionHeader.transaction_number = env("STORE_TRANSACTION_NUMBER_SEQ").replace(
                    "${CURRENT_YEAR}", datetime.today().strftime('%Y')
                ).replace(
                    "${AI_DIGIT_5}",str(store_transaction_count + 1).zfill(5)
                )
            storeTransactionHeader.transaction_date=request.POST['issue_date']
            storeTransactionHeader.job_order_id = request.POST['job_order_id']
            storeTransactionHeader.save()

            store_transaction_details = []
            store_items_add=[]
            for index, elem in enumerate(request.POST.getlist('item_id')):
                store_transaction_details.append(
                    models.Store_Transaction_Detail(
                        store_transaction_header=storeTransactionHeader,
                        item_id=elem,
                        store_id=request.POST['store_id'],
                        quantity=float(request.POST.getlist('quantity_sent')[index])
                    )
                )

                if request.POST['vendor_id']:
                    vendor_store=models.Store.objects.get(vendor_id=request.POST['vendor_id'])
                    # If the item exists in vendor store
                    if models.Store_Item.objects.filter(store=vendor_store, item_id=elem).exists():
                        store_item=models.Store_Item.objects.get(store=vendor_store, item_id=elem)
                        store_item.on_hand_qty+=Decimal(request.POST.getlist('quantity_sent')[index])
                        store_item.closing_qty+= Decimal(request.POST.getlist('quantity_sent')[index])
                        store_item.updated_at = datetime.now()
                        store_item.save()

                    # If the item does not exist in vendor store so new store item is being created
                    else:
                        store_items_add.append(
                            models.Store_Item(
                                store=vendor_store,
                                item_id=int(elem),
                                opening_qty=float(request.POST.getlist('quantity_sent')[index]),
                                on_hand_qty=float(request.POST.getlist('quantity_sent')[index]),
                                closing_qty=float(request.POST.getlist('quantity_sent')[index]),
                            )
                        )

                # In house store items being reduced
                in_house_store=models.Store.objects.get(id=request.POST['store_id'])
                store_item = models.Store_Item.objects.get(store=in_house_store, item_id=elem)
                store_item.on_hand_qty -= Decimal(request.POST.getlist('quantity_sent')[index])
                store_item.closing_qty -= Decimal(request.POST.getlist('quantity_sent')[index])
                store_item.updated_at = datetime.now()
                store_item.save()

            models.Store_Transaction_Detail.objects.bulk_create(store_transaction_details)
            models.Store_Item.objects.bulk_create(store_items_add)

        transaction.commit()

        context.update({
            'status': 200,
            'message': "Material Issue Created Successfully."
        })

    except Exception:
        context.update({
            'status': 595,
            'message': "Something Went Wrong. Please Try Again."

        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def materialIssueEdit(request):
    context = {}
    if not request.POST['issue_date']:
        context.update({
            'status': 596,
            'message': "Issue Date has not been provided."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            vendor_id = request.POST.get('vendor_id',None)
            item_id = request.POST.getlist('item_id')
            issue_date=request.POST['issue_date']
            store_transaction_id = request.POST['id']

            for index in range(0,len(item_id)):
                if(vendor_id):
                    store_item_vendor_update = models.Store_Item.objects.get(store_id = request.POST['store_id'] , item_id=item_id[index])
                    store_item_vendor_update.on_hand_qty = (float(store_item_vendor_update.on_hand_qty)- float(request.POST.getlist('quantity_sent_og')[0])) +float(request.POST.getlist('quantity_sent')[0])
                    store_item_vendor_update.closing_qty =(float(store_item_vendor_update.closing_qty)- float(request.POST.getlist('quantity_sent_og')[0])) + float(request.POST.getlist('quantity_sent')[0])
                    store_item_vendor_update.updated_at =  datetime.now()
                    store_item_vendor_update.save()

                store_transaction_deat_update = models.Store_Transaction_Detail.objects.get(store_transaction_header_id=store_transaction_id,item_id= item_id[index])
                store_transaction_deat_update.quantity = request.POST.getlist('quantity_sent')[index]
                store_transaction_deat_update.updated_at = datetime.now()
                store_transaction_deat_update.save()

                store_item_update = models.Store_Item.objects.get(store_id = request.POST['store_id'] , item_id=item_id[index])
                store_item_update.on_hand_qty = (float(store_item_update.on_hand_qty)+ float(request.POST.getlist('quantity_sent_og')[0])) - float(request.POST.getlist('quantity_sent')[0])
                store_item_update.closing_qty =(float(store_item_update.closing_qty)+ float(request.POST.getlist('quantity_sent_og')[0])) - float(request.POST.getlist('quantity_sent')[0])
                store_item_update.updated_at =  datetime.now()
                store_item_update.save()

        transaction.commit()
        context.update({
            'status': 200,
            'message': "Material Issue Edited Successfully."
        })

    except Exception:
        context.update({
            'status': 597,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)

#for grn inspection--- developed by saswata

#grnInspection Header List ----developed by saswata
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def grnInspectionHeaderList(request):
    # print("4244")
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    ins_completed = request.GET.get('ins_completed',None)

    try:
        if id is not None and id != "":
            grnInspection = list(models.Grn_Inspection_Transaction.objects.filter(pk=id ,ins_done = 1)[:1].values(
                'pk', 'vendor_id', 'vendor__name', 'transaction_number'))
            context.update({
                'status': 200,
                'message': "grnInspection header Fetched Successfully.",
                'page_items': grnInspection,
            })
        else:
            # print("4244",request.GET)
            if keyword is not None and keyword != "":
                # print("4244",request.GET)
                grnInspection = list(
                    models.Grn_Inspection_Transaction.objects.filter(
                        Q(vendor__name__icontains=keyword) | Q(transaction_number__icontains=keyword) 
                    ).filter(
                        status=1, deleted=0 ,ins_done = 1).values('pk', 'vendor_id', 'vendor__name', 'transaction_number')
                )
            elif ins_completed is not None and ins_completed != "":
                # print("4252",request.GET)
                grnInspection = list(models.Grn_Inspection_Transaction.objects.filter(status=1, deleted=0 ,ins_completed = 0).values(
                    'pk', 'vendor_id', 'vendor__name', 'transaction_number'))
                context.update({
                    'status': 200,
                    'message': "Store Items Fetched Successfully.",
                    'page_items': grnInspection,
                })
                return JsonResponse(context)

            else:
                # print("4263",request.GET)
                grnInspection = list(models.Grn_Inspection_Transaction.objects.filter(status=1, deleted=0 ,ins_done = 1).values(
                    'pk', 'vendor_id', 'vendor__name', 'transaction_number'))
            if find_all is not None and int(find_all) == 1:
                context.update({
                    'status': 200,
                    'message': "Store Items Fetched Successfully.",
                    'page_items': grnInspection,
                })
                return JsonResponse(context)

            per_page = int(env("PER_PAGE_DATA"))
            button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
            current_page = request.GET.get('current_page', 1)

            paginator = CustomPaginator(grnInspection, per_page)
            page_items = paginator.get_page(current_page)
            total_pages = paginator.get_total_pages()

            # print("4282",grnInspection,page_items,total_pages,per_page)
            context.update({
                'status': 200,
                'message': "grn Inspection Fetched Successfully.",
                'page_items': page_items,
                'total_pages': total_pages,
                'per_page': per_page,
                'current_page': int(current_page),
                'button_to_show': int(button_to_show),
            })
       
    except:
        context ={
            'status':597,
            'message':'server error'
        }
    return JsonResponse(context)


#GRN Inspection Transaction Details List ----developed by saswata
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getGrnInspectionTransactionDetail(request):
    # print(request.GET,"saswata")

    try:
        # print("4247")
        # Getting grn inspection transaction details whose inspection is not done
        if int(request.GET.get('ins_done'))==0:
            grn_Ins_Det = list(models.Grn_Inspection_Transaction_Detail.objects.filter(
                    grn_inspection_transaction_header_id = int(request.GET.get('insId')), ins_done = 0
                ).values(
                    'pk',
                    'grn_inspection_transaction_header_id',
                    'grn_inspection_transaction_header__vendor_id',
                    'grn_inspection_transaction_header__vendor__name',
                    'grn_inspection_transaction_header__purchase_order_header_id',
                    'grn_inspection_transaction_header__purchase_order_header__order_number',
                    'item_id',
                    'item__name',
                    'store_id',
                    'store__name',
                    'quantity',
                    'rate',
                    'amount',
                    'gst_percentage'
                ))
        # Getting grn inspection transaction details whose inspection is done
        if int(request.GET.get('ins_done')) == 1:
            grn_Ins_Det = list(models.Grn_Inspection_Transaction_Detail.objects.filter(
                grn_inspection_transaction_header_id=int(request.GET.get('insId')), ins_done=1,
            ).exclude(reject_quantity=0).values(
                'pk',
                'grn_inspection_transaction_header_id',
                'grn_inspection_transaction_header__vendor_id',
                'grn_inspection_transaction_header__vendor__name',
                'grn_inspection_transaction_header__purchase_order_header_id',
                'grn_inspection_transaction_header__purchase_order_header__order_number',
                'item_id',
                'item__name',
                'store_id',
                'store__name',
                'quantity',
                'rate',
                'amount',
                'reject_quantity',
                'quantity',
                'gst_percentage'
            ))
        context ={
            'status':200,
            'page_items': grn_Ins_Det
        }
    except:
        context ={
        'status':598,
        'message':'server error'
        }


    return JsonResponse(context)

#grnInspection add and update  ----developed by saswata

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addGrnDetailisInsTransaction(request):
    context = {}
    ins_completed = 0 if not all(request.POST.getlist('accp_quantity')) else 1 #if ins_completed is 0 means all item is not inspected may be inspection happened paritally
    try:
        if any(request.POST.getlist('accp_quantity')):
            with transaction.atomic():
                grn_ins_head = models.Grn_Inspection_Transaction.objects.get(pk = request.POST['insTraId'])
                grn_ins_head.ins_done = 1
                grn_ins_head.ins_completed = ins_completed
                grn_ins_head.save()
                storeTranscHeadPresent = models.Store_Transaction.objects.filter(grn_inspection_id = request.POST['insTraId']).first()
                if storeTranscHeadPresent is not None:
                    storeTransactionHeader = storeTranscHeadPresent
                    storeTransactionHeader.total_amount = float(storeTransactionHeader.total_amount) + float (request.POST['totalPrice'])
                    storeTransactionHeader.notes=grn_ins_head.notes
                    storeTransactionHeader.save()
                else:
                    store_transaction_count = models.Store_Transaction.objects.all().count()
                    storeTransactionHeader = models.Store_Transaction()
                    storeTransactionHeader.vendor_id = request.POST['vendor_id']
                    storeTransactionHeader.transaction_type_id = 2
                    if (request.POST.get('purchase_order_header_id',None) and request.POST['purchase_order_header_id']!=""):
                        storeTransactionHeader.purchase_order_header_id = request.POST[
                            'purchase_order_header_id']
                    storeTransactionHeader.transaction_number = env("STORE_TRANSACTION_NUMBER_SEQ").replace(
                        "${CURRENT_YEAR}", datetime.today().strftime('%Y')).replace("${AI_DIGIT_5}", str(store_transaction_count + 1).zfill(5))
                    storeTransactionHeader.transaction_date = request.POST['issue_date']
                    storeTransactionHeader.total_amount = request.POST['totalPrice']
                    storeTransactionHeader.grn_inspection_id = request.POST['insTraId']
                    storeTransactionHeader.notes = grn_ins_head.notes
                    storeTransactionHeader.save()
                order_details =[]
                for index in  range(0,len(request.POST.getlist('accp_quantity'))):
                    if request.POST.getlist('accp_quantity')[index] != '':
                        grn_ins_det = models.Grn_Inspection_Transaction_Detail.objects.get(pk =request.POST.getlist('ins_det_id')[index])
                        grn_ins_det.ins_done = 1
                        grn_ins_det.accepted_quantity  = request.POST.getlist('accp_quantity')[index] 
                        grn_ins_det.reject_quantity = request.POST.getlist('rej_quantity')[index] 
                        grn_ins_det.inspection_date = request.POST['issue_date']
                        grn_ins_det.amount = request.POST.getlist('amount')[index]
                        grn_ins_det.amount_with_gst = request.POST.getlist(
                                    'actualPrice')[index]
                        grn_ins_det.updated_at = datetime.now()
                        grn_ins_det.save()

                        order_details.append(
                            models.Store_Transaction_Detail(
                                store_transaction_header_id=storeTransactionHeader.id,
                                item_id=request.POST.getlist('item_id')[index],
                                store_id=request.POST.getlist('store_id')[index],
                                quantity=request.POST.getlist('accp_quantity')[index],
                                rate=request.POST.getlist('rate')[index],
                                amount=request.POST.getlist('amount')[index],
                                gst_percentage=request.POST.getlist('gst_percentage')[index],
                                amount_with_gst=request.POST.getlist('actualPrice')[index]
                                
                            )
                        )
                        storeItem = models.Store_Item.objects.filter(
                            item_id=request.POST.getlist('item_id')[index], store_id=request.POST.getlist('store_id')[index]).first()
                        if storeItem is None:
                            storeItem = models.Store_Item()
                            storeItem.opening_qty = Decimal(request.POST.getlist('accp_quantity')[index])
                            storeItem.on_hand_qty = Decimal(request.POST.getlist('accp_quantity')[index])
                            storeItem.closing_qty = Decimal(request.POST.getlist('accp_quantity')[index])
                            storeItem.item_id = request.POST.getlist('item_id')[index]
                            storeItem.store_id = request.POST.getlist('store_id')[index]
                            storeItem.save()
                        else:
                            storeItem.on_hand_qty += Decimal(request.POST.getlist('accp_quantity')[index])
                            storeItem.closing_qty += Decimal(request.POST.getlist('accp_quantity')[index])
                            storeItem.updated_at = datetime.now()
                            storeItem.save()
                models.Store_Transaction_Detail.objects.bulk_create(order_details)
                if request.POST['purchase_order_header_id'] != "" and (request.POST['purchase_order_header_id']) != 0:
                    for index, elem in enumerate(request.POST.getlist('item_id')):
                        if request.POST.getlist('accp_quantity')[index] != '':
                            purchaseOrderItem = models.Purchase_Order_Detail.objects.get(
                                purchase_order_header_id= request.POST['purchase_order_header_id'] ,item_id = elem)
                            purchaseOrderItem.delivered_quantity += Decimal(request.POST.getlist('accp_quantity')[index])
                            purchaseOrderItem.delivered_rate = Decimal(request.POST.getlist('rate')[index])
                            purchaseOrderItem.delivered_amount += Decimal(request.POST.getlist('amount')[index])
                            purchaseOrderItem.delivered_gst_percentage = Decimal(request.POST.getlist('gst_percentage')[index])
                            purchaseOrderItem.delivered_amount_with_gst += Decimal(request.POST.getlist('actualPrice')[index])
                            purchaseOrderItem.updated_at = datetime.now()
                            purchaseOrderItem.save()
                    purchaseOrderHeader = models.Purchase_Order.objects.prefetch_related(
                        'purchase_order_detail_set').get(pk=request.POST['purchase_order_header_id'])
                    flag = True
                    for purchaseOrderDetail in purchaseOrderHeader.purchase_order_detail_set.all():
                        if Decimal(purchaseOrderDetail.quantity) > Decimal(purchaseOrderDetail.delivered_quantity):
                            flag = False
                            break
                    if flag == True:
                        purchaseOrderHeader.delivery_status = 3
                    else:
                        purchaseOrderHeader.delivery_status = 2
                    purchaseOrderHeader.updated_at = datetime.now()
                    purchaseOrderHeader.save()  
           
            transaction.commit()
            context ={
                'status':200,
                'message':'inspection details updated succesfully and store transaction upadated sucesfully'
            }
    except:
        context ={
            'status':599,
            'message':'server error'
        }
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def materialReturnAdd(request):
    context = {}
    if not request.POST['reason'] or not request.POST['return_date'] :
        context.update({
            'status': 531,
            'message': "Reason or return date has not been provided."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            # Reason = On excess issue of items against a job
            if int(request.POST['reason'])==1:
                store_transaction_count = models.Store_Transaction.objects.all().count()
                material_issue=models.Store_Transaction.objects.get(transaction_type__name="MIS", job_order_id=request.POST['job_order_id'])
                material_return=models.Store_Transaction()
                if material_issue.vendor: material_return.vendor=material_issue.vendor
                material_return.transaction_type=models.Transaction_Type.objects.get(name="MR")
                material_return.transaction_number = env("STORE_TRANSACTION_NUMBER_SEQ").replace(
                        "${CURRENT_YEAR}", datetime.today().strftime('%Y')
                    ).replace(
                        "${AI_DIGIT_5}",str(store_transaction_count + 1).zfill(5)
                    )
                material_return.transaction_date = request.POST['return_date']
                material_return.job_order=material_issue.job_order
                material_return.save()

                in_house_store=models.Store_Transaction_Detail.objects.filter(store_transaction_header=material_issue).first().store
                vendor_store=models.Store.objects.filter(vendor=material_issue.vendor).first()
                store_transaction_details = []

                for (item_id, previous_quantity, updated_quantity) in zip(request.POST.getlist('item_id'),request.POST.getlist('previous_quantity'),request.POST.getlist('updated_quantity')):
                    store_transaction_details.append(
                        models.Store_Transaction_Detail(
                            store_transaction_header=material_return,
                            item_id=item_id,
                            store=in_house_store,
                            quantity=Decimal(updated_quantity)-Decimal(previous_quantity)
                        )
                    )

                    vendor_store_item = models.Store_Item.objects.get(store=vendor_store, item_id=item_id)
                    vendor_store_item.on_hand_qty -= Decimal(previous_quantity)-Decimal(updated_quantity)
                    vendor_store_item.closing_qty -= Decimal(previous_quantity)-Decimal(updated_quantity)
                    vendor_store_item.updated_at = datetime.now()
                    vendor_store_item.save()

                    in_house_store_item = models.Store_Item.objects.get(store=in_house_store, item_id=elem)
                    in_house_store_item.on_hand_qty += Decimal(previous_quantity)-Decimal(updated_quantity)
                    in_house_store_item.closing_qty += Decimal(previous_quantity)-Decimal(updated_quantity)
                    in_house_store_item.updated_at = datetime.now()
                    in_house_store_item.save()

                models.Store_Transaction_Detail.objects.bulk_create(store_transaction_details)

            # Reason = For rejected material during inspection process
            elif int(request.POST['reason'])==2:
                store_transaction_count = models.Store_Transaction.objects.all().count()
                grn_inspection_transaction_header=models.Grn_Inspection_Transaction.objects.get(id=request.POST['grn_inspection_id'])

                material_return = models.Store_Transaction()
                material_return.vendor = grn_inspection_transaction_header.vendor
                if grn_inspection_transaction_header.purchase_order_header: material_return.purchase_order_header = grn_inspection_transaction_header.purchase_order_header
                material_return.transaction_type = models.Transaction_Type.objects.get(name="MR")
                material_return.transaction_number = env("STORE_TRANSACTION_NUMBER_SEQ").replace(
                    "${CURRENT_YEAR}", datetime.today().strftime('%Y')
                ).replace(
                    "${AI_DIGIT_5}", str(store_transaction_count + 1).zfill(5)
                )
                material_return.transaction_date = request.POST['return_date']
                material_return.save()

                store_transaction_details = []
                for i in range(len(request.POST.getlist('item_id'))):
                    if request.POST.getlist('return_item')[i]=="1":
                        store_transaction_details.append(
                            models.Store_Transaction_Detail(
                                store_transaction_header=material_return,
                                item_id=request.POST.getlist('item_id')[i],
                                store_id=request.POST.getlist('store_id')[i],
                                quantity=request.POST.getlist('reject_quantity')[i]
                            )
                        )
                models.Store_Transaction_Detail.objects.bulk_create(store_transaction_details)


        transaction.commit()
        context.update({
            'status': 200,
            'message': "Material Return Created Successfully."
        })
    except Exception:
        context.update({
            'status': 533,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)
