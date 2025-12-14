"""
ASGI config for ufrnia project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import chat.routing

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from whitenoise import WhiteNoise
from chat.middlewares import TokenAuthMiddleware


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ufrnia.settings')

# django_asgi_app = WhiteNoise(get_asgi_application(), root='static')

# application = get_asgi_application()
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    # 'websocket': AuthMiddlewareStack(
    #     URLRouter(chat.routing.websocket_urlpatterns)
    # )
    'websocket': TokenAuthMiddleware(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})