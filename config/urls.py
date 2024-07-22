from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import TemplateView
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns

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

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/contracts/', include('apps.contracts.urls')),
    path('api/v1/entry/', include('apps.entry.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/info/', include('apps.info.urls')),
    path('api/v1/options/', include('apps.options.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('websocket-test/', TemplateView.as_view(template_name="websocket_test.html")),
]

