from django.urls import path
from products.views import *

urlpatterns = [
    path('', ProductCreateListView.as_view(), name='products'),
    path('<int:product_id>/', ProductDetailView.as_view(), name='product')
]
