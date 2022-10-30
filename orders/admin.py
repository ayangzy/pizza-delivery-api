from django.contrib import admin
from orders.models import *

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ['flavour', 'price', 'size']
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'total_amount', 'order_status', 'transaction_id']
    
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ['cartorder', 'product', 'price', 'quantity']
    
class TransactionAdmin(admin.ModelAdmin):
    list_display=['customer', 'ref', 'status', 'type', 'payment_type', 'currency']
    
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ['contact_name', 'phone_number', 'address_line_1', 'address_line_2', 'city']
    
admin.site.register(Product, ProductAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemsAdmin)
admin.site.register(DeliveryAddress, DeliveryAddressAdmin)

