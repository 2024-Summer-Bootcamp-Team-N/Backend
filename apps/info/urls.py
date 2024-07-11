from django.urls import path
from . import views

urlpatterns = [
    path('generate-url', views.URLGenerator.as_view(), name='info_generate-url_list'),
]


