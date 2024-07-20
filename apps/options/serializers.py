from rest_framework import serializers
from .models import RoomInfo, RoomDetailInfo

class RoomInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomInfo
        fields = '__all__'

class RoomDetailInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomDetailInfo
        fields = '__all__'