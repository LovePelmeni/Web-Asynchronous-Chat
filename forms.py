from django import forms
from django.core.exceptions import ValidationError

from .models import *


class RoomForm(forms.ModelForm):

    room_title = forms.CharField(label='Room Title', widget=forms.TextInput, required=True)
    members = forms.ModelMultipleChoiceField(label='choose users', queryset=CustomUser.objects.all(),  required=True)

    class Meta:
        model = Room
        fields = ['room_name', 'members']

class MessageForm(forms.ModelForm):
    text = forms.CharField(label='Message', widget=forms.TextInput, required=True)

    class Meta:
        model = Message
        fields = ['text']

class AuthForm(forms.ModelForm):

    username = forms.CharField(label='login', required=True)
    password = forms.CharField(label='password', required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

class CreateRoomForm(forms.ModelForm):

    room_name = forms.CharField(label='room name', widget=forms.TextInput, required=True)

    members = forms.ModelMultipleChoiceField(label='members', widget=forms.CheckboxSelectMultiple,
    queryset=CustomUser.objects.all(), required=False)

    class Meta:
        model = Room
        fields = ['room_name', 'members']

    def clean_room_name(self):
        rooms_name_list = [room.room_name for room in Room.objects.all()]
        if self.cleaned_data['room_name'] in rooms_name_list:
            raise ValidationError('there is already such name')

        return self.cleaned_data['room_name']






