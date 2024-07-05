from django.urls import path
from .views import RegionView, ResidenceView, TypeView, AptView, HouseView, OneTwoView, OfficetelView

urlpatterns = [
    path('regions/', RegionView.as_view(), name='region'),
    path('residences/', ResidenceView.as_view(), name='residence'),
    path('types/', TypeView.as_view(), name='type'),
    path('apt/', AptView.as_view(), name='apartment'),
    path('house/', HouseView.as_view(), name='house'),
    path('onetwo/', OneTwoView.as_view(), name='onetwo'),
    path('officetel/', OfficetelView.as_view(), name='officetel'),
]
