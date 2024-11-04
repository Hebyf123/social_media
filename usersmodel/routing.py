from django.urls import re_path,path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/(?P<user_id>\d+)/$', consumers.NotificationConsumer.as_asgi()),
    path("ws/chat/<int:chat_id>/", consumers.ChatConsumer.as_asgi()),
    path('ws/chat/<int:chat_id>/<uuid:invite_link>/', consumers.ChatConsumer.as_asgi()),

]