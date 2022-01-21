import json
from dataclasses import dataclass
from io import StringIO

from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models import Value
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
import logging

# Create your views here.
from django.template.context_processors import csrf
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin

from . import utils, forms
from .forms import RoomForm
from .models import Room, CustomUser, Message, Token

logger = logging.getLogger(__name__)


@login_required
def get_chat_room_form(request):
    template_name = 'chat/create_room.html'
    return render(request, template_name, context={'form': forms.CreateRoomForm()})

@require_POST
def create_chat(request):
    """Just a simple function creating new chat..."""
    form = forms.CreateRoomForm(request.POST)
    try:
        if form.is_valid():
            new_chat = Room.objects.create(room_name=form.cleaned_data['room_name'])

            for user in form.cleaned_data['members']:
                new_chat.members.add(user)

            logger.debug('new room was created: %s' % new_chat.room_name)
            return HttpResponseRedirect(reverse('chat:get_chat_room', kwargs={'room_name': new_chat.room_name}))

    except ValidationError:
        return HttpResponse(form.errors)

class HomePage(View):
    """Home Page Class-Based-View"""
    template_name = 'chat/index.html'

    def get(self, request):
        rooms = Room.objects.all()
        return render(request, self.template_name, {'rooms': rooms})

def process_room_kwargs(request, **kwargs):
    """This method returns a room name kwarg depends on request..."""
    chat_name = kwargs.get('room_name')

    if request.method == 'GET':
        return ChatRoom(chat_room_name=chat_name).get(request)

    elif request.method == 'POST':
        return ChatRoom(chat_room_name=chat_name).post(request)

class ChatRoom(utils.ChatMixin, FormMixin, View):
    """This is CBV implemented for processing messages in the room"""
    def __init__(self, chat_room_name=None):
        super().__init__(chat_room_name)

        self.context = {}
        self.success_url = './'

    @staticmethod
    def generate_token():
        from uuid import uuid4
        return uuid4()

    def update_with_token(self, user):
        token = Token.objects.create(user_connection=user, code=self.generate_token().hex).code.hex
        logger.debug('new token was generated...')
        return json.dumps(token)

    def prepare_request_data(self, user, room_name):
        """Just a func forming context..."""
        room_data = {
            'username': user.username,
            'room_name': room_name
        }
        return room_data

    def prepare_context(self, request, kwargs=None):

        self.context['banner'] = '%s' % self.chat_room_name
        self.context['members'] = self.get_members_list()
        self.context['username'] = request.user.username

        self.context['room'] = self.get_chat_room()
        self.context['form'] = forms.MessageForm()

        self.context.update(**self.prepare_request_data(user=request.user, room_name=self.get_chat_room().room_name))
        self.context.update({'websocket_token': kwargs.get('websocket_token')})

        return self.context

    def get(self, request):
        """room page, where is the main web-socket """
        self.context.update(csrf(request))
        user = auth.get_user(request)

        model_user = CustomUser.objects.get(username=user.username)
        if user.is_authenticated:
            try:
                token = json.dumps(Token.objects.get(user_connection=model_user).code.hex)

            except ObjectDoesNotExist:
                token = self.update_with_token(user=model_user)
            context = self.prepare_context(request, kwargs={'websocket_token': token})

            return render(request, self.template_name, {**context})

    def post(self, request):
        """Processing message for and redirects back to room page..."""
        user = auth.get_user(request)
        form = forms.MessageForm(request.POST)

        if form.is_valid():
            author = CustomUser.objects.get(username=user.username)
            Message.objects.create(**form.cleaned_data, author=author,

            chat=Room.objects.get(room_name=self.chat_room_name)
            )
            logger.debug('new message was created')

            return super().form_valid(form)
