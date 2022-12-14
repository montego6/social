from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import re

# Create your models here.


class Profile(models.Model):
    avatar = models.ImageField(upload_to='media/avatars/', null=True, blank=True)
    city = models.CharField(max_length=100, null=True)
    birthday = models.DateField(null=True)
    bio = models.TextField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    following = models.ManyToManyField('self', related_name='followers', symmetrical=False)


class Post(models.Model):
    image = models.ImageField(upload_to='media/posts', null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    like = models.ManyToManyField(User, related_name='likes')

    def save(self, *args, **kwargs):
        hashtags = re.findall(r'#(\w+)', self.text)
        for hashtag in hashtags:
            full_hashtag = '#' + hashtag
            link = reverse('hashtag', kwargs={'hashtag': hashtag})
            self.text = self.text.replace(full_hashtag, f'<a href="{link}">{full_hashtag}</a>')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return self.text


class Notification(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_from')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_to')
    action = models.CharField(max_length=20)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='notifications', null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='notifications', null=True)


class Chat(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_sender')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_receiver')
    user_unread_messages = models.ForeignKey(User, on_delete=models.CASCADE,
                                             related_name='unread_chats', null=True, default=None)

    def __str__(self):
        return f'{self.user1.username} - {self.user2.username}'


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_from')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_to')
    text = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='media/chats', null=True, blank=True)
    is_read = models.BooleanField(default=False)

