from rest_framework import serializers
from .models import Regions, Residences, Types, Options


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regions
        fields = ['province', 'district', 'street']


class ResidenceSerializer(serializers.ModelSerializer):
    apartment = serializers.BooleanField(default=False)
    officetel = serializers.BooleanField(default=False)
    house = serializers.BooleanField(default=False)
    onetwo = serializers.BooleanField(default=False)

    class Meta:
        model = Residences
        fields = ['apartment', 'officetel', 'house', 'onetwo']

    def validate(self, data):
        selected_options = [key for key, value in data.items() if value]

        if len(selected_options) != 1:
            raise serializers.ValidationError("하나만 선택해주세요.")

        return data


class TypeSerializer(serializers.ModelSerializer):
    LEASE = serializers.BooleanField(default=False)
    MONTHLY_RENT = serializers.BooleanField(default=False)
    depositRangeMax = serializers.CharField(default="0")
    priceRangeMax = serializers.CharField(default="0")

    class Meta:
        model = Types
        fields = ['LEASE', 'MONTHLY_RENT', 'depositRangeMax', 'priceRangeMax']

    def validate(self, data):
        lease = data.get('LEASE')
        monthly_rent = data.get('MONTHLY_RENT')
        deposit_range_max = data.get('depositRangeMax')
        price_range_max = data.get('priceRangeMax')

        if lease and monthly_rent:
            raise serializers.ValidationError("하나만 선택 해주세요!")

        if lease and not deposit_range_max:
            raise serializers.ValidationError("희망 전세금을 입력해주세요!")

        if monthly_rent and not (deposit_range_max and price_range_max):
            raise serializers.ValidationError("보증금과 월세를 입력해주세요!")

        return data


class OptionsSerializer(serializers.ModelSerializer):
    canParking = serializers.BooleanField(default=False)
    hasElevator = serializers.BooleanField(default=False)
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
    isDivision = serializers.BooleanField(default=False)
    isShortLease = serializers.BooleanField(default=False)
    isDuplex = serializers.BooleanField(default=False)

    class Meta:
        model = Options
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        option_type = kwargs.pop('option_type', None)
        super().__init__(*args, **kwargs)
        if option_type:
            if option_type == 'apartment':
                self.fields.pop('canParking')
                self.fields.pop('isDivision')
                self.fields.pop('isDuplex')
            elif option_type == 'officetel':
                self.fields.pop('isDivision')
                self.fields.pop('isDuplex')
            elif option_type == 'onetwo':
                self.fields.pop('roomCount')
                self.fields.pop('parkingNumRangeMin')
            elif option_type == 'house':
                self.fields.pop('parkingNumRangeMin')
                self.fields.pop('isDivision')
                self.fields.pop('isDuplex')
