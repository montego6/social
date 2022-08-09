from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    avatar = models.ImageField(upload_to='media/avatars/', null=True, blank=True)
    city = models.CharField(max_length=100, null=True)
    birthday = models.DateField(null=True)
    bio = models.TextField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')


class Post(models.Model):
    image = models.ImageField(upload_to='media/posts', null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    like = models.ManyToManyField(User, related_name='likes')
