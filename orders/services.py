from orders.models import*
import random
from rest_framework.exceptions import NotFound, APIException
from django.conf import settings
import requests


class OrderService:
    
    def create_order(self, request):
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
                raise NotFound("product not found")
            
        return order


class PaystackService:
    def pay(self, request, ref):
        
        url = 'https://api.paystack.co/transaction/initialize'
        
        headers = {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        
        data={
            "amount": request.data['total_amount'] * 100, 
            "email": request.user.email, 
            "reference": ref,
            "callback_url": "http://localhost:8000/orders/verify-payment"
            }
        
        response = requests.post(url, headers=headers, data=data).json()
        
        if response['status'] == False:
            raise APIException(response)
        
        return response
    
    def verify_payment(self, request):
        
        reference = request.GET.get('reference')
        
        url = f'https://api.paystack.co/transaction/verify/{reference}'
           
        headers = {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            
        data = requests.get(url, headers=headers)
        response = data.json()
        
        if response['status'] == False:
            raise APIException(response)
        
        return response
    
        
   
            