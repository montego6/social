from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    avatar = models.ImageField(upload_to='media/avatars')
    city = models.CharField(max_length=100, null=True)
    birthday = models.DateField(null=True)
    bio = models.CharField(max_length=500, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
