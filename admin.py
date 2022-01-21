from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin

from .models import *


class UserAdmin(ModelAdmin):
    model = CustomUser
    list_display = ['username', 'password', 'email', 'is_blocked', 'is_admin', 'is_superuser']
    fields = ['username', 'password', 'email', 'is_blocked', 'is_admin', 'is_superuser']

admin.site.register(CustomUser, UserAdmin)

class RoomAdmin(ModelAdmin):
    model = Room
    list_display = ['room_name']
    fields = ['room_name']


admin.site.register(Room, RoomAdmin)

class MessageAdmin(ModelAdmin):
    model = Message
    list_display = ['author', 'text', 'chat']
    fields = ['author', 'text', 'chat']


admin.site.register(Message, MessageAdmin)


admin.site.register(Token)