from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter

schema_view = get_schema_view(
   openapi.Info(
      title="Pizza Delivery API",
      default_version='v1',
      description="A RESTful API for Pizza Delivery Service",
      contact=openapi.Contact(email="felixdecoder2020@gmail.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("authentication.urls")),
    path("orders/", include("orders.urls")),
    path("products/", include("products.urls")),
    path('auth/', include('djoser.urls.jwt')),
    path('', include('djoser.urls')),
    path('swagger<format>.json|.yaml/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
