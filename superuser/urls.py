"""
URL configuration for vikramSolarBack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'superuser'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('get-ajax-form-type', views.getAjaxFormType, name='getAjaxFormType'),
    
    path('role-list', views.roleList, name='roleList'),
    path('role-add', views.roleAdd, name='roleAdd'),
    path('role-edit/<int:id>', views.roleEdit, name='roleEdit'),

    path('user-list', views.userList, name='userList'),
    path('user-add', views.userAdd, name='userAdd'),
    path('user-edit/<int:id>', views.userEdit, name='userEdit'),

    path('vendor-list', views.vendorList, name='vendorList'),
    path('vendor-add', views.vendorAdd, name='vendorAdd'),
    path('vendor-edit/<int:id>', views.vendorEdit, name='vendorEdit'),

    path('customer-list', views.customerList, name='customerList'),
    path('customer-add', views.customerAdd, name='customerAdd'),
    path('customer-edit/<int:id>', views.customerEdit, name='customerEdit'),

    path('uom-list', views.uomList, name='uomList'),
    path('uom-add', views.uomAdd, name='uomAdd'),
    path('uom-edit/<int:id>', views.uomEdit, name='uomEdit'),

    path('child-uom-list', views.childUomList, name='childUomList'),
    path('child-uom-add', views.childUomAdd, name='childUomAdd'),
    path('child-uom-edit/<int:id>', views.childUomEdit, name='childUomEdit'),

    path('item-category-list', views.itemCategoryList, name='itemCategoryList'),
    path('item-category-add', views.itemCategoryAdd, name='itemCategoryAdd'),
    path('item-category-edit/<int:id>', views.itemCategoryEdit, name='itemCategoryEdit'),

    path('item-type-list', views.itemTypeList, name='itemTypeList'),
    path('item-type-add', views.itemTypeAdd, name='itemTypeAdd'),
    path('item-type-edit/<int:id>', views.itemTypeEdit, name='itemTypeEdit'),

    path('item-color-list', views.itemColorList, name='itemColorList'),
    path('item-color-add', views.itemColorAdd, name='itemColorAdd'),
    path('item-color-edit/<int:id>', views.itemColorEdit, name='itemColorEdit'),

    path('item-list', views.itemList, name='itemList'),
    path('item-add', views.itemAdd, name='itemAdd'),
    path('item-edit/<int:id>', views.itemEdit, name='itemEdit'),
]
