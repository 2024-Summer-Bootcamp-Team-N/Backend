from rest_framework import serializers
from .models import Category

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['province', 'district', 'street']

class ResidenceSerializer(serializers.Serializer):
    apartment = serializers.BooleanField(required=False)
    villa = serializers.BooleanField(required=False)
    room = serializers.BooleanField(required=False)

class TypeSerializer(serializers.Serializer):
    yearly = serializers.BooleanField(required=False)
    monthly = serializers.BooleanField(required=False)
    yearly_fee = serializers.CharField(required=False)
    deposit = serializers.CharField(required=False)
    monthly_fee = serializers.CharField(required=False)

    def validate(self, data):
        yearly = data.get('yearly')
        monthly = data.get('monthly')
        yearly_fee = data.get('yearly_fee')
        deposit = data.get('deposit')
        monthly_fee = data.get('monthly_fee')

        if yearly and monthly:
            raise serializers.ValidationError("하나만 선택 해주세요!")

        if yearly and not yearly_fee:
            raise serializers.ValidationError("희망 전세금을 입력해주세요!")

        if monthly and not (deposit and monthly_fee):
            raise serializers.ValidationError("보증금과 월세를 입력해주세요!")

        return data

