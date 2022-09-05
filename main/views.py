from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse
from django.db.models import Q

from .forms import SignUpForm, ProfileForm, PostForm, CommentForm, MessageForm
from .models import Profile, Post, Notification, Comment, Chat, Message
from django.contrib.auth.models import User


# Create your views here.


def unread_messages_template(request):
    if not request.user.is_anonymous:
        unread_messages_count = Message.objects.filter(to_user=request.user, is_read=False).count()
    else:
        unread_messages_count = 0
    return {"unread_messages": unread_messages_count}


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def profile_my(request):
    user = User.objects.select_related('profile').prefetch_related('posts__like').get(id=request.user.id)
    return render(request, 'profile_my.html', {'user': user})


@login_required
def add_profile_bio(request):
    if request.user.profile:
        return redirect('profile my')
    if request.method == 'POST':
        form = ProfileForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect('profile my')
    else:
        form = ProfileForm()
    return render(request, 'form.html', {'form': form, 'title': 'Добавить био'})


class ProfileUpdateView(UserPassesTestMixin, UpdateView):
    model = Profile
    fields = ['avatar', 'city', 'birthday', 'bio']
    template_name_suffix = '_update'
    queryset = Profile.objects.select_related('user')

    def get_success_url(self):
        return reverse("profile my")

    def test_func(self):
        user_profile = self.get_object()
        return self.request.user == user_profile.user


@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user
            post.save()
            return redirect('profile my')
    else:
        form = PostForm()
    return render(request, 'form.html', {'form': form, 'title': 'Добавить пост'})


@login_required
def detail_post(request, post_id):
    post = get_object_or_404(Post.objects.prefetch_related('like').select_related('owner'). \
                             select_related('owner__profile'), id=post_id)
    comments = Comment.objects.select_related('owner').select_related('post'). \
        select_related('owner__profile').filter(post=post)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.owner = request.user
            comment.save()
            Notification.objects.create(
                from_user=request.user,
                to_user=post.owner,
                action='comment',
                comment=comment
            )
    else:
        form = CommentForm()
    return render(request, 'post_detail.html', {'post': post, 'form': form, 'comments': comments})


class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    queryset = Post.objects.select_related('owner')

    def get_success_url(self):
        return reverse("profile my")

    def test_func(self):
        delete_post = self.get_object()
        return self.request.user == delete_post.owner


class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['image', 'text']
    template_name_suffix = '_update'
    queryset = Post.objects.select_related('owner')

    def get_success_url(self):
        return reverse("profile my")

    def test_func(self):
        update_post = self.get_object()
        return self.request.user == update_post.owner


@login_required
def like_post(request, pk):
    post = Post.objects.select_related('owner').get(id=pk)
    if request.user in post.like.all():
        post.like.remove(request.user)
        Notification.objects.create(
            from_user=request.user,
            to_user=post.owner,
            action='dislike',
            post=post
        )
    else:
        post.like.add(request.user)
        Notification.objects.create(
            from_user=request.user,
            to_user=post.owner,
            action='like',
            post=post
        )
    return redirect(request.META.get('HTTP_REFERER', 'profile my'))


@login_required
def search(request):
    search_query = request.POST["search_input"]
    users = User.objects.select_related('profile').prefetch_related('posts').filter(username__icontains=search_query)
    posts = Post.objects.prefetch_related('like').select_related('owner'). \
        select_related('owner__profile').filter(text__icontains=search_query)
    return render(request, 'search.html', {'users': users, 'posts': posts})


@login_required
def follow(request, profile_id):
    following_profile = Profile.objects.get(id=profile_id)
    if following_profile not in request.user.profile.following.all():
        request.user.profile.following.add(following_profile)
        Notification.objects.create(
            from_user=request.user,
            to_user=following_profile.user,
            action='follow'
        )
    else:
        request.user.profile.following.remove(following_profile)
        Notification.objects.create(
            from_user=request.user,
            to_user=following_profile.user,
            action='disfollow'
        )
    return redirect("profile", profile_id=profile_id)


