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
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from pathlib import Path
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
        model__in=['user', 'role', 'role_permission', 'country', 'state', 'city', 'customer_type', 'kyc_type'])
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
    if id != None:
        role = list(models.Role.objects.filter(pk=id)[:1].values('pk', 'name'))
        context.update({
            'status': 200,
            'message': "Role Fetched Successfully.",
            'page_items': role,
        })
    else:
        if keyword != None and keyword != "":
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
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def roleAdd(request):
    context = {}
    exist_data = models.Role.objects.filter(
        name__iexact=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 502,
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
            'status': 503,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def roleEdit(request):
    context = {}
    exist_data = models.Role.objects.filter(
        name__iexact=request.POST['name']).exclude(id=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 504,
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
            'status': 505,
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
            'status': 506,
            'message': "Can not delete as " + str(len(role.user_set.all())) + " user(s) exist with this role."
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            role.role_permission_set.all().delete()
            role.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Role Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 507,
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
    if id != None:
        user = list(models.User.objects.filter(pk=id)[:1].values(
            'pk', 'name', 'email', 'phone', 'role__name'))
        context.update({
            'status': 200,
            'message': "User Fetched Successfully.",
            'page_items': user,
        })
    else:
        if keyword != None and keyword != "":
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
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def userAdd(request):
    context = {}
    if request.POST['password'] != request.POST['confirm_password']:
        context.update({
            'status': 508,
            'message': "Passwords do not match."
        })
        return JsonResponse(context)
    exist_data = models.User.objects.filter(
        Q(email__iexact=request.POST['email']) | Q(phone__iexact=request.POST['phone'])).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 509,
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
            'status': 510,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def userEdit(request):
    context = {}
    if request.POST['password'] != "" or request.POST['confirm_password'] != "":
        if request.POST['password'] != request.POST['confirm_password']:
            context.update({
                'status': 511,
                'message': "Passwords do not match."
            })
            return JsonResponse(context)
    exist_data = models.User.objects.filter(Q(email__iexact=request.POST['email']) | Q(
        phone__iexact=request.POST['phone'])).exclude(id=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 512,
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
            'status': 513,
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
            'status': 514,
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
    if id != None:
        vendor = list(models.Vendor.objects.filter(pk=id)[:1].values('pk', 'name', 'address', 'country__pk', 'state__pk', 'city__pk',
                      'country__name', 'state__name', 'city__name', 'pin', 'gst_no', 'contact_no', 'contact_name', 'contact_email'))
        context.update({
            'status': 200,
            'message': "Vendor Fetched Successfully.",
            'page_items': vendor,
        })
    else:
        if keyword != None and keyword != "":
            vendors = list(
                models.Vendor.objects.filter(
                    Q(name__icontains=keyword) | Q(contact_name__icontains=keyword) | Q(
                        contact_email__icontains=keyword) | Q(contact_no__icontains=keyword)
                ).filter(status=1, deleted=0).values(
                    'pk', 'name', 'address', 'country__pk', 'state__pk', 'city__pk', 'country__name', 'state__name',
                    'city__name', 'pin', 'gst_no', 'contact_no', 'contact_name', 'contact_email'))
        else:
            vendors = list(
                models.Vendor.objects.filter(status=1, deleted=0).values('pk', 'name', 'address', 'country__pk',
                                                                         'state__pk',
                                                                         'city__pk', 'country__name', 'state__name',
                                                                         'city__name', 'pin', 'gst_no', 'contact_no',
                                                                         'contact_name', 'contact_email'))
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
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vendorAdd(request):
    context = {}
    exist_data = models.Vendor.objects.filter(Q(contact_email__iexact=request.POST['contact_email']) | Q(
        contact_no__iexact=request.POST['contact_no'])).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 515,
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
            'status': 516,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vendorEdit(request):
    context = {}
    exist_data = models.Vendor.objects.filter(Q(contact_email__iexact=request.POST['contact_email']) | Q(
        contact_no__iexact=request.POST['contact_no'])).exclude(id=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 517,
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
            'status': 518,
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
            'status': 519,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customerList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id != None:
        customer = list(models.Customer.objects.filter(pk=id)[:1].values('pk', 'name', 'address', 'landmark', 'country__pk', 'state__pk', 'city__pk',
                        'country__name', 'state__name', 'city__name', 'pin', 'contact_no', 'contact_name', 'contact_email', 'customer_type__name', 'photo', 'kyc_image'))
        context.update({
            'status': 200,
            'message': "Customer Fetched Successfully.",
            'page_items': customer,
        })
    else:
        if keyword != None and keyword != "":
            customers = list(
                models.Customer.objects.filter(
                    Q(name__icontains=keyword) | Q(contact_name__icontains=keyword) | Q(email__icontains=keyword) | Q(
                        phone__icontains=keyword) | Q(customer_type__name__icontains=keyword)
                ).filter(status=1, deleted=0).values('pk', 'name', 'address', 'landmark',
                                                     'country__pk', 'state__pk', 'city__pk',
                                                     'country__name', 'state__name', 'city__name',
                                                     'pin', 'contact_no', 'contact_name',
                                                     'contact_email', 'customer_type__name',
                                                     'photo', 'kyc_image'))
        else:
            customers = list(
                models.Customer.objects.filter(status=1, deleted=0).values('pk', 'name', 'address', 'landmark',
                                                                           'country__pk', 'state__pk', 'city__pk',
                                                                           'country__name', 'state__name', 'city__name',
                                                                           'pin', 'contact_no', 'contact_name',
                                                                           'contact_email', 'customer_type__name',
                                                                           'photo', 'kyc_image'))
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
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customerAdd(request):
    context = {}
    exist_data = models.Customer.objects.filter(Q(contact_email__iexact=request.POST['contact_email']) | Q(
        contact_no__iexact=request.POST['contact_no'])).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 520,
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
            customer.weekly_closing_day = ", ".join(
                request.POST.getlist('weekly_closing_day'))
            customer.morning_from_time = request.POST['morning_from_time']
            customer.morning_to_time = request.POST['morning_to_time']
            customer.evening_from_time = request.POST['evening_from_time']
            customer.evening_to_time = request.POST['evening_to_time']
            customer.address = request.POST['address']
            customer.country_id = request.POST['country_id']
            customer.state_id = request.POST['state_id']
            customer.city_id = request.POST['city_id']
            customer.save()

            if 'photo' in request.FILES.keys():
                photo = request.FILES['photo']
                directory_path = settings.MEDIA_ROOT + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/photo/"
                path = Path(directory_path)
                path.mkdir(parents=True, exist_ok=True)
                fs = FileSystemStorage(location=settings.MEDIA_ROOT + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/photo/")
                saved_file = fs.save(photo.name, photo)
                photo_path = settings.MEDIA_URL + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/photo/" + saved_file
                customer.photo = photo_path
                customer.save()
            if 'kyc_image' in request.FILES.keys():
                kyc_image = request.FILES['kyc_image']
                directory_path = settings.MEDIA_ROOT + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/kyc/"
                path = Path(directory_path)
                path.mkdir(parents=True, exist_ok=True)
                fs = FileSystemStorage(location=settings.MEDIA_ROOT + env("CUSTOMER_MEDIA_PROFILE").replace(
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
            'status': 521,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customerEdit(request):
    context = {}
    exist_data = models.Customer.objects.filter(Q(contact_email__iexact=request.POST['contact_email']) | Q(
        contact_no__iexact=request.POST['contact_no'])).exclude(id=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 522,
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
            customer.weekly_closing_day = ", ".join(
                request.POST.getlist('weekly_closing_day'))
            customer.morning_from_time = request.POST['morning_from_time']
            customer.morning_to_time = request.POST['morning_to_time']
            customer.evening_from_time = request.POST['evening_from_time']
            customer.evening_to_time = request.POST['evening_to_time']
            customer.address = request.POST['address']
            customer.country_id = request.POST['country_id']
            customer.state_id = request.POST['state_id']
            customer.city_id = request.POST['city_id']
            customer.save()

            if 'photo' in request.FILES.keys():
                photo = request.FILES['photo']
                directory_path = settings.MEDIA_ROOT + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/photo/"
                path = Path(directory_path)
                path.mkdir(parents=True, exist_ok=True)
                fs = FileSystemStorage(location=settings.MEDIA_ROOT + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/photo/")
                saved_file = fs.save(photo.name, photo)
                photo_path = settings.MEDIA_URL + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/photo/" + saved_file
                customer.photo = photo_path
                customer.save()
            if 'kyc_image' in request.FILES.keys():
                kyc_image = request.FILES['kyc_image']
                directory_path = settings.MEDIA_ROOT + env("CUSTOMER_MEDIA_PROFILE").replace(
                    "${CUSTOMER}", str(customer.pk) + "~~" + customer.name) + "/kyc/"
                path = Path(directory_path)
                path.mkdir(parents=True, exist_ok=True)
                fs = FileSystemStorage(location=settings.MEDIA_ROOT + env("CUSTOMER_MEDIA_PROFILE").replace(
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
            'status': 523,
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
            'status': 524,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def uomList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    keyword = request.GET.get('keyword', None)
    if id != None:
        uom = list(models.Uom.objects.filter(pk=id)[:1].values('pk', 'name'))
        context.update({
            'status': 200,
            'message': "UOM Fetched Successfully.",
            'page_items': uom,
        })
    else:
        if keyword != None and keyword != "":
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
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def uomAdd(request):
    context = {}
    exist_data = models.Uom.objects.filter(
        name=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 525,
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
            'status': 526,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def uomEdit(request):
    context = {}
    exist_data = models.Uom.objects.filter(
        name=request.POST['name']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 527,
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
            'status': 528,
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
            'status': 529,
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
    if id != None:
        childUom = list(models.Child_Uom.objects.filter(pk=id)[:1].values(
            'pk', 'name', 'uom__name', 'conversion_rate'))
        context.update({
            'status': 200,
            'message': "UOM Fetched Successfully.",
            'page_items': childUom,
        })
    else:
        if keyword != None and keyword != "":
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
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def childUomAdd(request):
    context = {}
    exist_data = models.Child_Uom.objects.filter(
        name=request.POST['name'], uom_id=request.POST['uom_id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 530,
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
            'status': 531,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def childUomEdit(request):
    context = {}
    exist_data = models.Child_Uom.objects.filter(
        name=request.POST['name'], uom_id=request.POST['uom_id']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 532,
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
            'status': 533,
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
            'status': 534,
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
    if id != None:
        itemCategory = list(models.Item_Category.objects.get(
            pk=id).values('pk', 'name'))
        context.update({
            'status': 200,
            'message': "Item Category Fetched Successfully.",
            'page_items': itemCategory,
        })
    else:
        if keyword != None and keyword != "":
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
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemCategoryAdd(request):
    context = {}
    exist_data = models.Item_Category.objects.filter(
        name=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 535,
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
            'status': 536,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemCategoryEdit(request):
    context = {}
    exist_data = models.Item_Category.objects.filter(
        name=request.POST['name']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 537,
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
            'status': 538,
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
            'status': 539,
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
    if id != None:
        itemType = list(models.Item_Type.objects.filter(pk=id)[:1].values(
            'pk', 'name', 'item_category__name', 'hsn_code', 'gst_percentage'))
        context.update({
            'status': 200,
            'message': "Item Type Fetched Successfully.",
            'page_items': itemType,
        })
    else:
        if keyword != None and keyword != "":
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
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemTypeAdd(request):
    context = {}
    exist_data = models.Item_Type.objects.filter(
        name=request.POST['name'], item_category_id=request.POST['item_category_id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 540,
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
            'status': 541,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemTypeEdit(request):
    context = {}
    exist_data = models.Item_Type.objects.filter(
        name=request.POST['name'], item_category_id=request.POST['item_category_id']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 542,
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
            'status': 543,
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
            'status': 544,
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
    if id != None:
        itemColor = list(models.Item_Color.objects.get(
            pk=id).values('pk', 'name', 'color_code'))
        context.update({
            'status': 200,
            'message': "Item Color Fetched Successfully.",
            'page_items': itemColor,
        })
    else:
        if keyword != None and keyword != "":
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
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemColorAdd(request):
    context = {}
    exist_data = models.Item_Color.objects.filter(
        name=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 545,
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
            'status': 546,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemColorEdit(request):
    context = {}
    exist_data = models.Item_Color.objects.filter(
        name=request.POST['name']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 547,
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
            'status': 548,
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
            'status': 549,
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
    if id != None:
        item = list(models.Item.objects.filter(pk=id)[:1].values(
            'pk', 'name', 'item_type__name', 'item_type__item_category__name', 'uom__name', 'price'))
        context.update({
            'status': 200,
            'message': "Item Fetched Successfully.",
            'page_items': item,
        })
    else:
        if keyword != None and keyword != "":
            items = list(models.Item.objects.filter(
                Q(name__icontains=keyword) | Q(model_no__icontains=keyword)
            ).filter(status=1, deleted=0).values('pk', 'name', 'item_type__name', 'item_type__item_category__name', 'uom__name', 'price'))
        else:
            items = list(models.Item.objects.filter(status=1, deleted=0).values(
                'pk', 'name', 'item_type__name', 'item_type__item_category__name', 'uom__name', 'price'))
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
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemAdd(request):
    context = {}
    exist_data = models.Item.objects.filter(
        name__iexact=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 550,
            'message': "Item with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            item = models.Item()
            item.name = request.POST['name']
            item.uom_id = request.POST['uom_id']
            item.item_type_id = request.POST['item_type_id']
            item.price = request.POST['price']
            item.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Created Successfully."
        })
    except Exception:
        context.update({
            'status': 551,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def itemEdit(request):
    context = {}
    exist_data = models.Item.objects.filter(name__iexact=request.POST['name']).exclude(
        pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 552,
            'message': "Item with this name and model number already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            item = models.Item.objects.get(pk=request.POST['id'])
            item.name = request.POST['name']
            item.item_type_id = request.POST['item_type_id']
            item.uom_id = request.POST['uom_id']
            item.price = request.POST['price']
            item.save()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Item Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 553,
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
            'status': 554,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def componentList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    if id != None:
        component = list(models.Bill_Of_Material_Header.objects.filter(
            pk=id)[:1].values('pk', 'name', 'uom__name', 'quantity', 'price'))
        context.update({
            'status': 200,
            'message': "Component Fetched Successfully.",
            'page_items': component,
        })
    else:
        components = list(models.Bill_Of_Material_Header.objects.filter(is_component=1).filter(
            status=1, deleted=0).values('pk', 'name', 'uom__name', 'quantity', 'price'))
        if find_all is not None and int(find_all) == 1:
            context.update({
                'status': 200,
                'message': "Components Fetched Successfully.",
                'page_items': components,
            })
            return JsonResponse(context)

        per_page = int(env("PER_PAGE_DATA"))
        button_to_show = int(env("PER_PAGE_PAGINATION_BUTTON"))
        current_page = request.GET.get('current_page', 1)

        paginator = CustomPaginator(components, per_page)
        page_items = paginator.get_page(current_page)
        total_pages = paginator.get_total_pages()

        context.update({
            'status': 200,
            'message': "Components Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def componentAdd(request):
    context = {}
    exist_data = models.Bill_Of_Material_Header.objects.filter(
        name__iexact=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 555,
            'message': "Component with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            componentHeader = models.Bill_Of_Material_Header()
            componentHeader.name = request.POST['name']
            componentHeader.uom_id = request.POST['uom_id']
            componentHeader.quantity = request.POST['quantity']
            componentHeader.price = request.POST['total_amount']
            componentHeader.is_component = 1
            componentHeader.save()

            bill_of_material_details = []
            for index, elem in enumerate(request.POST.getlist('item_id')):
                bill_of_material_details.append(models.Bill_Of_Material_Detail(bill_of_material_header_id=componentHeader.id,
                                                item_id=elem, quantity=request.POST.getlist('item_quantity')[index], price=request.POST.getlist('item_price')[index]))
            models.Bill_Of_Material_Detail.objects.bulk_create(
                bill_of_material_details)
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Component Created Successfully."
        })
    except Exception:
        context.update({
            'status': 556,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def componentEdit(request):
    context = {}
    exist_data = models.Bill_Of_Material_Header.objects.filter(
        name__iexact=request.POST['name']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 557,
            'message': "Component with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            componentHeader = models.Bill_Of_Material_Header.objects.prefetch_related(
                'bill_of_material_detail_set').get(pk=request.POST['id'])
            componentHeader.name = request.POST['name']
            componentHeader.uom_id = request.POST['uom_id']
            componentHeader.quantity = request.POST['quantity']
            componentHeader.price = request.POST['total_amount']
            componentHeader.save()
            componentHeader.bill_of_material_detail_set.all().delete()
            bill_of_material_details = []
            for index, elem in enumerate(request.POST.getlist('item_id')):
                bill_of_material_details.append(models.Bill_Of_Material_Detail(bill_of_material_header_id=componentHeader.id,
                                                item_id=elem, quantity=request.POST.getlist('item_quantity')[index], price=request.POST.getlist('item_price')[index]))
            models.Bill_Of_Material_Detail.objects.bulk_create(
                bill_of_material_details)
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Component Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 558,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def componentDelete(request):
    context = {}
    component = models.Bill_Of_Material_Header.objects.prefetch_related('bill_of_material_detail_set').get(pk=request.POST['id'])
    try:
        with transaction.atomic():
            component.bill_of_material_detail_set.all().delete()
            component.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Component Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 559,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billOfMaterialList(request):
    context = {}
    id = request.GET.get('id', None)
    find_all = request.GET.get('find_all', None)
    if id != None:
        billOfMaterial = list(models.Bill_Of_Material_Header.objects.filter(
            pk=id)[:1].values('pk', 'name', 'uom__name', 'quantity', 'price'))
        context.update({
            'status': 200,
            'message': "Bill Of Material Fetched Successfully.",
            'page_items': billOfMaterial,
        })
    else:
        billOfMaterials = list(models.Bill_Of_Material_Header.objects.exclude(is_component=1).filter(
            status=1, deleted=0).values('pk', 'name', 'uom__name', 'quantity', 'price'))
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
            'message': "Components Fetched Successfully.",
            'page_items': page_items,
            'total_pages': total_pages,
            'current_page': int(current_page),
            'button_to_show': int(button_to_show),
        })
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def billOfMaterialAdd(request):
    context = {}
    exist_data = models.Bill_Of_Material_Header.objects.exclude(is_component=1).filter(name__iexact=request.POST['name']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 560,
            'message': "Bill Of Material with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            billOfMaterialHeader = models.Bill_Of_Material_Header()
            billOfMaterialHeader.name = request.POST['name']
            billOfMaterialHeader.uom_id = request.POST['uom_id']
            billOfMaterialHeader.quantity = request.POST['quantity']
            billOfMaterialHeader.price = request.POST['total_amount']
            billOfMaterialHeader.is_component = 0
            billOfMaterialHeader.save()

            bill_of_material_details = []
            for index, elem in enumerate(request.POST.getlist('item_id')):
                bill_of_material_details.append(models.Bill_Of_Material_Detail(bill_of_material_header_id=billOfMaterialHeader.id,
                                                item_id=elem, quantity=request.POST.getlist('item_quantity')[index], price=request.POST.getlist('item_price')[index]))
            for index, elem in enumerate(request.POST.getlist('component_id')):
                bill_of_material_details.append(models.Bill_Of_Material_Detail(bill_of_material_header_id=billOfMaterialHeader.id,
                                                component_id=elem, quantity=request.POST.getlist('component_quantity')[index], price=request.POST.getlist('component_price')[index]))
            models.Bill_Of_Material_Detail.objects.bulk_create(
                bill_of_material_details)
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Bill Of Material Created Successfully."
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
def billOfMaterialEdit(request):
    context = {}
    exist_data = models.Bill_Of_Material_Header.objects.filter(
        name__iexact=request.POST['name']).exclude(pk=request.POST['id']).filter(deleted=0)
    if len(exist_data) > 0:
        context.update({
            'status': 562,
            'message': "Bill Of Material with this name already exists.",
        })
        return JsonResponse(context)
    try:
        with transaction.atomic():
            billOfMaterialHeader = models.Bill_Of_Material_Header.objects.prefetch_related('bill_of_material_detail_set').get(pk=request.POST['id'])
            billOfMaterialHeader.name = request.POST['name']
            billOfMaterialHeader.uom_id = request.POST['uom_id']
            billOfMaterialHeader.quantity = request.POST['quantity']
            billOfMaterialHeader.price = request.POST['total_amount']
            billOfMaterialHeader.is_component = 0
            billOfMaterialHeader.save()
            billOfMaterialHeader.bill_of_material_detail_set.all().delete()
            bill_of_material_details = []
            for index, elem in enumerate(request.POST.getlist('item_id')):
                bill_of_material_details.append(models.Bill_Of_Material_Detail(bill_of_material_header_id=billOfMaterialHeader.id,
                                                item_id=elem, quantity=request.POST.getlist('item_quantity')[index], price=request.POST.getlist('item_price')[index]))
            for index, elem in enumerate(request.POST.getlist('component_id')):
                bill_of_material_details.append(models.Bill_Of_Material_Detail(bill_of_material_header_id=billOfMaterialHeader.id,
                                                component_id=elem, quantity=request.POST.getlist('component_quantity')[index], price=request.POST.getlist('component_price')[index]))
            models.Bill_Of_Material_Detail.objects.bulk_create(
                bill_of_material_details)
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Bill Of Material Updated Successfully."
        })
    except Exception:
        context.update({
            'status': 563,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def billOfMaterialDelete(request):
    context = {}
    component = models.Bill_Of_Material_Header.objects.get(
        pk=request.POST['id'])
    try:
        with transaction.atomic():
            component.delete()
        transaction.commit()
        context.update({
            'status': 200,
            'message': "Bill Of Material Deleted Successfully."
        })
    except Exception:
        context.update({
            'status': 564,
            'message': "Something Went Wrong. Please Try Again."
        })
        transaction.rollback()
    return JsonResponse(context)
