from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import RegionSerializer, ResidenceSerializer, TypeSerializer, OptionsSerializer
import re

def parse_number(value):
    """ 문자열로 입력된 숫자를 정수로 변환 """
    return int(re.sub(r'[^0-9]', '', value))

class RegionView(APIView): #지역설정
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'province': openapi.Schema(type=openapi.TYPE_STRING, description='시/도 입력', example='인천광역시'),
                'district': openapi.Schema(type=openapi.TYPE_STRING, description='구 입력', example='미추홀구'),
                'street': openapi.Schema(type=openapi.TYPE_STRING, description='동 입력', example='숭의동')
            },
            required=['province', 'district', 'street']
        )
    )
    def post(self, request):
        serializer = RegionSerializer(data=request.data)  # 데이터 본문에서 받아오기
        if serializer.is_valid():
            province = serializer.validated_data['province']
            district = serializer.validated_data['district']
            street = serializer.validated_data['street']
            results = (province, district, street, [])

            return Response({
                "message": "입력한 지역 정보입니다.",
                "data": serializer.data,
                "results": results.to_dict(orient='records')
            }, status=status.HTTP_200_OK)
        return Response({"message": "전부 다 입력 부탁 드립니다!"}, status=status.HTTP_400_BAD_REQUEST)



class ResidenceView(APIView): #거주형태 설정(아파트, 오피스텔, 빌라/주택, 원룸/투룸)
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('apartment', openapi.IN_QUERY, description="아파트 선택", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('officetel', openapi.IN_QUERY, description="오피스텔 선택", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('house', openapi.IN_QUERY, description="주택/빌라 선택", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('onetwo', openapi.IN_QUERY, description="원룸/투룸 선택", type=openapi.TYPE_BOOLEAN, required=False),
        ]
    )
    def post(self, request):
        serializer = ResidenceSerializer(data=request.query_params)
        if serializer.is_valid():
            selected_residences = [
                key for key, value in serializer.validated_data.items() if value
            ]
            if len(selected_residences) != 1:
                return Response({"message": "하나만 선택해주세요!"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "message": f"선택한 거주 형태는 {', '.join(selected_residences)}입니다.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TypeView(APIView): #월세/전세 --> 전세보증금 / 월세
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('LEASE', openapi.IN_QUERY, description="전세 선택", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('MONTHLY_RENT', openapi.IN_QUERY, description="월세 선택", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('depositRangeMax', openapi.IN_QUERY, description="전세/보증금 금액 입력", type=openapi.TYPE_STRING, required=False),
            # openapi.Parameter('deposit', openapi.IN_QUERY, description="보증금 입력", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('priceRangeMax', openapi.IN_QUERY, description="월세 금액 입력", type=openapi.TYPE_STRING, required=False),
        ],
    )
    def post(self, request):
        serializer = TypeSerializer(data=request.query_params)
        if serializer.is_valid():
            LEASE = serializer.validated_data.get('LEASE')
            MONTHLY_RENT = serializer.validated_data.get('MONTHLY_RENT')
            depositRangeMax = serializer.validated_data.get('yearly_fee')
            # deposit = serializer.validated_data.get('deposit')
            priceRangeMax = serializer.validated_data.get('priceRangeMax')

            if LEASE and MONTHLY_RENT:
                return Response({"message": "하나만 선택해주세요!"}, status=status.HTTP_400_BAD_REQUEST)
            if LEASE:
                if not depositRangeMax:
                    return Response({"message": "희망 전세금을 입력해주세요!"}, status=status.HTTP_400_BAD_REQUEST)
                return Response({
                    "message": f"입력한 전세 정보입니다. 희망하신 전세금은 '{depositRangeMax}'입니다.",
                    "data": {
                        "LEASE": LEASE,
                        "depositRangeMax": depositRangeMax
                    }
                }, status=status.HTTP_200_OK)
            if MONTHLY_RENT:
                if not (depositRangeMax and priceRangeMax):
                    return Response({"message": "보증금과 월세를 입력해주세요!"}, status=status.HTTP_400_BAD_REQUEST)
                return Response({
                    "message": f"입력한 월세 정보입니다. 희망하신 보증금은 '{depositRangeMax}', 월세는 '{priceRangeMax}'입니다.",
                    "data": {
                        "MONTHLY_RENT": MONTHLY_RENT,
                        "depositRangeMax": depositRangeMax,
                        "priceRangeMax": priceRangeMax
                    }
                }, status=status.HTTP_200_OK)
            return Response({"message": "하나만 선택해주세요!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class AptView(APIView):
#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter('parkingNumRangeMin', openapi.IN_QUERY, description="최소 주차 대수", type=openapi.TYPE_INTEGER,
#                               enum=[0, 1, 2], required=False),
#             openapi.Parameter('roomCount', openapi.IN_QUERY, description="방 개수 설정", type=openapi.TYPE_INTEGER,
#                               enum=[0, 1, 2, 3, 4], required=False),
#             openapi.Parameter('isShortLease', openapi.IN_QUERY, description="단기임대", type=openapi.TYPE_BOOLEAN, required=False),
#         ]
#     )
#     def post(self, request):
#         serializer = AptSerializer(data=request.query_params)
#         if serializer.is_valid():
#             validated_data = serializer.validated_data
#             messages = []
#
#             if validated_data.get('parkingNumRangeMin') is not None:
#                 parking_choices = {0: "0개", 1: "1대 이상", 2: "2대 이상"}
#                 messages.append(f"가능한 주차 대수는 {parking_choices[validated_data.get('parkingNumRangeMin')]}입니다.")
#
#             if validated_data.get('roomCount') is not None:
#                 room_choices = {0: "0개", 1: "1개", 2: "2개", 3: "3개", 4: "4개 이상"}
#                 messages.append(f"방 개수는 {room_choices[validated_data.get('roomCount')]}입니다.")
#
#             if validated_data.get('isShortLease'):
#                 messages.append("단기임대 매물만 보여드립니다.")
#
#             if messages:
#                 return Response({"messages": messages}, status=status.HTTP_200_OK)
#             else:
#                 return Response({"message": "선택된 옵션이 없습니다."}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class OfficetelView(APIView):
#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter('parkingNumRangeMin', openapi.IN_QUERY, description="최소 주차 대수", type=openapi.TYPE_INTEGER, enum=[0, 1, 2], required=False),
#             openapi.Parameter('roomCount', openapi.IN_QUERY, description="방 개수 설정", type=openapi.TYPE_INTEGER, enum=[0, 1, 2, 3, 4], required=False),
#             openapi.Parameter('hasElevator', openapi.IN_QUERY, description="엘리베이터 유무", type=openapi.TYPE_BOOLEAN, required=False),
#             openapi.Parameter('isShortLease', openapi.IN_QUERY, description="단기임대", type=openapi.TYPE_BOOLEAN, required=False),
#             openapi.Parameter('canParking', openapi.IN_QUERY, description="주차 가능 여부", type=openapi.TYPE_BOOLEAN, required=False),
#         ]
#     )
#     def post(self, request):
#         serializer = OfficetelSerializer(data=request.query_params)
#         if serializer.is_valid():
#             validated_data = serializer.validated_data
#             messages = []
#             if validated_data.get('parkingNumRangeMin') is not None:
#                 parking_choices = {0: "0개", 1: "1대 이상", 2: "2대 이상"}
#                 messages.append(f"가능한 주차 대수는 {parking_choices[validated_data.get('parkingNumRangeMin')]}입니다.")
#             if validated_data.get('roomCount') is not None:
#                 room_choices = {0: "0개", 1: "1개", 2: "2개", 3: "3개", 4: "4개 이상"}
#                 messages.append(f"방 개수는 {room_choices[validated_data.get('roomCount')]}입니다.")
#             if validated_data.get('hasElevator'):
#                 messages.append("엘리베이터가 있는 매물만 보여드립니다.")
#             if validated_data.get('isShortLease'):
#                 messages.append("단기임대 매물만 보여드립니다.")
#             if validated_data.get('canParking'):
#                 messages.append("주차가 가능한 매물만 보여드립니다.")
#             if messages:
#                 return Response({"messages": messages}, status=status.HTTP_200_OK)
#             else:
#                 return Response({"message": "선택된 옵션이 없습니다."}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
# class OneTwoView(APIView):
#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter('canParking', openapi.IN_QUERY, description="주차 가능 여부", type=openapi.TYPE_BOOLEAN, required=False),
#             openapi.Parameter('hasElevator', openapi.IN_QUERY, description="엘리베이터 유무", type=openapi.TYPE_BOOLEAN, required=False),
#             openapi.Parameter('isShortLease', openapi.IN_QUERY, description="단기임대", type=openapi.TYPE_BOOLEAN, required=False),
#             openapi.Parameter('isDivision', openapi.IN_QUERY, description="분리형", type=openapi.TYPE_BOOLEAN, required=False),
#             openapi.Parameter('isDuplex', openapi.IN_QUERY, description="복층", type=openapi.TYPE_BOOLEAN, required=False),
#         ]
#     )
#     def post(self, request):
#         serializer = OnetwoSerializer(data=request.query_params)
#         if serializer.is_valid():
#             validated_data = serializer.validated_data
#             messages = []
#             if validated_data.get('hasElevator'):
#                 messages.append("엘리베이터가 있는 매물만 보여드립니다.")
#             if validated_data.get('isShortLease'):
#                 messages.append("단기임대 매물만 보여드립니다.")
#             if validated_data.get('canParking'):
#                 messages.append("주차가 가능한 매물만 보여드립니다.")
#             if validated_data.get('isDivision'):
#                 messages.append("분리형 매물만 보여드립니다.")
#             if validated_data.get('isDuplex'):
#                 messages.append("복층 매물만 보여드립니다.")
#             if messages:
#                 return Response({"messages": messages}, status=status.HTTP_200_OK)
#             else:
#                 return Response({"message": "선택된 옵션이 없습니다."}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
# class HouseView(APIView):
#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter('roomCount', openapi.IN_QUERY, description="방 개수 설정", type=openapi.TYPE_INTEGER,
#                               enum=[0, 1, 2, 3, 4], required=False),
#             openapi.Parameter('canParking', openapi.IN_QUERY, description="주차 가능 여부", type=openapi.TYPE_BOOLEAN, required=False),
#             openapi.Parameter('hasElevator', openapi.IN_QUERY, description="엘리베이터 유무", type=openapi.TYPE_BOOLEAN, required=False),
#             openapi.Parameter('isShortLease', openapi.IN_QUERY, description="단기임대", type=openapi.TYPE_BOOLEAN, required=False),
#         ]
#     )
#     def post(self, request):
#         serializer = HouseSerializer(data=request.query_params)
#         if serializer.is_valid():
#             validated_data = serializer.validated_data
#             messages = []
#             if validated_data.get('roomCount') is not None:
#                 room_choices = {0: "0개", 1: "1개", 2: "2개", 3: "3개", 4: "4개 이상"}
#                 messages.append(f"방 개수는 {room_choices[validated_data.get('roomCount')]}입니다.")
#             if validated_data.get('canParking'):
#                 messages.append("주차가 가능한 매물만 보여드립니다.")
#             if validated_data.get('hasElevator'):
#                 messages.append("엘리베이터가 있는 매물만 보여드립니다.")
#             if validated_data.get('isShortLease'):
#                 messages.append("단기임대 매물만 보여드립니다.")
#             if messages:
#                 return Response({"messages": messages}, status=status.HTTP_200_OK)
#             else:
#                 return Response({"message": "선택된 옵션이 없습니다."}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AptView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('parkingNumRangeMin', openapi.IN_QUERY, description="최소 주차 대수", type=openapi.TYPE_INTEGER, enum=[0, 1, 2], required=False),
            openapi.Parameter('roomCount', openapi.IN_QUERY, description="방 개수 설정", type=openapi.TYPE_INTEGER, enum=[0, 1, 2, 3, 4], required=False),
            openapi.Parameter('isShortLease', openapi.IN_QUERY, description="단기임대", type=openapi.TYPE_BOOLEAN, required=False),
        ]
    )
    def post(self, request):
        serializer = OptionsSerializer(data=request.query_params, option_type='apartment')
        if serializer.is_valid():
            validated_data = serializer.validated_data
            messages = []

            if validated_data.get('parkingNumRangeMin') is not None:
                parking_choices = {0: "0개", 1: "1대 이상", 2: "2대 이상"}
                messages.append(f"가능한 주차 대수는 {parking_choices[validated_data.get('parkingNumRangeMin')]}입니다.")

            if validated_data.get('roomCount') is not None:
                room_choices = {0: "0개", 1: "1개", 2: "2개", 3: "3개", 4: "4개 이상"}
                messages.append(f"방 개수는 {room_choices[validated_data.get('roomCount')]}입니다.")

            if validated_data.get('isShortLease'):
                messages.append("단기임대 매물만 보여드립니다.")

            if messages:
                return Response({"messages": messages}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "선택된 옵션이 없습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OfficetelView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('parkingNumRangeMin', openapi.IN_QUERY, description="최소 주차 대수", type=openapi.TYPE_INTEGER, enum=[0, 1, 2], required=False),
            openapi.Parameter('roomCount', openapi.IN_QUERY, description="방 개수 설정", type=openapi.TYPE_INTEGER, enum=[0, 1, 2, 3, 4], required=False),
            openapi.Parameter('hasElevator', openapi.IN_QUERY, description="엘리베이터 유무", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('isShortLease', openapi.IN_QUERY, description="단기임대", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('canParking', openapi.IN_QUERY, description="주차 가능 여부", type=openapi.TYPE_BOOLEAN, required=False),
        ]
    )
    def post(self, request):
        serializer = OptionsSerializer(data=request.query_params, option_type='officetel')
        if serializer.is_valid():
            validated_data = serializer.validated_data
            messages = []
            if validated_data.get('parkingNumRangeMin') is not None:
                parking_choices = {0: "0개", 1: "1대 이상", 2: "2대 이상"}
                messages.append(f"가능한 주차 대수는 {parking_choices[validated_data.get('parkingNumRangeMin')]}입니다.")
            if validated_data.get('roomCount') is not None:
                room_choices = {0: "0개", 1: "1개", 2: "2개", 3: "3개", 4: "4개 이상"}
                messages.append(f"방 개수는 {room_choices[validated_data.get('roomCount')]}입니다.")
            if validated_data.get('hasElevator'):
                messages.append("엘리베이터가 있는 매물만 보여드립니다.")
            if validated_data.get('isShortLease'):
                messages.append("단기임대 매물만 보여드립니다.")
            if validated_data.get('canParking'):
                messages.append("주차가 가능한 매물만 보여드립니다.")
            if messages:
                return Response({"messages": messages}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "선택된 옵션이 없습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OneTwoView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('canParking', openapi.IN_QUERY, description="주차 가능 여부", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('hasElevator', openapi.IN_QUERY, description="엘리베이터 유무", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('isShortLease', openapi.IN_QUERY, description="단기임대", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('isDivision', openapi.IN_QUERY, description="분리형", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('isDuplex', openapi.IN_QUERY, description="복층", type=openapi.TYPE_BOOLEAN, required=False),
        ]
    )
    def post(self, request):
        serializer = OptionsSerializer(data=request.query_params, option_type='onetwo')
        if serializer.is_valid():
            validated_data = serializer.validated_data
            messages = []
            if validated_data.get('hasElevator'):
                messages.append("엘리베이터가 있는 매물만 보여드립니다.")
            if validated_data.get('isShortLease'):
                messages.append("단기임대 매물만 보여드립니다.")
            if validated_data.get('canParking'):
                messages.append("주차가 가능한 매물만 보여드립니다.")
            if validated_data.get('isDivision'):
                messages.append("분리형 매물만 보여드립니다.")
            if validated_data.get('isDuplex'):
                messages.append("복층 매물만 보여드립니다.")
            if messages:
                return Response({"messages": messages}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "선택된 옵션이 없습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HouseView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('roomCount', openapi.IN_QUERY, description="방 개수 설정", type=openapi.TYPE_INTEGER, enum=[0, 1, 2, 3, 4], required=False),
            openapi.Parameter('canParking', openapi.IN_QUERY, description="주차 가능 여부", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('hasElevator', openapi.IN_QUERY, description="엘리베이터 유무", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('isShortLease', openapi.IN_QUERY, description="단기임대", type=openapi.TYPE_BOOLEAN, required=False),
        ]
    )
    def post(self, request):
        serializer = OptionsSerializer(data=request.query_params, option_type='house')
        if serializer.is_valid():
            validated_data = serializer.validated_data
            messages = []
            if validated_data.get('roomCount') is not None:
                room_choices = {0: "0개", 1: "1개", 2: "2개", 3: "3개", 4: "4개 이상"}
                messages.append(f"방 개수는 {room_choices[validated_data.get('roomCount')]}")