from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from orders.serializers import *
from orders.models import*
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, IsAuthenticated, AllowAny
from django.conf import settings
import requests
import random
from drf_yasg.utils import swagger_auto_schema
from django.core.mail import send_mail 
from orders.services import OrderService, PaystackService
from rest_framework.pagination import PageNumberPagination
from orders.paginations import CustomPagination

# Create your views here.
User = get_user_model()

class OrderCreate(generics.GenericAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_summary="Add new order")
    def post(self, request):
        
        order = OrderService.create_order(self, request)
       
        response = PaystackService.pay(self, request, order.transaction.ref)
        
        authorization_url=response['data']['authorization_url']
            
        return Response({"status": True, "message": "Order created successfully", "data": {"authorization_url": authorization_url}}, status=status.HTTP_201_CREATED)
    
class VerifyPayment(generics.GenericAPIView):
    
    @swagger_auto_schema(operation_summary="Verify transaction payment")
    def get(self,request):
        
        reference = request.GET.get('reference')
        
        check_pay = Transaction.objects.filter(ref=reference).exists()
        
        if check_pay == False:
            return Response({"status": False, "message": "Invalid payment reference"}, status=status.HTTP_400_BAD_REQUEST)
        
        transaction = Transaction.objects.get(ref=reference)
       
        response = PaystackService.verify_payment(self, request)
      
        if response['data']['status'] == 'success':
                
            Transaction.objects.filter(ref=transaction).update(status=response['data']['status'])
            return Response(response, status=status.HTTP_200_OK)
            
        Transaction.objects.filter(ref=transaction).update(status=response['data']['status'])
        return Response({"status": False, "message": "Verification Failed"}, status=status.HTTP_400_BAD_REQUEST)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAdminUser]
    pagination_class = PageNumberPagination
    
    # @swagger_auto_schema(operation_summary="View all orders")
    # def get(self, request):
    #     orders = Order.objects.all()
    #     serializers = self.serializer_class(instance=orders, many=True)
    #     return Response({"status": True, "message": "Orders retreived successfully", "data": serializers.data})
    
class OrderDetailView(generics.GenericAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAdminUser]
   
    @swagger_auto_schema(operation_summary="View the detail of an order by its ID")
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        serializer = self.serializer_class(instance=order)
        return Response({"status": True, "message": "Order retreived successfully", "data": serializer.data}, status=status.HTTP_200_OK)

class UpdateOrderStatus(generics.GenericAPIView):
    serializer_class = OrderStatusUpdateSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(operation_summary="Update the status of an order")
    def put(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        transaction_status=order.transaction.status
       
        if transaction_status !='success':
            return Response({"status": False, "message": "You cannot update an order status whose transaction is pending"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer=self.serializer_class(instance=order, data=request.data)
       
        
        if serializer.is_valid():
            
            serializer.save()
            
            send_mail(
                'Order status Tracking',
                f'Hi {order.customer.username}, Your order status at this point is: ' + str(serializer.data['order_status'].lower().replace('_', ' ')),
                'felixdecoder2020@gmail.com',
                [order.customer.email]
            )
            
            return Response({"status": True, "message": "Order status updated successfuly", "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST,data=serializer.errors)


class UserOrdersView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(operation_summary="Get all orders made by a specific user")
    def get(self, request, user_id):
        user = User.objects.get(pk=user_id)
        orders = Order.objects.all().filter(customer=user)
        
        serializers = self.serializer_class(instance=orders, many=True)
        
        return Response({"status": True, "message": "Users orders retreived successfully", "data": serializers.data}, status=status.HTTP_200_OK)


class UsersOrderDetailView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(operation_summary="Get the detail of an order made by a specific user")
    def get(self, request, user_id, order_id):
        order = get_object_or_404(Order, pk=order_id)
        
        user=User.objects.get(pk=user_id)
        
        order = Order.objects.all().filter(customer=user).get(pk=order_id)
       
        serializer = self.serializer_class(instance=order)
        
        return Response({"status": True, "message": "User order retreived successfully", "data": serializer.data}, status=status.HTTP_200_OK)

        
    

        
        
        