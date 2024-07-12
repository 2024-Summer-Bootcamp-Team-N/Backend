from rest_framework import serializers
from .models import RoomInfo

class RoomInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomInfo
        fields = '__all__'
