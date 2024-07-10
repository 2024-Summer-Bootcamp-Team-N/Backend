from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer
from drf_yasg.utils import swagger_auto_schema, logger
from drf_yasg import openapi
import logging


class SignupView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="User sign up",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User created successfully",
                schema=UserSerializer
            ),
            400: "Invalid input"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)  # 시리얼라이저 인스턴스 생성
        serializer.is_valid(raise_exception=True)  # 데이터 유효성 검사
        user = serializer.save()  # 새로운 사용자 객체 생성 및 저장

        # 커스터마이즈된 응답 생성
        response_data = {
            'message': '회원가입이 완료되었습니다',
            '이름': user.name,
            'ID': user.auth_id,
            'pk': user.id,

        }

        return Response(response_data, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="User login",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "access_token": "string",
                        "refresh_token": "string"
                    }
                }
            ),
            401: "Invalid credentials"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            auth_id=serializer.validated_data['auth_id'],
            password=serializer.validated_data['password']
        )
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    @swagger_auto_schema(
        operation_description="User logout",
        # request_body=LogoutSerializer,
        responses={
            205: "Logout successful",
            400: "Invalid refresh token"
        }
    )
    def delete(self, request, *args, **kwargs):
        try:
            user = request.user
            logger.info(f"Logout attempt by user: {user.auth_id}")
            # 현재 사용자에 대한 모든 Refresh Token을 블랙리스트 처리
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                    logger.info(f"Refresh token blacklisted for user: {user.auth_id}")
                except Exception as e:
                    logger.error(f"Token blacklist failed: {str(e)}")
                    return Response({'error': 'Token blacklist failed'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.info(f"No refresh token provided for user: {user.auth_id}")

            logger.info(f"User {user.auth_id} logged out successfully.")
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return Response({'error': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)