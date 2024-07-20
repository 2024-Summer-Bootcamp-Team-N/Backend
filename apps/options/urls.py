from django.urls import path
from .views import GenerateAndCrawlView, DetailedRoomInfoView

urlpatterns = [
    path('crawling/', GenerateAndCrawlView.as_view(), name='trigger_crawl'),
    path('crawling/<int:room_id>/', DetailedRoomInfoView.as_view(), name='crawl_room_detail'),
]