from urllib.parse import parse_qs
from channels.db import database_sync_to_async

@database_sync_to_async
def get_user_from_token(token_key):
    from rest_framework.authtoken.models import Token
    from django.contrib.auth.models import AnonymousUser
    try:
        token = Token.objects.select_related('user').get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    """
    Middleware que autentica WebSocket usando Token DRF (?token=...)
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser
        scope['user'] = AnonymousUser()
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token_key = query_params.get('token', [None])[0]
        if token_key:
            scope['user'] = await get_user_from_token(token_key)
        return await self.app(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)
