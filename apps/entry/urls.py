from django.urls import path
from . import views

urlpatterns = [
    path('regions', views.RegionView.as_view(), name='entry_regions_create'),
    path('residences', views.ResidenceView.as_view(), name='entry_residences_create'),
    path('residences/apt', views.AptView.as_view(), name='entry_residences_apt_create'),
    path('residences/house', views.HouseView.as_view(), name='entry_residences_house_create'),
    path('residences/officetel', views.OfficetelView.as_view(), name='entry_residences_officetel_create'),
    path('residences/onetwo', views.OneTwoView.as_view(), name='entry_residences_onetwo_create'),
    path('types', views.TypeView.as_view(), name='entry_types_create'),
]

