from django.shortcuts import render,redirect
from .models import*
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
import json
from django.db.models import Q

def adminHome(request):
    return render(request, 'admin_base.html')

#Add Category
def add_category(request):
    if request.method == "POST":
        name = request.POST['name']
        Category.objects.create(name=name)
        msg = "Category added"
    return render(request, 'add_category.html', locals())

#View Category
def view_category(request):
    category = Category.objects.all()
    return render(request, 'view_category.html', locals())
#Update Category
def edit_category(request, pid):
    category = Category.objects.get(id=pid)
    if request.method == "POST":
        name = request.POST['name']
        category.name = name
        category.save()
        messages.success(request, "Category Updated")
        return redirect('view_category')
    return render(request, 'edit_category.html', locals())
#Delete Category
def delete_category(request, pid):
    category = Category.objects.get(id=pid)
    category.delete()
    messages.success(request, "Category Deleted")
    return redirect('view_category')



#Add Medicine
def add_medicine(request):
    categories = Category.objects.all()
    if request.method=="POST":
        name = request.POST['name']
        cat = request.POST['category']
        bat_no = request.POST['batch_no']
        qty = request.POST['quantity']
        exp = request.POST['expiry_date']
        price = request.POST['price']
        bar_code = request.POST['barcode']
        catobj = Category.objects.get(id=cat)
        Medicine.objects.create(name=name,category=catobj,batch_no=bat_no,quantity=qty,expiry_date=exp,price=price,barcode=bar_code)
        messages.success(request, "Medicine added")
    return render(request, 'add_medicine.html', locals())

#View Category
def view_medicines(request):
    query = request.GET.get('q', '')  # Get search query from URL parameters
    if query:
        medicines = Medicine.objects.filter(Q(name__icontains=query) | Q(barcode__icontains=query))
    else:
        medicines = Medicine.objects.all()
    return render(request, 'view_medicine.html', locals())