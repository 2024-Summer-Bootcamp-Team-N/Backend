from django.urls import path
from .views import URLGenerator

urlpatterns = [
    path('generate-url/', URLGenerator.as_view(), name='generate-url'),
]
