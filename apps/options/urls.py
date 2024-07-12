from django.urls import path
from .views import GenerateAndCrawlView

urlpatterns = [
    path('generate-and-crawl/', GenerateAndCrawlView.as_view(), name='generate-and-crawl'),
]
