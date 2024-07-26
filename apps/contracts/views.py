import boto3
import uuid
import botocore
import mimetypes
import re
import os
import io
import base64
import datetime
import pytz

from django.utils import timezone
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from ..options.models import RoomInfo, RoomDetailInfo
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO

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
            refresh_token = request.headers.get('Authorization', '')

            # 리프레시 토큰을 사용하여 OutstandingToken 객체 가져오기
            token = OutstandingToken.objects.get(token=refresh_token)

            # OutstandingToken의 user_id를 사용하여 User 객체 가져오기
            user = User.objects.get(id=token.user_id)

            result = {
                "location": latest_room_detail.location,
                "exclusive_overall_area": latest_room_detail.exclusive_overall_area,
                "building_use": latest_room_detail.building_use,
                "latest_user_name": user.name,  # User 모델의 name 필드 사용
                "deposit": deposit,
                "monthly_rent": monthly_rent,
            }
            return Response(result, status=status.HTTP_200_OK)
        except OutstandingToken.DoesNotExist:
            return Response({"error": "유효하지 않은 리프레시 토큰입니다."}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


#계약서 이미지 s3에 업로드
class S3ImageUploadView(APIView):
    parser_classes = (JSONParser,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.s3 = boto3.client('s3',
                               aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    @swagger_auto_schema(
        operation_description="Upload an image to S3 (image data in request body)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'image_data': openapi.Schema(type=openapi.TYPE_STRING, description='Image data (base64 encoded)'),
                'file_name': openapi.Schema(type=openapi.TYPE_STRING, description='Original file name'),
                'content_type': openapi.Schema(type=openapi.TYPE_STRING, description='MIME type of the image')
            },
            required=['image_data', 'file_name', 'content_type']
        ),
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
            404: 'Not Found',
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        try:
            image_data = request.data.get('image_data')
            file_name = request.data.get('file_name')
            content_type = request.data.get('content_type')

            if not all([image_data, file_name, content_type]):
                return Response({'error': '이미지 데이터, 파일 이름, 콘텐츠 타입이 모두 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

            # Base64 디코딩
            image_data = base64.b64decode(image_data)

            # 파일 크기 검증 (예: 10MB 제한)
            if len(image_data) > 10 * 1024 * 1024:
                return Response({'error': '파일 크기가 10MB를 초과합니다.'}, status=status.HTTP_400_BAD_REQUEST)

            # 파일 타입 검증
            allowed_mime_types = ['image/jpeg', 'image/png']
            if content_type not in allowed_mime_types:
                return Response({'error': '유효하지 않은 파일 형식입니다.'}, status=status.HTTP_400_BAD_REQUEST)

            refresh_token = request.headers.get('Authorization', '')

            if not refresh_token:
                return Response({"error": "리프레시 토큰이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # 리프레시 토큰을 사용하여 사용자 정보 가져오기 (OutstandingToken 모델 활용)
                token = OutstandingToken.objects.get(token=refresh_token)
                user_id = token.user_id

            except OutstandingToken.DoesNotExist:
                return Response({"error": "유효하지 않은 리프레시 토큰입니다."}, status=status.HTTP_401_UNAUTHORIZED)

            # 현재 시간 기반으로 고유한 파일 이름 생성
            timestamp = timezone.now().strftime("%Y%m%d-%H%M%S")
            file_name = f"images/{user_id}_contract_{timestamp}"

            # 파일 확장자 추가
            file_extension = mimetypes.guess_extension(content_type)
            file_name += file_extension

            # S3에 파일 업로드
            self.s3.upload_fileobj(
                io.BytesIO(image_data),
                settings.AWS_STORAGE_BUCKET_NAME,
                file_name,
                ExtraArgs={'ContentType': content_type}
            )

            # 이미지 URL 생성
            image_url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': file_name},
                ExpiresIn=3600
            )

            return Response({'image_url': image_url}, status=status.HTTP_201_CREATED)

        except boto3.exceptions.S3UploadFailedError as e:
            return Response({'error': 'S3 업로드에 실패했습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class S3ImageListView(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="S3 이미지 URL 목록 (createdDate 포함)",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description="파일 이름 (확장자 제외)"),
                            'url': openapi.Schema(type=openapi.TYPE_STRING, description="Presigned 이미지 URL"),
                            'createdDate': openapi.Schema(type=openapi.TYPE_STRING, description="생성 날짜 및 시간 (KST, 9시간 추가)", format='date-time')
                        }
                    )
                )
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="이미지 또는 사용자 정보를 찾을 수 없음"
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="이미지 가져오는 중 오류 발생"
            )
        }
    )
    def get(self, request):
        # 사용자에게서 리프레시 토큰을 받음
        refresh_token = request.headers.get('Authorization', '')

        if not refresh_token:
            return Response({"error": "리프레시 토큰이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 리프레시 토큰을 사용하여 사용자 정보 가져오기 (OutstandingToken 모델 활용)
            token = OutstandingToken.objects.get(token=refresh_token)
            user_id = token.user_id

        except OutstandingToken.DoesNotExist:
            return Response({"error": "유효하지 않은 리프레시 토큰입니다."}, status=status.HTTP_401_UNAUTHORIZED)

        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

        try:
            prefix = f"images/{user_id}_contract"
            response = s3.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix=prefix)

            image_data = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        presigned_url = s3.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': obj['Key']},
                            ExpiresIn=3600  # 1시간 동안 유효
                        )
                        image_name = os.path.splitext(os.path.basename(obj['Key']))[0]  # 파일 이름만 추출

                        # 파일 이름에서 날짜 및 시간 추출
                        try:
                            date_time_str = image_name.split('_')[-1]  # 마지막 부분 추출
                            date_time_obj = datetime.datetime.strptime(date_time_str, "%Y%m%d-%H%M%S")

                            # KST 타임존 설정
                            kst = pytz.timezone('Asia/Seoul')
                            date_time_obj = kst.localize(date_time_obj)

                            # 9시간 더하기
                            date_time_obj += datetime.timedelta(hours=9)

                            # createdDate 형식으로 변환
                            created_date = date_time_obj.strftime("%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            created_date = None  # 파싱 실패 시 None으로 설정

                        image_data.append({
                            'name': image_name,
                            'url': presigned_url,
                            'createdDate': created_date
                        })

            else:
                return Response({"error": "해당 사용자의 이미지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            return Response(image_data, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = {"error": f"S3 이미지를 가져오는 중 오류 발생: {str(e)}"}
            return Response(error_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
