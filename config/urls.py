from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API for your config",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    urlconf='config.api_urls'
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/entry/', include('apps.entry.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/info/', include('apps.info.urls')),
    path('api/v1/options/', include('apps.options.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
