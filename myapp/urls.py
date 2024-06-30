from django.urls import path
from . import views  # myapp 내의 views 가져오기

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('read/<int:id>/', views.read, name='read'),
]

