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

# Create your views here.
User = get_user_model()

class OrderCreate(generics.GenericAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_summary="Add new order")
    def post(self, request):
        request_data = request.data
        items = request_data.pop('item')
        
        transaction_ref = random.randint(10**12, 10**13 - 1)
       
       #Create a transaction and generate transaction ref
        transaction = Transaction.objects.create(
            customer=request.user,
            ref="PIZ" + str(transaction_ref),
            type='pizza-payment',
            payment_type='paystack',
            currency='NGN'
        )
        
         #create a delivery address for the order
        delivery_address = DeliveryAddress.objects.create(
            phone_number=request_data['phone_number'],
            address_line_1=request_data['address_line_1'],
            address_line_2=request_data['address_line_2'],
            contact_name=request_data['contact_name'],
            city=request_data['city'],
           )
        
        #Create an order for the customer
        order = Order.objects.create(
               customer=request.user,
               deliveryaddress=delivery_address,
               transaction=transaction,
               total_amount=request_data['total_amount']
           )
        
        #Loop through the list of order items and save in db
        for item in items:
            try:
                product = Product.objects.get(id=item['product_id'])
                quantity = item['quantity']
                OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity ,
                price=product.price
            )
            except Product.DoesNotExist:
                return Response({"status": False, "message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
             
        url = 'https://api.paystack.co/transaction/initialize'
        
        headers = {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        
        data = requests.post(
            url, headers=headers, 
            data={
            "amount": request_data['total_amount'] * 100, 
            "email": request.user.email, 
            "reference": "PIZ" + str(transaction_ref),
            "callback_url": "http://localhost:8000/orders/verify-payment"
            })
        
        response = data.json()
        
        if response['status'] == False:
            return Response(response)
        
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
            
        url = f'https://api.paystack.co/transaction/verify/{transaction}'
           
        headers = {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            
        data = requests.get(url, headers=headers)
            
        response = data.json()
            
        if response['status'] == False:
            return Response(response)
            
        if response['data']['status'] == 'success':
                
            Transaction.objects.filter(ref=reference).update(status=response['data']['status'])
            return Response(response, status=status.HTTP_200_OK)
            
        Transaction.objects.filter(ref=reference).update(status=response['data']['status'])
        return Response({"status": False, "message": "Verification Failed"}, status=status.HTTP_400_BAD_REQUEST)

class OrderListView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(operation_summary="View all orders")
    def get(self, request):
        orders = Order.objects.all()
        serializers = self.serializer_class(instance=orders, many=True)
        return Response({"status": True, "message": "Orders retreived successfully", "data": serializers.data})
    
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
       
        print(order.customer.email)
       
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

        
    

        
        
        