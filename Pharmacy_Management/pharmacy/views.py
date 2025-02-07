import json
import pdfkit
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from .models import Medicine, Sale, SaleItem

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



# Upload Prescription
def upload_prescription(request):
    if request.method == "POST":
        patient_name = request.POST['patient_name']
        doctor_name = request.POST['doctor_name']
        notes = request.POST.get('notes', '')

        prescription_file = request.FILES.get('prescription_file')

        prescription = Prescription(
            patient_name=patient_name,
            doctor_name=doctor_name,
            notes=notes,
            prescription_file=prescription_file
        )
        prescription.save()
        messages.success(request, "Prescription uploaded successfully.")
        return redirect('prescription_list')

    return render(request, 'upload_prescription.html')

# View Prescription History
def prescription_list(request):
    prescriptions = Prescription.objects.all().order_by('-prescription_date')
    return render(request, 'prescription_list.html', {'prescriptions': prescriptions})

# Link Prescription to Sale
def link_prescription_to_sale(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    if request.method == "POST":
        medicine_name = request.POST['medicine_name']
        quantity = int(request.POST['quantity'])
        total_price = float(request.POST['total_price'])

        sale = Sale(prescription=prescription, medicine_name=medicine_name, quantity=quantity, total_price=total_price)
        sale.save()
        messages.success(request, "Sale linked to prescription successfully.")
        return redirect('prescription_list')

    return render(request, 'link_prescription.html', {'prescription': prescription})
