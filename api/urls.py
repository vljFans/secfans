from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from . import views

app_name='api'
urlpatterns = [
    path('login', jwt_views.TokenObtainPairView.as_view(), name='login'),
    path('login/refresh', jwt_views.TokenRefreshView.as_view(), name='login_refresh'),

    path('login-user', views.loginUser, name='login_user'),
    path('get-user-details', views.getUserDetails, name='get_user_details'),
    path('logout-user', views.logoutUser, name='logout_user'),

    path('get-content-types', views.getContentTypes, name='getContentTypes'),

    path('get-customer-types', views.getCustomerTypes, name='getCustomerTypes'),
    path('get-kyc-types', views.getKycTypes, name='getKycTypes'),

    path('get-countries', views.getCountries, name='getCountries'),
    path('get-country-states', views.getCountryStates, name='getCountryStates'),
    path('get-state-cities', views.getStateCities, name='getStateCities'),

    path('role-list', views.roleList, name='roleList'),
    path('role-add', views.roleAdd, name='roleAdd'),
    path('role-edit', views.roleEdit, name='roleEdit'),
    path('role-delete', views.roleDelete, name='roleDelete'),

    path('user-list', views.userList, name='userList'),
    path('user-add', views.userAdd, name='userAdd'),
    path('user-edit', views.userEdit, name='userEdit'),
    path('user-delete', views.userDelete, name='userDelete'),

    path('vendor-list', views.vendorList, name='vendorList'),
    path('vendor-add', views.vendorAdd, name='vendorAdd'),
    path('vendor-edit', views.vendorEdit, name='vendorEdit'),
    path('vendor-delete', views.vendorDelete, name='vendorDelete'),

    path('customer-list', views.customerList, name='customerList'),
    path('customer-add', views.customerAdd, name='customerAdd'),
    path('customer-edit', views.customerEdit, name='customerEdit'),
    path('customer-delete', views.customerDelete, name='customerDelete'),

    path('uom-list', views.uomList, name='uomList'),
    path('uom-add', views.uomAdd, name='uomAdd'),
    path('uom-edit', views.uomEdit, name='uomEdit'),
    path('uom-delete', views.uomDelete, name='uomDelete'),

    path('child-uom-list', views.childUomList, name='childUomList'),
    path('child-uom-add', views.childUomAdd, name='childUomAdd'),
    path('child-uom-edit', views.childUomEdit, name='childUomEdit'),
    path('child-uom-delete', views.childUomDelete, name='childUomDelete'),

    path('item-category-list', views.itemCategoryList, name='itemCategoryList'),
    path('item-category-add', views.itemCategoryAdd, name='itemCategoryAdd'),
    path('item-category-edit', views.itemCategoryEdit, name='itemCategoryEdit'),
    path('item-category-delete', views.itemCategoryDelete, name='itemCategoryDelete'),

    path('item-type-list', views.itemTypeList, name='itemTypeList'),
    path('item-type-add', views.itemTypeAdd, name='itemTypeAdd'),
    path('item-type-edit', views.itemTypeEdit, name='itemTypeEdit'),
    path('item-type-delete', views.itemTypeDelete, name='itemTypeDelete'),

    path('item-color-list', views.itemColorList, name='itemColorList'),
    path('item-color-add', views.itemColorAdd, name='itemColorAdd'),
    path('item-color-edit', views.itemColorEdit, name='itemColorEdit'),
    path('item-color-delete', views.itemColorDelete, name='itemColorDelete'),

    path('item-list', views.itemList, name='itemList'),
    path('item-add', views.itemAdd, name='itemAdd'),
    path('item-edit', views.itemEdit, name='itemEdit'),
    path('item-delete', views.itemDelete, name='itemDelete'),
    
    path('component-list', views.componentList, name='componentList'),
    path('component-add', views.componentAdd, name='componentAdd'),
    path('component-edit', views.componentEdit, name='componentEdit'),
    path('component-delete', views.componentDelete, name='componentDelete'),
    
    path('bill-of-material-list', views.billOfMaterialList, name='billOfMaterialList'),
    path('bill-of-material-add', views.billOfMaterialAdd, name='billOfMaterialAdd'),
    path('bill-of-material-edit', views.billOfMaterialEdit, name='billOfMaterialEdit'),
    path('bill-of-material-delete', views.billOfMaterialDelete, name='billOfMaterialDelete'),
]