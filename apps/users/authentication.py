from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    def get_header(self, request):
        header = request.META.get('HTTP_AUTHORIZATION')
        if header is None:
            return None
        return header.encode('utf-8')

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

    def get_raw_token(self, header):
        # header에서 raw token 반환
        return header.strip()

    def get_validated_token(self, raw_token):
        try:
            return super().get_validated_token(raw_token)
        except InvalidToken:
            raise AuthenticationFailed('Invalid token')
