from django.urls import path, include

urlpatterns = [
    path('api/v1/entry/', include('apps.entry.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/info/', include('apps.info.urls')),
    path('api/v1/options/', include('apps.options.urls')),
]