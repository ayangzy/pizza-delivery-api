from rest_framework import serializers
from orders.models import Product


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.ReadOnlyField()
    class Meta:
        model = Product
        fields = '__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop("image")
        
        return representation
    
    def validate(self, attrs):
        
        return super().validate(attrs)