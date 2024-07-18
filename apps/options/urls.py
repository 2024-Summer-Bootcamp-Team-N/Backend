from django.urls import path
from .views import GenerateAndCrawlView

urlpatterns = [
    path('crawling/', GenerateAndCrawlView.as_view(), name='trigger_crawl'),
]