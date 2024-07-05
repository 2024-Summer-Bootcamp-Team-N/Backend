from django.urls import path
from . import views

urlpatterns = [
    path('', views.OptionListView.as_view(), name='option-list'),
    path('<int:pk>/', views.OptionDetailView.as_view(), name='option-detail'),
]
