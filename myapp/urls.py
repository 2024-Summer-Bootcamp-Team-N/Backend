from . import views  # myapp 내의 views 가져오기
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet

router = DefaultRouter()
router.register(r'api', PostViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('read/<int:id>/', views.read, name='read'),
    path('', include(router.urls)),  # API 엔드포인트 추가
]


