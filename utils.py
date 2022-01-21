from dataclasses import dataclass

from asgiref.sync import sync_to_async
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
import logging

# Create your views here.
from .forms import RoomForm
from .models import Room, CustomUser

@dataclass
class ChatMixin(object):
    chat_room_name: str

    template_name = 'chat/room.html'

    def get_chat_room(self):
        return Room.objects.get(room_name__iexact=self.chat_room_name)

    def get_message(self, id):
        return self.get_chat_room().message_set.get(id=id)

    def get_members_list(self):
        return self.get_chat_room().members.filter(is_blocked=False)

class WebsocketChatMixin(object):
    """Mixin for Websocket Consumer, just replaced some extra methods to this class"""

    @sync_to_async
    def get_user_credentials(self, session_items):
        session_list_data = [{x[0]: x[1]} for x in session_items]
        merged_data = {}
        response_data = {}
        data_keys = ['login', 'password']

        for dictionary in session_list_data:
            merged_data.update(**dictionary)

        #getting specific data from merged_data
        for key in data_keys:
            if key in merged_data.keys():
                response_data[key] = merged_data[key]

        return response_data




