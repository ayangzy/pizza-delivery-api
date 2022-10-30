from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from orders.serializers import *
from orders.models import*
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from django.conf import settings
import requests
import random
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
User = get_user_model()

class OrderCreateList(generics.GenericAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(operation_summary="View all orders")
    def get(self, request):
        orders = Order.objects.all()
        serializers = self.serializer_class(instance=orders, many=True)
        return Response({"status": True, "message": "Order retreived successfully", "data": serializers.data})
    
    @swagger_auto_schema(operation_summary="Add new order")
    def post(self, request):
        request_data = request.data
        items = request_data.pop('item')
        
        #Create an order for the customer
        cart_order = Order.objects.create(
               customer=request.user,
               total_amount=request_data['total_amount']
           )
        
        #create a delivery address
        DeliveryAddress.objects.create(
            cartorder=cart_order,
            phone_number=request_data['phone_number'],
            address_line_1=request_data['address_line_1'],
            address_line_2=request_data['address_line_2'],
            city=request_data['city'],
           )

        #Loop through the list of order items and save in db
        for item in items:
            product = Product.objects.get(id=item['product_id'])
            order_items = OrderItem.objects.create(
               cartorder=cart_order,
               product=product,
               quantity=request_data['quantity'],
               price=product.price
           )
            
        url = 'https://api.paystack.co/transaction/initialize'
        
        transaction_ref = random.randint(10**12, 10**13 - 1)
       
        headers = {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        
        r = requests.post(url, headers=headers, data={"amount": request_data['total_amount'] *100, "email": request.user.email, "reference": "PIZ" + str(transaction_ref)})
        response = r.json()
        if response['status'] == False:
            return Response(response)
        
        authorization_url=response['data']['authorization_url']
            
        Transaction.objects.create(
            customer=request.user,
            ref="PIZ" + str(transaction_ref),
            type='pizza-payment',
            payment_type='paystack',
            currency='NGN'
        )
        return Response({"status": True, "message": "Order created successfully", "data": {"authorization_url": authorization_url}}, status=status.HTTP_201_CREATED)
    
class VerifyPayment(generics.GenericAPIView):
    
    @swagger_auto_schema(operation_summary="Verify transaction payment")
    def get(self,request,reference):
        try:
            transaction = Transaction.objects.get(ref=reference)
            
            url = 'https://api.paystack.co/transaction/verify/{}'.format(transaction)
            
            headers = {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            r = requests.get(url, headers=headers)
            
            response = r.json()
        
            if response['data']['status'] == 'success':
                
                Transaction.objects.filter(ref=reference).update(status=response['data']['status'])
                return Response(response, status=status.HTTP_200_OK)
            
            Transaction.objects.filter(ref=reference).update(status=response['data']['status'])
            return Response({"status": False, "message": "Verification Failed"}, status=status.HTTP_400_BAD_REQUEST)
        
        except ObjectDoesNotExist:
            return Response({"status":False, "message": "Invalid transaction reference"}, status=status.HTTP_400_BAD_REQUEST)

class OrderDetailView(generics.GenericAPIView):
    serializer_class = OrderSerializer
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
        serializer=self.serializer_class(instance=order, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Order status updated successfuly", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST,data=serializer.errors)


class UserOrdersView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(operation_summary="Get all orders made by a specific user")
    def get(self, request, user_id):
        user = User.objects.get(pk=user_id)
        orders = Order.objects.all().filter(customer=user)
        
        serializers = self.serializer_class(instance=orders, many=True)
        
        return Response({"status": True, "message": "Users orders retreived successfully", "data": serializers.data}, status=status.HTTP_200_OK)


class UsersOrderDetailView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(operation_summary="Get the detail of an order made by a specific user")
    def get(self, request, user_id, order_id):
        
        user=User.objects.get(pk=user_id)
        order = Order.objects.all().filter(customer=user).get(pk=order_id)
        
        serializer = self.serializer_class(instance=order)
        
        return Response({"status": True, "message": "User order retreived successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        
    

        
        
        