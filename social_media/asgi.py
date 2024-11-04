import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.layers import get_channel_layer
import usersmodel.routing
from usersmodel.middleware import JWTAuthMiddleware
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': JWTAuthMiddleware(
        URLRouter(
            usersmodel.routing.websocket_urlpatterns
        )
    ),
})
#пример как добавить два роутера
# URLRouter(
#            # Объединяем маршруты из разных приложений
#            usermodel.routing.websocket_urlpatterns +
#            chat.routing.websocket_urlpatterns
#        )
