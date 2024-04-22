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
    path('vendor-export', views.vendorExport, name='vendorExport'),

    path('customer-list', views.customerList, name='customerList'),
    path('customer-add', views.customerAdd, name='customerAdd'),
    path('customer-edit', views.customerEdit, name='customerEdit'),
    path('customer-delete', views.customerDelete, name='customerDelete'),
    path('customer-export', views.customerExport, name='customerExport'),

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
    path('item-export', views.itemExport, name='itemExport'),

    path('store-list', views.storeList, name='storeList'),
    path('store-add', views.storeAdd, name='storeAdd'),
    path('store-edit', views.storeEdit, name='storeEdit'),
    path('store-delete', views.storeDelete, name='storeDelete'),
    path('store-export', views.storeExport, name='storeExport'),
    
    path('bill-of-material-list', views.billOfMaterialList, name='billOfMaterialList'),
    path('bill-of-material-add', views.billOfMaterialAdd, name='billOfMaterialAdd'),
    path('bill-of-material-edit', views.billOfMaterialEdit, name='billOfMaterialEdit'),
    path('bill-of-material-delete', views.billOfMaterialDelete, name='billOfMaterialDelete'),
    path('bill-of-material-structure', views.getBillOfMaterialStructure, name='getBillOfMaterialStructure'),
    
    path('purchase-order-list', views.purchaseOrderList, name='purchaseOrderList'),
    path('purchase-order-add', views.purchaseOrderAdd, name='purchaseOrderAdd'),
    path('purchase-order-edit', views.purchaseOrderEdit, name='purchaseOrderEdit'),
    path('purchase-order-delete', views.purchaseOrderDelete, name='purchaseOrderDelete'),
    path('purchase-order-details', views.purchaseOrderDetails, name='purchaseOrderDetails'),

    path('transaction-type-list', views.transactionTypeList, name='transactionTypeList'),
    path('transaction-type-add', views.transactionTypeAdd, name='transactionTypeAdd'),
    path('transaction-type-edit', views.transactionTypeEdit, name='transactionTypeEdit'),
    path('transaction-type-delete', views.transactionTypeDelete, name='transactionTypeDelete'),

    path('store-item-list', views.storeItemList, name='storeItemList'),
    path('store-item-add', views.storeItemAdd, name='storeItemAdd'),
    path('store-item-edit', views.storeItemEdit, name='storeItemEdit'),
    path('store-item-delete', views.storeItemDelete, name='storeItemDelete'),
    path('store-item-export', views.storeItemExport, name='storeItemExport'),
    # path('store-item-report-export', views.storeItemReportExport, name='storeItemReportExport'),


    path('store-transaction-list', views.storeTransactionList, name='storeTransactionList'),
    path('store-transaction-add', views.storeTransactionAdd, name='storeTransactionAdd'),
    path('store-transaction-edit', views.storeTransactionEdit, name='storeTransactionEdit'),
    path('store-transaction-delete', views.storeTransactionDelete, name='storeTransactionDelete'),
    path('store-transaction-details', views.storeTransactionDetails, name='storeTransactionDetails'),

    path('job-order-list', views.jobOrderList, name='jobOrderList'),
    path('job-order-add', views.jobOrderAdd, name='jobOrderAdd'),
    path('job-order-edit', views.jobOrderEdit, name='jobOrderEdit'),
    path('job-order-delete', views.jobOrderDelete, name='jobOrderDelete'),
    path('job-order-details', views.jobOrderDetails, name='jobOrderDetails'),

    # path('material-issue-details', views.materialIssueDetails, name='materialIssueDetails'),
    path('get-actual-quantity', views.getActualQuantity, name='getActualQuantity'),
    path('material-issue-add', views.materialIssueAdd, name='materialIssueAdd'),
    path('material-issue-edit', views.materialIssueEdit, name='materialIssueEdit'),
    path('material-issue-details', views.materialIssueDetails, name='materialIssueDetails'),

    # path grn inspection ---developed by saswata
    path('grn-inspection-details-transaction', views.getGrnInspectionTransactionDetail, name='getGrnInspectionTransactionDetail'),
    path('grn-inspection-list-Add', views.addGrnDetailisInsTransaction, name='addGrnDetailisInsTransaction'),
    path('grn-inspection-head-list', views.grnInspectionHeaderList, name='grnInspectionHeaderList'), 

    path('material-return-add', views.materialReturnAdd, name='materialReturnAdd'),

    # path on transit transaction ---developed by saswata

    path('on-transit-transaction-list', views.getOnTransitTransactionHeadersList, name='getOnTransitTransactionHeadersList'),
    path('on-transit-transaction-all-list', views.getOnTransitTransactionDetalisList, name='getOnTransitTransactionDetalisList'),
    # path('store-transfer-report-export', views.storeTransferReportExport, name='storeTransferReportExport'),
    
    # material out
    path('material-out-details-add', views.materialOutDetailsAdd, name='materialOutDetailsAdd'),
    path('material-out-details-delete', views.materialOutDetailsDelete, name='materialOutDetailsDelete'),
    path('material-out-details-edit', views.materialOutDetailsEdit, name='materialOutDetailsEdit'),
    # path('', views.grnInspectionHeaderList, name='grnInspectionHeaderList'), reportStockTransfer

    # material in
    path('material-in-details-add', views.materialInDetailsAdd, name='materialInDetailsAdd'),
    # path('grn-inspection-list-Add', views.addGrnDetailisInsTransaction, name='addGrnDetailisInsTransaction'),
    # path('grn-inspection-head-list', views.grnInspectionHeaderList, name='grnInspectionHeaderList'),

    # physical Inspection on Store Items --- developed by saswata
    path('physical-inspection-header-list', views.getPhysicalInspectionHeadersList, name='getPhysicalInspectionHeadersList'),
    path('physical-inspection-details-add', views.physicalInspectionDetailsAdd, name='physicalInspectionDetailsAdd'),

    # purchase bill url --- developed by saswata
    path('purchase-bill-header-list', views.getPurchaseBillHeadersList, name='getPurchaseBillHeadersList'),
    path('purchase-bill-details-add', views.purchaseBillDetailsAdd, name='purchaseBillDetailsAdd'),
    path('purchase-bill-details-edit', views.purchaseBillDetailsEdit, name='purchaseBillDetailsEdit'),
    path('purchase-bill-details-delete', views.purchaseBillDetailsDelete, name='purchaseBillDetailsDelete'),

    path('item-tracking-report', views.reportItemTrackingReport, name='reportItemTrackingReport'),
    path('report-inventory-summary', views.reportInventorySummary, name='reportInventorySummary'),
    path('report-inventory-storewise', views.reportInventoryStorewise, name='reportInventoryStorewise'),
    path('report-stock-transfer', views.reportStockTransfer, name='reportStockTransfer'),
    path('report-purchase-order-by-vendor', views.reportPurchaseOrderByVendor, name='reportPurchaseOrderByVendor'),
    path('report-purchase-order-by-item', views.reportPurchaseOrderByItem, name='reportPurchaseOrderByItem'),
    path('report-active-purchase-order', views.reportActivePurchaseOrder, name='reportActivePurchaseOrder'),
]