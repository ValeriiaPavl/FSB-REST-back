import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed


class JWTAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        authorization_header = request.META.get('HTTP_AUTHORIZATION')

        if not authorization_header:
            return None
        user_model = get_user_model()  # Define user_model here

        try:
            token_type, token = authorization_header.split()
            if token_type.lower() != 'bearer':
                return None

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            user = user_model.objects.get(pk=user_id)
            return user, None
        except (ValueError, jwt.ExpiredSignatureError, jwt.DecodeError, user_model.DoesNotExist):
            raise AuthenticationFailed('Authentication failed')

    def authenticate_header(self, request):
        return 'Bearer'
