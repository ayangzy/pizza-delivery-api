from django.urls import path
from authentication.views import*

urlpatterns = [
    path('signup', UserCreateView.as_view(), name='sign_up'),
    path('password-rest', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm', reset_password)
]
