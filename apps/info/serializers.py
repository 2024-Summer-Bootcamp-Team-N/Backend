from rest_framework import serializers
from .models import Region, Residence, PropertyType, Option

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['province', 'district', 'street','id','name','url']

class ResidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Residence
        fields = ['apartment', 'officetel', 'house', 'onetwo']

class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyType
        fields = ['lease', 'monthly_rent', 'depositRangeMax', 'priceRangeMax']

class OptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = [
            'parkingNumRangeMin', 'isShortLease', 'roomCount',
            'hasElevator', 'canParking', 'isDivision', 'isDuplex'
        ]