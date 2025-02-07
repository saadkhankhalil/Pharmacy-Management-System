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
    path('', adminHome, name="adminhome"),
    path('add-category/', add_category, name="add_category"),
    path('view-category/', view_category, name="view_category"),
    path('edit-category/<int:pid>/', edit_category, name="edit_category"),
    path('delete-category/<int:pid>/', delete_category, name="delete_category"),
    path('add_medicine/', add_medicine, name="add_medicine"),
    path('view_medicine/', view_medicines, name="view_medicine"),
    path('delete-medicine/<int:pid>/', delete_medicine, name="delete_medicine"),
    path('edit-medicine/<int:pid>/', edit_medicine, name="edit_medicine"),
    path('sales/', sales_billing, name='sales_billing'),
    path('invoice/<int:sale_id>/', generate_invoice, name='generate_invoice'),
    path('email-invoice/<int:sale_id>/', email_invoice, name='email_invoice'),
    path('upload-prescription/', upload_prescription, name='upload_prescription'),
    path('prescriptions/', prescription_list, name='prescription_list'),
    path('link-prescription/<int:prescription_id>/', link_prescription_to_sale, name='link_prescription_to_sale'),

]
