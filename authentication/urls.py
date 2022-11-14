from django.urls import path
from authentication.views import*

urlpatterns = [
    path('signup', UserCreateView.as_view(), name='sign_up'),
    path('forgot-password', PasswordResetView.as_view(), name='forgot_password'),
    path('reset-password', reset_password, name='reset_password')
]
