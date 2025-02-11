"""Pharmacy_Management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from pharmacy.views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name="dashboard"),

    # Category URLs
    path('add-category/', add_category, name="add_category"),
    path('view-category/', view_category, name="view_category"),
    path('edit-category/<int:pid>/', edit_category, name="edit_category"),
    path('delete-category/<int:pid>/', delete_category, name="delete_category"),

    # Medicine URLs
    path('add_medicine/', add_medicine, name="add_medicine"),
    path('view_medicine/', view_medicines, name="view_medicine"),
    path('delete-medicine/<int:pid>/', delete_medicine, name="delete_medicine"),
    path('edit-medicine/<int:pid>/', edit_medicine, name="edit_medicine"),

    # Sales & Billing
    path('sales/', sales_billing, name='sales_billing'),
    path('invoice/<int:sale_id>/', generate_invoice, name='generate_invoice'),
    path('email-invoice/<int:sale_id>/', email_invoice, name='email_invoice'),

    # Prescriptions
    path('prescriptions/add/', add_prescription, name='add_prescription'),
    path('prescriptions/view/', view_prescriptions, name='view_prescriptions'),
    path('prescriptions/link/<int:sale_id>/', link_prescription, name='link_prescription'),
    path('prescriptions/search/', search_prescriptions, name='search_prescriptions'),

    # Supplier Management
    path('suppliers/add/', add_supplier, name="add_supplier"),
    path('suppliers/view/', view_suppliers, name="view_suppliers"),
    path('suppliers/edit/<int:supplier_id>/', edit_supplier, name="edit_supplier"),
    path('suppliers/delete/<int:supplier_id>/', delete_supplier, name="delete_supplier"),

    # Purchase Orders
    path('purchases/create/', create_purchase_order, name="create_purchase_order"),
    path('purchases/view/', view_purchase_orders, name="view_purchase_orders"),
    path('purchases/add-item/<int:order_id>/', add_purchase_item, name="add_purchase_item"),

    # Payments
    path('make-payment/<int:supplier_id>/', make_payment, name='make_payment'),


    path('payments/tracking/', view_payment_tracking, name="view_payment_tracking"),  # ✅ Added this line

    #Reports and Analytics
    path('reports/sales/', sales_report, name='sales_report'),
    path('reports/stock/', stock_report, name='stock_report'),
    path('reports/profit-loss/', profit_loss_report, name='profit_loss_report'),
    path("dashboard/", dashboard, name="dashboard"),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

