import channels
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import *
from django.core.asgi import get_asgi_application
import channels

from django.urls import path

from . import consumers

websocket_urlpatterns = [

    path('get/chat/room/<str:room_name>/', consumers.GroupChatConsumer.as_asgi()),

]

application = ProtocolTypeRouter({

    "http": AsgiHandler(),

    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(

        URLRouter(websocket_urlpatterns)

    ),
)

})
