import boto3
from rest_framework.parsers import MultiPartParser, FormParser
import uuid
import re
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from ..options.models import RoomInfo, RoomDetailInfo
from django.contrib.auth import get_user_model

User = get_user_model()

#계약서 작성에 필요한 텍스트 호출
def parse_price(price_str):
    deposit = None
    monthly_rent = None
    if "전세" in price_str:
        match = re.search(r'전세\s*(\d+)억?\s*(\d+)?', price_str)
        if match:
            if match.group(2):
                deposit = f"{match.group(1)}억 {match.group(2)}만원"
            else:
                deposit = f"{match.group(1)}억원"
    elif "월세" in price_str:
        match = re.search(r'월세\s*(\d+)/(\d+)', price_str)
        if match:
            deposit = f"{match.group(1)}만원"
            monthly_rent = f"{match.group(2)}만원"
    return deposit, monthly_rent

class LatestRoomDetailInfoAPIView(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="최근 방 정보 및 최근 사용자 정보",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "location": openapi.Schema(type=openapi.TYPE_STRING, description="방 위치"),
                        "exclusive_overall_area": openapi.Schema(type=openapi.TYPE_STRING, description="전용면적"),
                        "building_use": openapi.Schema(type=openapi.TYPE_STRING, description="건물 용도"),
                        "latest_user_name": openapi.Schema(type=openapi.TYPE_STRING, description="최근 사용자 이름"),
                        "deposit": openapi.Schema(type=openapi.TYPE_STRING, description="보증금"),
                        "monthly_rent": openapi.Schema(type=openapi.TYPE_STRING, description="월세"),
                    }
                )
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="정보를 찾을 수 없음",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
                )
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="서버 오류 발생",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
                )
            )
        }
    )
    def get(self, request):
        try:
            # 가장 최근 방 정보 가져오기
            latest_room_detail = RoomDetailInfo.objects.order_by('-id').first()

            if not latest_room_detail:
                return Response({"error": "방 정보를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            # RoomInfo에서 price 정보 가져오기
            try:
                room_info = RoomInfo.objects.get(id=latest_room_detail.room_id)
                deposit, monthly_rent = parse_price(room_info.price)
            except RoomInfo.DoesNotExist:
                return Response({"error": "해당 방의 가격 정보를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            # 가장 최근 사용자 정보 가져오기
            latest_token = OutstandingToken.objects.order_by('-created_at').first()

            if not latest_token:
                return Response({"error": "최근 사용자 정보를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            try:
                latest_user = User.objects.get(id=latest_token.user_id)
            except User.DoesNotExist:
                return Response({"error": "해당 사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            result = {
                "location": latest_room_detail.location,
                "exclusive_overall_area": latest_room_detail.exclusive_overall_area,
                "building_use": latest_room_detail.building_use,
                "latest_user_name": latest_user.name,
                "deposit": deposit,
                "monthly_rent": monthly_rent,
            }
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#계약서 이미지 s3에 업로드
class S3ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.s3 = boto3.client('s3',
                               aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    @swagger_auto_schema(
        operation_description="Upload an image to S3",
        manual_parameters=[
            openapi.Parameter(
                name="image",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="Image file to upload"
            ),
        ],
        responses={
            201: openapi.Response(
                description="Created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'image_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the uploaded image'),
                    }
                )
            ),
            400: 'Bad Request',
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        try:
            if 'image' not in request.FILES:
                return Response({'error': 'Image file not provided'}, status=status.HTTP_400_BAD_REQUEST)

            image_file = request.FILES['image']

            # 파일 크기 검증 (예: 10MB 제한)
            if image_file.size > 10 * 1024 * 1024:
                return Response({'error': 'File size exceeds 10MB'}, status=status.HTTP_400_BAD_REQUEST)

            # 파일 타입 검증 (예: 이미지 파일만 허용)
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if image_file.content_type not in allowed_types:
                return Response({'error': 'Invalid file type'}, status=status.HTTP_400_BAD_REQUEST)

            # Generate a unique filename using UUID
            file_name = f"images/{uuid.uuid4().hex}_{image_file.name}"

            self.s3.upload_fileobj(image_file, settings.AWS_STORAGE_BUCKET_NAME, file_name)

            image_url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': file_name},
                ExpiresIn=3600)  # URL 유효 시간 (1시간)

            return Response({'image_url': image_url}, status=status.HTTP_201_CREATED)

        except boto3.exceptions.S3UploadFailedError as e:
            return Response({'error': 'Failed to upload image to S3'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class S3ImageListView(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="List of S3 image URLs",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'url': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="Error occurred while fetching images"
            )  # Simplified error response
        }
    )
    def get(self, request):
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

        try:
            paginator = s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=settings.AWS_STORAGE_BUCKET_NAME)

            image_data = []

            for page in pages:
                for obj in page.get('Contents', []):
                    if obj['Key'].endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        presigned_url = s3.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': obj['Key']},
                            ExpiresIn=3600  # 1 hour expiration
                        )

                        image_data.append({'name': obj['Key'], 'url': presigned_url})

            return Response(image_data, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = {"error": f"Error fetching S3 images: {str(e)}"}  # Include exception details
            return Response(error_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)