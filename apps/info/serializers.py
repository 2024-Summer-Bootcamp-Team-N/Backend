from rest_framework import serializers
from ..entry.models import Regions, Residences, Types, Options

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regions
        fields = ['province', 'district', 'street', 'id']

class ResidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Residences
        fields = ['apartment', 'officetel', 'house', 'onetwo']

class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Types
        fields = ['lease', 'monthly_rent', 'deposit_range_max', 'price_range_max']

class OptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = [
            'parking_num_range_min', 'is_short_lease', 'room_count',
            'has_elevator', 'can_parking', 'is_division', 'is_duplex'
        ]
