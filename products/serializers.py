from rest_framework import serializers
from orders.models import Product
from rest_framework.validators import UniqueValidator

class ProductSerializer(serializers.ModelSerializer):
    PIZZA_SIZES=(
        ('SMALL','Small'),
        ('MEDIUM','Medium'),
        ('LARGE','Large'),
        ('EXTRA_LARGE','Extra_Large'),
    )
   
    price = serializers.DecimalField(max_digits=20, decimal_places=2)
    flavour = serializers.CharField(max_length=40)
    size = serializers.ChoiceField(choices=PIZZA_SIZES)
    stock = serializers.IntegerField()
    image_url = serializers.ReadOnlyField()
    class Meta:
        model = Product
        fields = '__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop("image")
        
        return representation
    
    def validate(self, attrs):
        product_exists = Product.objects.filter(flavour=attrs['flavour']).exists()
        if product_exists:
            raise serializers.ValidationError(detail=f"Product with the name {attrs['flavour']} already exists")
        return super().validate(attrs)
    
    
