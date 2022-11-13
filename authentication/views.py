from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from authentication.models import User, PasswordReset
from authentication.serializers import UserCreationSerializer, PasswordResetSerializer
from drf_yasg.utils import swagger_auto_schema
import random
from django.core.mail import send_mail
from django.template.loader import render_to_string

class UserCreateView(generics.GenericAPIView):
    serializer_class = UserCreationSerializer
    
    @swagger_auto_schema(operation_summary="Create a useer account")
    def post(self, request):
        data=request.data
        serializer=self.serializer_class(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class PasswordReset(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    queryset = PasswordReset.objects.all()
    
    def post(self, request):
        request_data = request.data
        token = random.randint(1000,9999)
        request_data['token'] = token
        try:
            user = User.objects.get(email=request_data['email'])
            
            template = render_to_string('password_reset.html', {'user': user, 'token': token})
            
            send_mail(
            'Password Reset',
            None,
            'felixdecoder2020@gmail.com',
            [request_data['email']],
            fail_silently=False,
            html_message=template
            )
            serializer = self.serializer_class(data=request_data)
            if serializer.is_valid():
                serializer.save()
            return Response({"status": True, "message": "A password reset token has been sent to your email"}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({"status": False, "message": f"User with the email {request_data['email']} not found"}, status=status.HTTP_404_NOT_FOUND)
       
        
        
       
        
