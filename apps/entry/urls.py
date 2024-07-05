from django.urls import path
from .views import RegionView, ResidenceView, TypeView

urlpatterns = [
    path('regions/', RegionView.as_view(), name='region'),
    path('residences/', ResidenceView.as_view(), name='residence'),
    path('types/', TypeView.as_view(), name='type'),
]
