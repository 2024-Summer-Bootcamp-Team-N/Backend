from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import RegionSerializer, ResidenceSerializer, TypeSerializer
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
            openapi.Parameter('apartment', openapi.IN_QUERY, description="아파트/오피스텔 선택", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('villa', openapi.IN_QUERY, description="주택/빌라 선택", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('room', openapi.IN_QUERY, description="원룸/투룸 선택", type=openapi.TYPE_BOOLEAN, required=False),
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
            openapi.Parameter('yearly', openapi.IN_QUERY, description="전세 선택", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('monthly', openapi.IN_QUERY, description="월세 선택", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('yearly_fee', openapi.IN_QUERY, description="전세 금액 입력", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('deposit', openapi.IN_QUERY, description="보증금 입력", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('monthly_fee', openapi.IN_QUERY, description="월세 금액 입력", type=openapi.TYPE_STRING, required=False),
        ],
        responses={200: '성공적으로 처리되었습니다.', 400: '잘못된 요청입니다.'}
    )
    def post(self, request):
        serializer = TypeSerializer(data=request.query_params)
        if serializer.is_valid():
            yearly = serializer.validated_data.get('yearly')
            monthly = serializer.validated_data.get('monthly')
            yearly_fee = serializer.validated_data.get('yearly_fee')
            deposit = serializer.validated_data.get('deposit')
            monthly_fee = serializer.validated_data.get('monthly_fee')

            if yearly and monthly:
                return Response({"message": "하나만 선택해주세요!"}, status=status.HTTP_400_BAD_REQUEST)
            if yearly:
                if not yearly_fee:
                    return Response({"message": "희망 전세금을 입력해주세요!"}, status=status.HTTP_400_BAD_REQUEST)
                return Response({
                    "message": f"입력한 전세 정보입니다. 희망하신 전세금은 '{yearly_fee}'입니다.",
                    "data": {
                        "yearly": yearly,
                        "yearly_fee": yearly_fee
                    }
                }, status=status.HTTP_200_OK)
            if monthly:
                if not (deposit and monthly_fee):
                    return Response({"message": "보증금과 월세를 입력해주세요!"}, status=status.HTTP_400_BAD_REQUEST)
                return Response({
                    "message": f"입력한 월세 정보입니다. 희망하신 보증금은 '{deposit}', 월세는 '{monthly_fee}'입니다.",
                    "data": {
                        "monthly": monthly,
                        "deposit": deposit,
                        "monthly_fee": monthly_fee
                    }
                }, status=status.HTTP_200_OK)
            return Response({"message": "하나만 선택해주세요!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class optionView(APIView):


