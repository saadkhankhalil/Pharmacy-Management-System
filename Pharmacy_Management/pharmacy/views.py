import json
import pdfkit
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import redirect

from .models import *


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
    if request.method == "POST":
        name = request.POST['name']
        cat = request.POST['category']
        batch_no = request.POST['batch_no']
        qty = request.POST['quantity']
        exp = request.POST['expiry_date']
        price = request.POST['price']
        barcode = request.POST.get('barcode', '')

        requires_prescription = 'requires_prescription' in request.POST  # Check if checkbox is checked

        catobj = Category.objects.get(id=cat)
        Medicine.objects.create(
            name=name,
            category=catobj,
            batch_no=batch_no,
            quantity=qty,
            expiry_date=exp,
            price=price,
            barcode=barcode,
            requires_prescription=requires_prescription  # Save in DB
        )
        messages.success(request, "Medicine added successfully")
    
    return render(request, 'add_medicine.html', locals())


#View Category
def view_medicines(request):
    query = request.GET.get('q', '')  # Get search query from URL parameters
    if query:
        medicines = Medicine.objects.filter(Q(name__icontains=query) | Q(barcode__icontains=query))
    else:
        medicines = Medicine.objects.all()
    return render(request, 'view_medicine.html', locals())

#Delete Medicine
def delete_medicine(request, pid):
    medicine = Medicine.objects.get(id=pid)
    medicine.delete()
    messages.success(request, "Medicine Deleted")
    return redirect('view_medicine')

#Edit Medicine
def edit_medicine(request, pid):
    medicine = get_object_or_404(Medicine, id=pid)  # Using pid for consistency
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        category_id = request.POST['category']
        batch_no = request.POST['batch_no']
        quantity = request.POST['quantity']
        expiry_date = request.POST['expiry_date']
        barcode = request.POST.get('barcode', '')

        # Update the medicine fields
        catobj = Category.objects.get(id=category_id)
        Medicine.objects.filter(id=pid).update(
            name=name, 
            price=price, 
            category=catobj, 
            batch_no=batch_no, 
            quantity=quantity, 
            expiry_date=expiry_date, 
            barcode=barcode
        )

        messages.success(request, "Medicine Updated Successfully")
        return redirect('view_medicine')  # Redirect to medicine list view

    return render(request, 'edit_medicine.html', locals())

def sales_billing(request):
    medicines = Medicine.objects.all()

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Received Data:", data)  # Debugging

            discount = float(data.get('discount', 0))
            tax = float(data.get('tax', 0))
            payment_method = data.get('payment_method', 'Cash')
            cart_items = data.get('cart', [])

            total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
            discount_amount = (discount / 100) * total_amount
            tax_amount = (tax / 100) * (total_amount - discount_amount)
            final_amount = total_amount - discount_amount + tax_amount

            # Create Sale
            sale = Sale.objects.create(
                total_amount=total_amount,
                discount=discount,
                tax=tax,
                final_amount=final_amount,
                payment_method=payment_method
            )

            # Add items to SaleItem
            for item in cart_items:
                medicine = get_object_or_404(Medicine, id=item['id'])
                SaleItem.objects.create(sale=sale, medicine=medicine, quantity=item['quantity'], price=item['price'])
                medicine.quantity -= item['quantity']  # Reduce stock
                medicine.save()

            print("Sale saved:", sale.id)  # Debugging

            return JsonResponse({'sale_id': sale.id, 'message': 'Sale Processed Successfully'})

        except Exception as e:
            print("Error:", str(e))  # Debugging
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'sales_billing.html', {'medicines': medicines})

