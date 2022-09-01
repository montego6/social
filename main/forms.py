from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from .models import Profile, Post, Comment, Message


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, help_text='Ваше имя')
    email = forms.EmailField(max_length=254, help_text='Адрес вашей электронной почты')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2',)


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'city', 'birthday', 'bio']


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'text']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'image']
