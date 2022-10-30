from rest_framework import serializers
from authentication.models import User
from django.contrib.auth.hashers import make_password
from phonenumber_field.modelfields import PhoneNumberField

class UserCreationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=40)
    email=serializers.CharField(max_length=80)
    phone_number=PhoneNumberField()
    password=serializers.CharField(min_length=8, write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'password']
        
    def validate(self, attrs):
        
        username_exist = User.objects.filter(username=attrs['username']).exists()
        if username_exist:
            raise serializers.ValidationError(detail="The username  has already been taken")
        
        email_exist = User.objects.filter(email=attrs['email']).exists()
        if email_exist:
            raise serializers.ValidationError(detail="The email already exists")
        
        return super().validate(attrs)
    
    def create(self, validated_data):
        
        user = User(**validated_data)
        user.password=make_password(validated_data.get('password'))
        user.save()
        return user