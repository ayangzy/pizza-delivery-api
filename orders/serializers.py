

from rest_framework import serializers
from orders.models import*

from django.contrib.auth import get_user_model

User = get_user_model();
class CustomerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=User
        fields=['first_name', 'last_name', 'username', 'email', 'phone_number']
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields = '__all__'
        

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Transaction
        fields = ['id', 'ref', 'status', 'type', 'payment_type', 'currency']
        
class OrderSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer()
    customer = CustomerSerializer()
    class Meta:
        model=Order
        fields = ['id', 'transaction', 'customer', 'total_amount', 'order_status', 'created_at', 'updated_at']
        
class OrderItemSerializer(serializers.ModelSerializer):
    flavour = serializers.CharField(source='product.flavour', read_only=True)
    class Meta:
        model=OrderItem
        fields = ['id', 'price', 'quantity', 'flavour']
        depth=1
        
class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model=DeliveryAddress
        fields = '__all__'
        
class OrderDetailSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    transaction = TransactionSerializer()
    customer = CustomerSerializer()
    deliveryaddress = DeliverySerializer()
    class Meta:
        model=Order
        fields='__all__'  
        depth=1
        
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    #order_status = serializers.CharField(default='PENDING')
    class Meta:
        model=Order
        fields=['id', 'order_status']