@login_required
def profile(request, profile_id):
    user_profile = get_object_or_404(Profile.objects.select_related('user').prefetch_related('following'),
                                     id=profile_id)
    if user_profile == request.user.profile:
        return redirect('profile my')
    posts = Post.objects.select_related('owner__profile').select_related('owner'). \
        prefetch_related('like').filter(owner=user_profile.user)
    return render(request, 'profile.html', {'profile': user_profile, 'posts': posts})


@login_required
def feed(request):
    posts = Post.objects.select_related('owner').select_related('owner__profile') \
        .prefetch_related('like') \
        .filter(owner__profile__followers=request.user.profile)
    return render(request, 'feed.html', {'posts': posts})


@login_required
def followers(request, profile_id):
    user_profile = get_object_or_404(Profile.objects.select_related('user').prefetch_related('followers__user'). \
                                     prefetch_related('followers__user__posts'), id=profile_id)
    user_followers = user_profile.followers.all()
    return render(request, 'followers.html', {'profile': user_profile, 'followers': user_followers})


@login_required
def following(request, profile_id):
    user_profile = get_object_or_404(Profile.objects.select_related('user'). \
                                     prefetch_related('following').prefetch_related('following__user'). \
                                     prefetch_related('following__user__posts'), id=profile_id)
    user_following = user_profile.following.all()
    return render(request, 'following.html', {'profile': user_profile, 'following': user_following})


@login_required
def notifications_view(request):
    notifications = Notification.objects.select_related('from_user').select_related('to_user'). \
                        select_related('to_user__profile').select_related('from_user__profile').select_related('post'). \
                        select_related('comment').select_related('comment__post'). \
                        filter(Q(from_user=request.user) | Q(to_user=request.user)).order_by('-id')[:20]
    return render(request, 'notifications.html', {'notifications': notifications})


@login_required
def hashtag_search(request, hashtag):
    posts = Post.objects.select_related('owner').select_related('owner__profile'). \
        prefetch_related('like').filter(text__icontains='#' + hashtag)
    return render(request, 'search.html', {'users': None, 'posts': posts})


class CommentDeleteView(UserPassesTestMixin, DeleteView):
    model = Comment
    queryset = Comment.objects.select_related('owner').select_related('post')

    def get_success_url(self):
        post_id = self.object.post.id
        return reverse("post detail", kwargs={"post_id": post_id})

    def test_func(self):
        delete_comment = self.get_object()
        return self.request.user == delete_comment.owner


@login_required
def send_message(request, receiver_id):
    user1 = request.user
    user2 = User.objects.get(id=receiver_id)
    try:
        chat = Chat.objects.get(Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1))
    except Chat.DoesNotExist:
        chat = Chat.objects.create(user1=user1, user2=user2)
    return redirect('chat', chat_id=chat.id)


@login_required
def message_chat(request, chat_id):
    chat = get_object_or_404(Chat.objects.select_related('user1').select_related('user2'). \
                             select_related('user_unread_messages'), id=chat_id)
    if request.user != chat.user1 and request.user != chat.user2:
        return HttpResponseForbidden()
    recipient = chat.user2 if request.user == chat.user1 else chat.user1
    messages = chat.messages.order_by("-id").select_related('from_user')
    unread_messages = chat.messages.filter(is_read=False)
    if unread_messages.exists():
        to_user = unread_messages[0].to_user
        if to_user == request.user:
            unread_messages.update(is_read=True)
            chat.user_unread_messages = None
            chat.save()
    if request.method == 'POST':
        form = MessageForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.from_user = request.user
            message.to_user = chat.user2 if chat.user1 == request.user else chat.user1
            message.save()
            chat.user_unread_messages = message.to_user
            chat.save()
            return redirect('chat', chat_id=chat.id)
    else:
        form = MessageForm()
    return render(request, 'chat.html', {'messages': messages, 'form': form, 'recipient': recipient})


@login_required
def all_chats(request):
    unread_chats = Chat.objects.select_related('user1').select_related('user2'). \
        filter(user_unread_messages=request.user)
    read_chats = Chat.objects.select_related('user1').select_related('user2'). \
        filter(Q(user1=request.user) | Q(user2=request.user)) \
        .exclude(user_unread_messages=request.user)
    return render(request, 'chats.html', {'unread_chats': unread_chats, 'read_chats': read_chats})
