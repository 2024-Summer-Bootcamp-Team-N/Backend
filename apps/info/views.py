from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Region, Residence, PropertyType, Option
from ..entry.serializers import RegionSerializer, ResidenceSerializer, TypeSerializer, OptionsSerializer
from urllib.parse import urlencode
from django.http import HttpResponse
from ..entry.views import get_location
from drf_yasg.utils import swagger_auto_schema


class URLGenerator(APIView):

    @swagger_auto_schema(
        request_body=RegionSerializer,  # 사용자 입력 데이터의 Serializer 클래스
        responses={200: RegionSerializer},  # 응답의 Serializer 클래스
        operation_description="Generate URL based on user input.",  # 작업 설명
    )

    def post(self, request, format=None):
        # 사용자 입력 값 받아오기
        region_data = request.data.get('region', {})
        residence_data = request.data.get('residence', {})
        type_data = request.data.get('type', {})
        options_data = request.data.get('options', {})

        # 시리얼라이저로 데이터 검증
        region_serializer = RegionSerializer(data=region_data)
        residence_serializer = ResidenceSerializer(data=residence_data)
        type_serializer = TypeSerializer(data=type_data)
        options_serializer = OptionsSerializer(data=options_data)

        if not (
                region_serializer.is_valid() and residence_serializer.is_valid() and type_serializer.is_valid() and options_serializer.is_valid()):
            return Response({
                'region': region_serializer.errors,
                'residence': residence_serializer.errors,
                'type': type_serializer.errors,
                'options': options_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 주소 정보에서 위도, 경도 얻기
        address = f"{region_data.get('province')}, {region_data.get('district')}, {region_data.get('street')}"
        crd = get_location(address)

        if crd is None:
            return Response({'error': 'Invalid address.'}, status=status.HTTP_400_BAD_REQUEST)

        # 임대 유형 설정
        selling_type = None
        if type_data.get('lease'):
            selling_type = "LEASE"
        elif type_data.get('monthly_rent'):
            selling_type = "MONTHLY_RENT"
        else:
            return Response({'error': 'Invalid selling type.'}, status=status.HTTP_400_BAD_REQUEST)

        # 기본 매개변수 설정
        base_params = {
            "sellingTypeList": f'["{selling_type}"]',
            "m_lat": crd['lat'],
            "m_lng": crd['lng'],
            "m_zoom": 15
        }

        # 임대 유형에 따른 매개변수 설정
        params = {}
        if selling_type == "LEASE":
            params["depositRangeMax"] = type_data.get('depositRangeMax')
        elif selling_type == "MONTHLY_RENT":
            params["depositRangeMax"] = type_data.get('depositRangeMax')
            params["priceRangeMax"] = type_data.get('priceRangeMax')

        # 주거 형태 설정
        property_type = None
        if residence_data.get('apartment'):
            property_type = "apt"
        elif residence_data.get('officetel'):
            property_type = "officetel"
        elif residence_data.get('house'):
            property_type = "house"
        elif residence_data.get('onetwo'):
            property_type = "onetwo"
        else:
            return Response({'error': 'Invalid residence type.'}, status=status.HTTP_400_BAD_REQUEST)

        # 각 주거 형태에 따른 추가 옵션 설정
        if property_type in ["apt", "officetel", "house", "onetwo"]:
            params.update({
                "parkingNumRangeMin": options_data.get('parkingNumRangeMin'),
                "isShortLease": options_data.get('isShortLease'),
                "roomCount": options_data.get('roomCount')
            })
            if property_type in ["officetel", "house", "onetwo"]:
                params.update({
                    "hasElevator": options_data.get('hasElevator')
                })
            if property_type in ["house", "onetwo"]:
                params.update({
                    "canParking": options_data.get('canParking')
                })
            if property_type == "onetwo":
                params.update({
                    "isDivision": options_data.get('isDivision'),
                    "isDuplex": options_data.get('isDuplex')
                })
        else:
            return Response({'error': 'Invalid property type.'}, status=status.HTTP_400_BAD_REQUEST)

        # 방 수가 숫자라면 변환하여 설정
        room_count_map = {
            "1": "ONE_ROOM",
            "2": "TWO_ROOM",
            "3": "THREE_ROOM",
            "4": "FOUR_ROOM",
            "5": "FOUR_ROOM",
            "6": "FOUR_ROOM",
            "7": "FOUR_ROOM",
            "8": "FOUR_ROOM",
            "9": "FOUR_ROOM",
            "10": "FOUR_ROOM",
        }
        if params["roomCount"].isdigit():
            room_count_value = params["roomCount"]
            if room_count_value in room_count_map:
                params["roomCount"] = room_count_map[room_count_value]
            else:
                return Response({'error': 'Invalid room count.'}, status=status.HTTP_400_BAD_REQUEST)

        # URL 생성
        base_url = f"https://www.dabangapp.com/map/{property_type}?"
        param_str = urlencode({**params, **base_params})
        full_url = base_url + param_str

        region = region_serializer.save(url=full_url)

        response_data = region_serializer.data
        response_data['url'] = full_url
        return Response(response_data, status=status.HTTP_200_OK)