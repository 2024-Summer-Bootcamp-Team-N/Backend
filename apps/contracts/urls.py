from django.urls import path
from .views import LatestRoomDetailInfoAPIView, S3ImageUploadView, S3ImageListView

urlpatterns = [
    path('latest-room-detail/', LatestRoomDetailInfoAPIView.as_view(), name='latest_room_detail'),
    path('s3-upload/', S3ImageUploadView.as_view(), name='s3_upload'),
    path('s3-list/', S3ImageListView.as_view(), name='s3_list'),
]