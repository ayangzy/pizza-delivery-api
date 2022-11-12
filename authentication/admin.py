from django.contrib import admin
from authentication.models import User, PasswordReset

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone_number', 'is_active', 'is_staff', 'is_superuser']

admin.site.register(User, UserAdmin)
admin.site.register(PasswordReset)