def generate_invoice(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    sale_items = SaleItem.objects.filter(sale=sale)

    html_content = render_to_string('invoice_template.html', {'sale': sale, 'sale_items': sale_items})
    pdf = pdfkit.from_string(html_content, False)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{sale.id}.pdf"'
    return response

def email_invoice(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    sale_items = SaleItem.objects.filter(sale=sale)

    html_content = render_to_string('invoice_template.html', {'sale': sale, 'sale_items': sale_items})
    pdf = pdfkit.from_string(html_content, False)

    email = EmailMessage(
        subject=f"Invoice for Sale #{sale.id}",
        body=strip_tags(html_content),
        from_email='yourpharmacy@example.com',
        to=['customer@example.com'],
    )
    email.attach(f'invoice_{sale.id}.pdf', pdf, 'application/pdf')
    email.send()

    return JsonResponse({'message': 'Invoice emailed successfully'})


def add_prescription(request):
    if request.method == "POST":
        patient_name = request.POST['patient_name']
        doctor_name = request.POST['doctor_name']
        notes = request.POST.get('notes', '')
        prescription_file = request.FILES.get('prescription_file', None)

        prescription = Prescription.objects.create(
            patient_name=patient_name,
            doctor_name=doctor_name,
            notes=notes,
            prescription_file=prescription_file
        )

        messages.success(request, "Prescription added successfully")
        return redirect('view_prescriptions')

    return render(request, 'add_prescription.html')

def view_prescriptions(request):
    query = request.GET.get('q', '')
    if query:
        prescriptions = Prescription.objects.filter(patient_name__icontains=query)
    else:
        prescriptions = Prescription.objects.all()

    return render(request, 'view_prescriptions.html', {'prescriptions': prescriptions})

def link_prescription(request, sale_id=None):
    sales = Sale.objects.all()  # Fetch all sales
    prescriptions = Prescription.objects.filter(sale__isnull=True)  # Fetch only unlinked prescriptions

    if request.method == "POST":
        sale_id = request.POST.get('sale_id')
        prescription_id = request.POST.get('prescription_id')

        if not sale_id or not prescription_id:
            messages.error(request, "Both Sale and Prescription must be selected.")
            return redirect('link_prescription')  

        sale = get_object_or_404(Sale, id=sale_id)
        prescription = get_object_or_404(Prescription, id=prescription_id)

        prescription.sale = sale
        prescription.save()

        messages.success(request, "Prescription linked successfully!")
        return redirect('view_prescriptions')

    return render(request, 'link_prescription.html', {'sales': sales, 'prescriptions': prescriptions})



def search_prescriptions(request):
    query = request.GET.get('q', '')

    if query:
        prescriptions = Prescription.objects.filter(
            models.Q(patient_name__icontains=query) |
            models.Q(doctor_name__icontains=query)
        )
    else:
        prescriptions = Prescription.objects.all()

    return render(request, 'search_prescriptions.html', {'prescriptions': prescriptions})


def add_supplier(request):
    if request.method == "POST":
        name = request.POST.get('name')
        contact_person = request.POST.get('contact_person')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')

        Supplier.objects.create(name=name, contact_person=contact_person, phone=phone, email=email, address=address)
        messages.success(request, "Supplier added successfully!")
        return redirect('view_suppliers')

    return render(request, 'add_supplier.html')

def view_suppliers(request):
    suppliers = Supplier.objects.all()
    return render(request, 'view_suppliers.html', {'suppliers': suppliers})


def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == "POST":
        supplier.name = request.POST.get('name')
        supplier.contact_person = request.POST.get('contact_person')
        supplier.phone = request.POST.get('phone')
        supplier.email = request.POST.get('email')
        supplier.address = request.POST.get('address')
        supplier.save()
        messages.success(request, "Supplier updated successfully!")
        return redirect('view_suppliers')

    return render(request, 'edit_supplier.html', {'supplier': supplier})

def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.delete()
    messages.success(request, "Supplier deleted successfully!")
    return redirect('view_suppliers')

def create_purchase_order(request):
    suppliers = Supplier.objects.all()

    if request.method == "POST":
        supplier_id = request.POST.get('supplier_id')
        supplier = get_object_or_404(Supplier, id=supplier_id)

        purchase_order = PurchaseOrder.objects.create(supplier=supplier)
        messages.success(request, "Purchase Order created successfully!")
        return redirect('view_purchase_orders')

    return render(request, 'create_purchase_order.html', {'suppliers': suppliers})

def view_purchase_orders(request):
    orders = PurchaseOrder.objects.all()
    return render(request, 'view_purchase_orders.html', {'orders': orders})

from decimal import Decimal  # Import Decimal at the top

def add_purchase_item(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    medicines = Medicine.objects.all()

    if request.method == "POST":
        medicine_id = request.POST.get('medicine_id')
        quantity = int(request.POST.get('quantity'))

        # Fix: Convert price properly
        price_str = request.POST.get('price', '0').replace(',', '')  
        try:
            price = Decimal(price_str)  # Convert to Decimal instead of float
        except ValueError:
            messages.error(request, "Invalid price format. Please enter a valid number.")
            return redirect('add_purchase_item', order_id=order_id)

        medicine = get_object_or_404(Medicine, id=medicine_id)
        PurchaseItem.objects.create(purchase_order=order, medicine=medicine, quantity=quantity, price=price)
        
        # Fix: Ensure both operands are Decimals
        order.total_amount += quantity * price  # Now both are Decimal
        order.save()

        messages.success(request, "Item added to purchase order!")
        return redirect('view_purchase_orders')

    return render(request, 'add_purchase_item.html', {'order': order, 'medicines': medicines})



def make_payment(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == "POST":
        amount_paid = float(request.POST.get('amount_paid'))
        payment_method = request.POST.get('payment_method')

        SupplierPayment.objects.create(supplier=supplier, amount_paid=amount_paid, payment_method=payment_method)
        messages.success(request, "Payment recorded successfully!")
        return redirect('view_suppliers')

    return render(request, 'make_payment.html', {'supplier': supplier})

def view_payment_tracking(request):
    return render(request, 'view_payment_tracking.html') 
