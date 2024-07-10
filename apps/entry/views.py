from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import RegionSerializer, ResidenceSerializer, TypeSerializer, OptionsSerializer
from .models import Regions, Residences, Types, Options
import re
import requests
import os


def parse_number(value):
    """ 문자열로 입력된 숫자를 정수로 변환 """
    return int(re.sub(r'[^0-9]', '', value))

def get_location(address):
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + address
    headers = {"Authorization": "KakaoAK " + os.getenv("KAKAO_AK")}  # 환경 변수에서 API 키 가져오기
    response = requests.get(url, headers=headers)
    api_json = response.json()
    if api_json['documents']:
        address_info = api_json['documents'][0]['address']
        crd = {"lat": str(address_info['y']), "lng": str(address_info['x'])}
        address_name = address_info['address_name']
        return crd
    return None

class RegionView(APIView):
    @swagger_auto_schema(
        request_body=RegionSerializer
    )
    def post(self, request):
        serializer = RegionSerializer(data=request.data)
        if serializer.is_valid():
            province = serializer.validated_data['province']
            district = serializer.validated_data['district']
            street = serializer.validated_data['street']
            full_address = f"{province} {district} {street}"
            coordinates = get_location(full_address)

            if coordinates:
                region = Regions.objects.create(
                    province=province,
                    district=district,
                    street=street,
                    latitude=coordinates['lat'],
                    longitude=coordinates['lng']
                )
                region.save()  # Save the object to the database
                data = {
                    "province": province,
                    "district": district,
                    "street": street,
                    "latitude": coordinates['lat'],
                    "longitude": coordinates['lng']
                }
                return Response({
                    "message": "입력한 지역 정보입니다.",
                    "data": data
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "주소를 변환할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "전부 다 입력 부탁 드립니다!"}, status=status.HTTP_400_BAD_REQUEST)

class ResidenceView(APIView): #거주형태 설정(아파트, 오피스텔, 빌라/주택, 원룸/투룸)
    @swagger_auto_schema(
        request_body=ResidenceSerializer
    )
    def post(self, request):
        serializer = ResidenceSerializer(data=request.data)
        if serializer.is_valid():
            selected_residences = [
                key for key, value in serializer.validated_data.items() if value
            ]
            if len(selected_residences) != 1:
                return Response({"message": "하나만 선택 해주세요!"}, status=status.HTTP_400_BAD_REQUEST)

            residence = Residences.objects.create(**serializer.validated_data)
            residence.save()

            return Response({
                "message": f"선택한 거주 형태는 {', '.join(selected_residences)}입니다.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TypeView(APIView): #월세/전세 --> 전세보증금 / 월세
    @swagger_auto_schema(
        request_body=TypeSerializer
    )
    def post(self, request):
        serializer = TypeSerializer(data=request.data)
        if serializer.is_valid():
            LEASE = serializer.validated_data.get('LEASE')
            MONTHLY_RENT = serializer.validated_data.get('MONTHLY_RENT')
            depositRangeMax = serializer.validated_data.get('depositRangeMax')
            priceRangeMax = serializer.validated_data.get('priceRangeMax')

            if LEASE and MONTHLY_RENT:
                return Response({"message": "하나만 선택 해주세요!"}, status=status.HTTP_400_BAD_REQUEST)
            if LEASE:
                if not depositRangeMax:
                    return Response({"message": "희망 전세금을 입력 해주세요!"}, status=status.HTTP_400_BAD_REQUEST)

                type = Types.objects.create(
                    LEASE=LEASE,
                    depositRangeMax=depositRangeMax
                )
                type.save()

                return Response({
                    "message": f"입력 하신 정보 입니다. 전세금은 '{depositRangeMax}'입니다.",
                    "data": {
                        "LEASE": LEASE,
                        "depositRangeMax": depositRangeMax
                    }
                }, status=status.HTTP_200_OK)
            if MONTHLY_RENT:
                if not (depositRangeMax and priceRangeMax):
                    return Response({"message": "보증금 / 월세를 입력 해주세요!"}, status=status.HTTP_400_BAD_REQUEST)

                type = Types.objects.create(
                    LEASE=LEASE,
                    depositRangeMax=depositRangeMax,
                    priceRangeMax=priceRangeMax
                )
                type.save()

                return Response({
                    "message": f"입력 하신 정보 입니다. 보증금은 '{depositRangeMax}', 월세는 '{priceRangeMax}'입니다.",
                    "data": {
                        "MONTHLY_RENT": MONTHLY_RENT,
                        "depositRangeMax": depositRangeMax,
                        "priceRangeMax": priceRangeMax
                    }
                }, status=status.HTTP_200_OK)



            return Response({"message": "하나만 선택 해주세요!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AptView(APIView): #아파트: 주차대수, 방수, 단기임대
    @swagger_auto_schema(
        request_body=OptionsSerializer
    )
    def post(self, request):
        serializer = OptionsSerializer(data=request.data, option_type='apartment')
        if serializer.is_valid():
            validated_data = serializer.validated_data
            messages = []

            if validated_data.get('parkingNumRangeMin') is not None:
                parking_choices = {0: "없음", 1: "1대 이상", 2: "2대 이상"}
                messages.append(f"가능한 주차 대수는 {parking_choices[validated_data.get('parkingNumRangeMin')]}입니다.")

            if validated_data.get('roomCount') is not None:
                if validated_data.get('roomCount') == 0:
                    messages.append("전체 방 개수를 포함합니다.")
                else:
                    room_choices = {1: "1개", 2: "2개", 3: "3개", 4: "4개 이상"}
                    messages.append(f"방 개수는 {room_choices[validated_data.get('roomCount')]}입니다.")

            if validated_data.get('isShortLease'):
                messages.append("단기 임대 매물만 보여 드립니다.")

            option = Options.objects.create(**validated_data)
            option.save()

            if messages:
                return Response({"messages": messages}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "선택된 옵션이 없습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OfficetelView(APIView): #오피스텔: 주차대수, 방수, 주차가능, 단기임대, 엘리베이터
    @swagger_auto_schema(
        request_body=OptionsSerializer
    )
    def post(self, request):
        serializer = OptionsSerializer(data=request.data, option_type='officetel')
        if serializer.is_valid():
            validated_data = serializer.validated_data
            messages = []
            if validated_data.get('parkingNumRangeMin') is not None:
                parking_choices = {0: "없음", 1: "1대 이상", 2: "2대 이상"}
                messages.append(f"가능한 주차 대수는 {parking_choices[validated_data.get('parkingNumRangeMin')]}입니다.")
            if validated_data.get('roomCount') is not None:
                if validated_data.get('roomCount') == 0:
                    messages.append("전체 방 개수를 포함합니다.")
                else:
                    room_choices = {1: "1개", 2: "2개", 3: "3개", 4: "4개 이상"}
                    messages.append(f"방 개수는 {room_choices[validated_data.get('roomCount')]}입니다.")
            if validated_data.get('hasElevator'):
                messages.append("엘리베이터가 있는 매물만 보여 드립니다.")
            if validated_data.get('isShortLease'):
                messages.append("단기 임대 매물만 보여 드립니다.")
            if validated_data.get('canParking'):
                messages.append("주차가 가능한 매물만 보여 드립니다.")

            option = Options.objects.create(**validated_data)
            option.save()

            if messages:
                return Response({"messages": messages}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "선택된 옵션이 없습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OneTwoView(APIView): #원/투룸: 주차가능, 단기임대, 엘리베이터, 분리형, 복층
    @swagger_auto_schema(
        request_body=OptionsSerializer
    )
    def post(self, request):
        serializer = OptionsSerializer(data=request.data, option_type='onetwo')
        if serializer.is_valid():
            validated_data = serializer.validated_data
            messages = []
            if validated_data.get('hasElevator'):
                messages.append("엘리베이터가 있는 매물만 보여 드립니다.")
            if validated_data.get('isShortLease'):
                messages.append("단기 임대 매물만 보여 드립니다.")
            if validated_data.get('canParking'):
                messages.append("주차가 가능한 매물만 보여 드립니다.")
            if validated_data.get('isDivision'):
                messages.append("분리형 매물만 보여 드립니다.")
            if validated_data.get('isDuplex'):
                messages.append("복층 매물만 보여 드립니다.")

            option = Options.objects.create(**validated_data)
            option.save()

            if messages:
                return Response({"messages": messages}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "선택된 옵션이 없습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HouseView(APIView): #주택/빌라: 주차가능, 단기임대, 엘리베이터
    @swagger_auto_schema(
        request_body=OptionsSerializer
    )
    def post(self, request):
        serializer = OptionsSerializer(data=request.data, option_type='house')
        if serializer.is_valid():
            validated_data = serializer.validated_data
            messages = []
            if validated_data.get('roomCount') is not None:
                if validated_data.get('roomCount') == 0:
                    messages.append("전체 방 개수를 포함합니다.")
                else:
                    room_choices = {1: "1개", 2: "2개", 3: "3개", 4: "4개 이상"}
                    messages.append(f"방 개수는 {room_choices[validated_data.get('roomCount')]}입니다.")
            if validated_data.get('hasElevator'):
                messages.append("엘리베이터가 있는 매물만 보여 드립니다.")
            if validated_data.get('isShortLease'):
                messages.append("단기 임대 매물만 보여 드립니다.")
            if validated_data.get('canParking'):
                messages.append("주차가 가능한 매물만 보여 드립니다.")

            option = Options.objects.create(**validated_data)
            option.save()

            if messages:
                return Response({"messages": messages}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "선택된 옵션이 없습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
