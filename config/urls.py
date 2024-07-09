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
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('entry/', include('apps.entry.urls')),  # entry 앱의 urls.py 포함
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # 위와 같이 작성
    #path('users/', include('apps.users.urls')),  # users 앱의 urls.py 포함
    #path('info/', include('apps.info.urls')),  # info 앱의 urls.py 포함
    #path('options/', include('apps.options.urls')),  # options 앱의 urls.py 포함
    path('users/', include('apps.users.urls')),
]



