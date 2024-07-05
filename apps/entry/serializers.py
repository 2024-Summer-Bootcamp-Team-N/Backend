from rest_framework import serializers
from .models import Regions, Residences, Types, Options

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regions
        fields = ['province', 'district', 'street']

class ResidenceSerializer(serializers.Serializer):
    apartment = serializers.BooleanField(required=False)
    officetel = serializers.BooleanField(required=False)
    villa = serializers.BooleanField(required=False)
    house = serializers.BooleanField(required=False)

    def validate(self, data):
        # 선택된 필드를 모두 리스트에 저장
        selected_options = [key for key, value in data.items() if value]

        # 선택된 옵션이 하나가 아닌 경우 오류 발생
        if len(selected_options) != 1:
            raise serializers.ValidationError("하나만 선택해주세요.")

        return data

class TypeSerializer(serializers.Serializer):
    LEASE = serializers.BooleanField(required=False)
    MONTHLY_RENT = serializers.BooleanField(required=False)
    depositRangeMax = serializers.CharField(required=False)
    # deposit = serializers.CharField(required=False)
    priceRangeMax = serializers.CharField(required=False)

    def validate(self, data):
        LEASE = data.get('LEASE')
        MONTHLY_RENT = data.get('MONTHLY_RENT')
        depositRangeMax = data.get('yearly_fee')
        # deposit = data.get('deposit')
        priceRangeMax = data.get('monthly_fee')

        if LEASE and MONTHLY_RENT:
            raise serializers.ValidationError("하나만 선택 해주세요!")

        if LEASE and not depositRangeMax:
            raise serializers.ValidationError("희망 전세금을 입력해주세요!")

        if MONTHLY_RENT and not (depositRangeMax and priceRangeMax):
            raise serializers.ValidationError("보증금과 월세를 입력해주세요!")

        return data
class AptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = '__all__'

    parkingNumRangeMin = serializers.ChoiceField(
        choices=[
            (0, '상관없음'),
            (1, '1대 이상'),
            (2, '2대 이상')],
        default=0, required=False)
    roomCount = serializers.ChoiceField(
        choices=[
            (0, '상관없음'),
            (1, '1개'),
            (2, '2개'),
            (3, '3개'),
            (4, '4개 이상')],
        default=0, required=False)
    hasElevator = serializers.BooleanField(required=False)
    isShortLease = serializers.BooleanField(required=False)

class OfficetelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = '__all__'

    parkingNumRangeMin = serializers.ChoiceField(
        choices=[
            (0, '상관없음'),
            (1, '1대 이상'),
            (2, '2대 이상')],
        default=0, required=False)
    roomCount = serializers.ChoiceField(
        choices=[
            (0, '상관없음'),
            (1, '1개'),
            (2, '2개'),
            (3, '3개'),
            (4, '4개 이상')],
        default=0, required=False)
    hasElevator = serializers.BooleanField(required=False)
    isShortLease = serializers.BooleanField(required=False)
    canParking = serializers.BooleanField(required=False)

class OnetwoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = '__all__'

    canParking = serializers.BooleanField(required=False)
    hasElevator = serializers.BooleanField(required=False)
    isShortLease = serializers.BooleanField(required=False)
    isDivision = serializers.BooleanField(required=False)
    isDuplex = serializers.BooleanField(required=False)

class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = '__all__'

    roomCount = serializers.ChoiceField(
        choices=[
            (0, '상관없음'),
            (1, '1개'),
            (2, '2개'),
            (3, '3개'),
            (4, '4개 이상')],
        default=0, required=False)
    canParking = serializers.BooleanField(required=False)
    hasElevator = serializers.BooleanField(required=False)
    isShortLease = serializers.BooleanField(required=False)
# class OptionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Options
#         fields = '__all__'
#
#     canParking = serializers.BooleanField(required=False)
#     hasElevator = serializers.BooleanField(required=False)
#     # parkingNumRangeMin = serializers.BooleanField(required=False)
#     # roomCount = serializers.BooleanField(required=False)
#     isDivision = serializers.BooleanField(required=False)
#     isShortLease = serializers.BooleanField(required=False)
#     isDuplex = serializers.BooleanField(required=False)
#
#     PARKING_CHOICES = (
#         (0, '상관없음'),
#         (1, '1대 이상'),
#         (2, '2대 이상'),
#     )
#
#     ROOM_CHOICES = (
#         (0, '상관없음'),
#         (1, '1개'),
#         (2, '2개'),
#         (3, '3개'),
#         (4, '4개 이상'),
#     )
#     parkingNumRangeMin = serializers.ChoiceField(choices=PARKING_CHOICES, default=0, required=False)
#     roomCount = serializers.ChoiceField(choices=ROOM_CHOICES, default=0, required=False)
#
#     def validate(self, data):
#         canParking = data.get('canParking')
#         hasElevator = data.get('hasElevator')
#         parkingNumRangeMin = data.get('parkingNumRangeMin')
#         roomCount = data.get('roomCount')
#         isDivision = data.get('isDivision')
#         isShortLease = data.get('isShortLease')
#         isDuplex = data.get('isDuplex')

