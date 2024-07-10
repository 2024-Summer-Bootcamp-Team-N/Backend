from django.urls import path
from . import views

urlpatterns = [
    path('generate_url/', views.GenerateURLView.as_view(), name='info-detail'),
]