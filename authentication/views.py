from rest_framework import generics, status
from rest_framework.response import Response
from authentication.models import User, PasswordReset
from authentication.serializers import *
from drf_yasg.utils import swagger_auto_schema
import random
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

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
    
    
class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    
    @swagger_auto_schema(operation_summary="Forgot password")
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
        
@api_view(['PUT'])
def reset_password(request):
    request_data = request.data
    email = request_data['email']
    try:
        user = User.objects.get(email=email)
        userToken = PasswordReset.objects.get(email=user.email)
        
        if not request_data['token'] == userToken.token:
             return Response({"status": False, "message": "Invalid password reset token"}, status=status.HTTP_400_BAD_REQUEST)
         
        if request_data['new_password']  == '':
            return Response({"status": False, "message": "Password field cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        if request_data['new_confirm_password'] == '':
              return Response({"status": False, "message": "The new password field cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)
          
        if request_data['new_password'] !=request_data['new_confirm_password']:
           return Response({"status": False, "message": "Password does not match"}, status=status.HTTP_400_BAD_REQUEST)
       
        user.set_password(request_data['new_password'])
        user.save()
        userToken.delete()
        return Response({"status": True, "message": "password reset successully"}, status=status.HTTP_200_OK)
    
    except PasswordReset.DoesNotExist:
       return Response({"status": False, "message": "Invalid Password reset token"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    request_data = request.data
    user = User.objects.get(username=request.user)
    if request_data['old_password'] == '':
        return Response({"status": False, "message": "The old password field cannot be blank"}, status=status.HTTP_400_BAD_REQUEST)
    
    if request_data['new_password'] == '':
        return Response({"status": False, "message": "The old password field cannot be blank"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.check_password(request_data['old_password']):
        return Response({"status": False, "message": "Password does not match"}, status=status.HTTP_400_BAD_REQUEST)
    
    if user.check_password(request_data['new_password']):
         return Response({"status": False, "message": "You have used this password before, kindly use a different password"}, status=status.HTTP_400_BAD_REQUEST)
     
    user.set_password(request_data['new_password'])
    user.save()
    return Response({"status": True, "message": "Password updated succesfully"}, status=status.HTTP_200_OK)
    
    
    
   

       
    
       
        
   
       
        
        
       
        
