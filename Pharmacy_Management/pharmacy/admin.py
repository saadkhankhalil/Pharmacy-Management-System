from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Category)
admin.site.register(Medicine)
admin.site.register(Sale)
admin.site.register(SaleItem)
admin.site.register(Prescription)



