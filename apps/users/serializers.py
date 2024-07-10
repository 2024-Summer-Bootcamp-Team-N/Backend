from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'auth_id', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        instance.auth_id = validated_data.get('auth_id', instance.auth_id)
        if 'password' in validated_data:
            instance.password = validated_data['password']  # 평문 비밀번호 업데이트
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('auth_id', 'password', 'confirm_password', 'name')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("비밀번호를 다시 확인해주세요.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # confirm_password 필드를 제거합니다.
        user = CustomUser.objects.create(
            auth_id=validated_data['auth_id'],
            password=validated_data['password'],  # 비밀번호를 평문으로 저장
            name=validated_data['name']
        )
        return user

class LoginSerializer(serializers.Serializer):
    auth_id = serializers.CharField()
    password = serializers.CharField(write_only=True)

