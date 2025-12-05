from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken

from .models import User

class SimpleJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            access = AccessToken(token)
            user_id = access["user_id"]

            user = User.objects(id=user_id).first()
            if not user:
                raise AuthenticationFailed("Usuário não encontrado")

            return (user, None)
        except Exception:
            raise AuthenticationFailed("Token inválido ou expirado")
