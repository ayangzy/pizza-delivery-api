from django.urls import path
from orders.views import*


urlpatterns = [
    path('create/', OrderCreate.as_view(), name='orders'),
    path('list', OrderListView.as_view(), name='view_orders'),
    path('<int:order_id>/', OrderDetailView.as_view(), name='order'),
    path('order-status/<int:order_id>/',  UpdateOrderStatus.as_view(), name='order_status'),
    path('user/<int:user_id>/orders', UserOrdersView.as_view(), name='user_orders'),
    path('user/<int:user_id>/order/<int:order_id>/', UsersOrderDetailView.as_view(), name='users_order'),
    path('verify-payment', VerifyPayment.as_view(), name='verify_payment')
]
