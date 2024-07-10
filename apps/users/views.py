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
            'id': user.id,

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
                        "refresh_token": "string",
                        "access_token": "string"
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
                'refresh_token': str(refresh),
                'access_token': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="User logout",
        responses={
            205: "Logout successful",
            400: "Invalid refresh token"
        }
    )
    def delete(self, request, *args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return Response({'error': 'Refresh token not provided'}, status=status.HTTP_400_BAD_REQUEST)

            refresh_token = auth_header.strip()  # JWT 접두사 제거
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)
