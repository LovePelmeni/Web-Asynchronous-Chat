import json

import requests
from channels.db import database_sync_to_async
from channels.routing import *

from asgiref.sync import sync_to_async
from channels.exceptions import DenyConnection

from channels.generic.http import AsyncHttpConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django import dispatch

from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.urls import reverse

from . import utils
from .models import CustomUser, Room
from .views import logger

user_joined = dispatch.Signal()

class GroupChatConsumer(AsyncWebsocketConsumer, utils.WebsocketChatMixin):
    """This is async consumer to process websocket connections from chat_rooms"""

    @sync_to_async
    def get_group_name(self):
        return 'group_%s' % str(self.chat_name.replace(' ', '_'))

    @sync_to_async
    def send_add_signal(self):
        return user_joined.send(sender=self.websocket_connect, instance=self.user,
        joined=True, room_name=self.chat_name)

    async def connect(self):
        """Default connection websocket method. Accepts user if passed requirements"""

        self.chat_name = self.scope['url_route']['kwargs']['room_name']
        self.group_name = await self.get_group_name()
        self.c_code = 4444

        self.user = self.scope.get('user')
        try:
            user = await sync_to_async(CustomUser.objects.get)(username=self.user.username)
            if not user.is_authenticated:
                await self.close(code=self.c_code)

        except ObjectDoesNotExist:
            raise DenyConnection('user does not exist')

        await self.channel_layer.group_add(self.group_name,
            self.channel_name
    )
        await self.accept()
        await self.send_add_signal()

        logger.debug('User is connected' % user.username)

    @sync_to_async
    def check_user_auth_perms(self, user: CustomUser):
        """Method checks for user authentication and for blocking status..."""
        if not user.is_authenticated or user.is_blocked:
            raise DenyConnection('Got not enough perms... This user is blocked or non-authenticated')

    async def receive(self, text_data=None, bytes_data=None):
        """This method receives json info from front-end
        and returns it to other channels in the group"""

        if text_data is not None:
            loaded_data = json.loads(text_data)

            msg = loaded_data['data'].get('message')
            username = loaded_data['data'].get('username')

            user = await sync_to_async(CustomUser.objects.get)(username=username)
            await self.check_user_auth_perms(user)

            response = {
                'message': msg,
                'author': username,
            }
            await self.channel_layer.group_send(
                self.group_name,
                {'type': 'send_message', 'data': response}
            )

    async def send_message(self, event):
        """This method sending info back to front-end part..."""
        await self.send(json.dumps({'type': 'websocket.send',
        'data': event['data']}))

        logger.debug('data has been sended...')

    @sync_to_async
    def leave_group(self):
        """This method deleting user from the group"""
        room = Room.objects.get(room_name=self.chat_name)
        members_list = [member for member in room.members.filter(is_blocked=False)]

        if self.user in members_list:
            Room.objects.get(room_name=self.chat_name).members.remove(self.user)

    async def disconnect(self, close_code):
        await self.leave_group() # awaiting for removing user from the room...

        await self.channel_layer.group_discard( # then removing user's channel from websocket group...
            self.group_name,
            self.channel_name
        )
        logger.debug('disconnected', close_code)
