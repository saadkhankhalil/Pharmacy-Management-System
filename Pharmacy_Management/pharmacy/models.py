from django.db import models
from datetime import datetime

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)  # Field to track the creation time

    def __str__(self):
        return self.name
    
class Medicine(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    batch_no = models.CharField(max_length=50, )
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    barcode = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.batch_no}"
    


class Sale(models.Model):
    date = models.DateTimeField(default=datetime.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[('Cash', 'Cash'), ('Card', 'Card'), ('Digital Wallet', 'Digital Wallet')])

    def __str__(self):
        return f"Sale {self.id} - {self.date}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    medicine = models.ForeignKey('Medicine', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.medicine.name} - {self.quantity} pcs"
    
class Prescription(models.Model):
    patient_name = models.CharField(max_length=200)
    doctor_name = models.CharField(max_length=200)
    prescription_date = models.DateField(auto_now_add=True)
    prescription_file = models.FileField(upload_to='prescriptions/', null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Prescription for {self.patient_name} ({self.prescription_date})"
    
class Sales(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True)
    medicine_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale of {self.medicine_name} on {self.sale_date}"
    


    

