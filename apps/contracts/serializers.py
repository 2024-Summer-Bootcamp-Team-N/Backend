from rest_framework import serializers
from .models import LatestRoomInfo

class LatestRoomInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatestRoomInfo
        fields = '__all__'  # 또는 필요한 필드만 명시적으로 포함할 수 있습니다.
