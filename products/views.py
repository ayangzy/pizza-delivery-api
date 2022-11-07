from rest_framework import generics
from products.serializers import ProductSerializer
from orders.models import Product
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework  import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


class ProductCreateListView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    #permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(operation_summary="Get all products")
    def get_queryset(self):
        queryset = Product.objects.all().order_by('-id')
        size = self.request.query_params.get('size', None)
        if size is not None:
            queryset = queryset.filter(size=size)
        return queryset
   
    # @swagger_auto_schema(operation_summary="Get all products")
    # def get(self, request):
        
    #     products = Product.objects.all().order_by('-id')
        
    #     paginator = PageNumberPagination()
    #     paginator.page_size = 10
    #     result_page = paginator.paginate_queryset(products,request)
        
    #     serializer = self.serializer_class(result_page, many=True)
    #     return paginator.get_paginated_response(serializer.data)
        
    
    @swagger_auto_schema(operation_summary="Create a new product")
    def post(self, request):
        request_data = request.data
        serializer = self.serializer_class(data=request_data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Product created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductDetailView(generics.GenericAPIView):
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser)
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(operation_summary="View the detail of a product by its ID")
    def get(self, request, product_id):
        try:
           product = Product.objects.get(pk=product_id)
           serializer = self.serializer_class(instance=product)
           return Response({"status": True, "message": "Product retrieved successfully", "data": serializer.data})
        except Product.DoesNotExist:
             return Response({"status": False, "messaage": f"product with the specified id {product_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(operation_summary="Update a product by its ID")
    def patch(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            serializer = self.serializer_class(instance=product, data=request.data)
        
            if serializer.is_valid():
                serializer.save()
                return Response({"status": True, "message": "Product updated successfully", "data": serializer.data})
            
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Product.DoesNotExist:
             return Response({"status": False, "messaage": f"product with the specified id {product_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
    
    @swagger_auto_schema(operation_summary="Delete a product by its ID")
    def delete(self, request, product_id):
        try:
             product = Product.objects.get(pk=product_id)
             product.delete()
             return Response({"status": True, "messaage": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
         
        except Product.DoesNotExist:
            return Response({"status": False, "messaage": f"product with the specified id {product_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
       
        
       
        
       
        
           
        
      
        
