from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    avatar = models.ImageField(upload_to='media/avatars/', null=True, blank=True)
    city = models.CharField(max_length=100, null=True)
    birthday = models.DateField(null=True)
    bio = models.TextField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
