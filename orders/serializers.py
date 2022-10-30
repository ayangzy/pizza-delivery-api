
from dataclasses import fields
from itertools import product
from pyexpat import model
from rest_framework import serializers
from orders.models import*

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields = '__all__'
        

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Transaction
        fields = '__all__'
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields = '__all__'
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    cartorder = OrderSerializer()
    class Meta:
        model=OrderItem
        fields = '__all__'
        

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model=DeliveryAddress
        fields = '__all__'
        
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    #order_status = serializers.CharField(default='PENDING')
    class Meta:
        model=Order
        fields=['id', 'order_status']