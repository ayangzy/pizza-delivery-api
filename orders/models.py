from django.db import models
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField
# Create your models here.

User=get_user_model()

class Product(models.Model):
     PIZZA_SIZES=(
        ('SMALL','Small'),
        ('MEDIUM','Medium'),
        ('LARGE','Large'),
        ('EXTRA_LARGE','Extra_Large'),
    )
     price = models.DecimalField(max_digits=20, decimal_places=2)
     flavour=models.CharField(max_length=40)
     size = models.CharField(max_length=40, choices=PIZZA_SIZES)
     stock=models.PositiveIntegerField()
     description=models.TextField(null=True, blank=True)
     image=CloudinaryField(null=True, blank=True)
     created_at=models.DateTimeField(auto_now_add=True)
     updated_at=models.DateTimeField(auto_now=True)
     
     def __str__(self):
         return self.flavour
     
     @property
     def image_url(self):
         if not self.image:
             return ""
         return f"https://res.cloudinary.com/logic360/image/upload/v1667735057/{self.image}"
         
     
     
class Transaction(models.Model):
    customer=models.ForeignKey(User,on_delete=models.CASCADE)
    ref=models.CharField(max_length=10)
    status=models.CharField(max_length=10,default='Pending')
    type=models.CharField(max_length=20,null=True,blank=True)
    payment_type=models.CharField(max_length=20)
    currency=models.CharField(max_length=20,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
         return self.ref
    
class DeliveryAddress(models.Model):
        contact_name=models.CharField(max_length=40,null=True,blank=True)
        phone_number=models.CharField(max_length=15)
        address_line_1=models.TextField()
        address_line_2=models.TextField(null=True,blank=True)
        city=models.CharField(max_length=30)
        created_at=models.DateTimeField(auto_now_add=True)
        updated_at=models.DateTimeField(auto_now=True)
    
        def __str__(self):
            return self.contact_name    
class Order(models.Model):
    ORDER_STATUS=(
        ('PENDING', 'Pending'),
        ('IN_TRANSIT', 'In_Transit'),
        ('DELIVERED', 'Delivered')
    )
    customer=models.ForeignKey(User, on_delete=models.CASCADE)
    deliveryaddress=models.ForeignKey(DeliveryAddress,on_delete=models.CASCADE)
    total_amount=models.DecimalField(max_digits=20, decimal_places=2)
    order_status=models.CharField(max_length=40, choices=ORDER_STATUS, default=ORDER_STATUS[0][0])
    transaction=models.ForeignKey(Transaction, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
         return self.order_status
     
    @property
    def order_items(self):
        return self.orderitem_set.all()

    
class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    price=models.DecimalField(max_digits=20, decimal_places=2)
    quantity=models.PositiveIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
         return self.order.order_status
     
    
    
    