from django.urls import path
from .views import RegionView, ResidenceView, TypeView, AptView, OfficetelView, OneTwoView, HouseView

urlpatterns = [
    path('regions/', RegionView.as_view(), name='region'),
    path('residences/', ResidenceView.as_view(), name='residence'),
    path('types/', TypeView.as_view(), name='type'),
    path('residences/apt/', AptView.as_view(), name='apartment-options'),
    path('residences/officetel/', OfficetelView.as_view(), name='officetel-options'),
    path('residences/onetwo/', OneTwoView.as_view(), name='onetwo-options'),
    path('residences/house/', HouseView.as_view(), name='house-options'),

]
