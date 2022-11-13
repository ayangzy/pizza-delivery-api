from django.urls import path
from authentication.views import UserCreateView, PasswordReset

urlpatterns = [
    path('signup', UserCreateView.as_view(), name='sign_up'),
    path('password-rest', PasswordReset.as_view(), name='password_reset')
]
