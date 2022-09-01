from django.contrib.auth import login, authenticate
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse
from django.db.models import Q

from .forms import SignUpForm, ProfileForm, PostForm, CommentForm, MessageForm
from .models import Profile, Post, Notification, Comment, Chat, Message
from django.contrib.auth.models import User

# Create your views here.


def home(request):
    return render(request, "home.html")


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


def profile_my(request):
    return render(request, 'profile_my.html')


def add_profile_bio(request):
    if request.method == 'POST':
        form = ProfileForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('profile my')
    else:
        form = ProfileForm()
    return render(request, 'form.html', {'form': form, 'title': 'Добавить био'})


class ProfileUpdateView(UpdateView):
    model = Profile
    fields = ['avatar', 'city', 'birthday', 'bio']
    template_name_suffix = '_update'

    def get_success_url(self):
        return reverse("profile my")


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


def detail_post(request, post_id):
    post = Post.objects.get(id=post_id)
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
    return render(request, 'post_detail.html', {'post': post, 'form': form})


class PostDeleteView(DeleteView):
    model = Post

    def get_success_url(self):
        return reverse("profile my")


class PostUpdateView(UpdateView):
    model = Post
    fields = ['image', 'text']
    template_name_suffix = '_update'

    def get_success_url(self):
        return reverse("profile my")


def like_post(request, pk):
    post = Post.objects.get(id=pk)
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
    return redirect(request.META.get('HTTP_REFERER', 'profile'))


def search(request):
    search_query = request.POST["search_input"]
    users = User.objects.filter(username__icontains=search_query)
    posts = Post.objects.filter(text__icontains=search_query)
    return render(request, 'search.html', {'users': users, 'posts': posts})


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


def profile(request, profile_id):
    user_profile = Profile.objects.get(id=profile_id)
    posts = Post.objects.filter(owner=user_profile.user)
    return render(request, 'profile.html', {'profile': user_profile, 'posts': posts})


def feed(request):
    posts = Post.objects.filter(owner__profile__followers=request.user.profile)
    return render(request, 'feed.html', {'posts': posts})


def followers(request, profile_id):
    user_profile = Profile.objects.get(id=profile_id)
    user_followers = user_profile.followers.all()
    return render(request, 'followers.html', {'profile': user_profile, 'followers': user_followers})


def following(request, profile_id):
    user_profile = Profile.objects.get(id=profile_id)
    user_following = user_profile.following.all()
    return render(request, 'following.html', {'profile': user_profile, 'following': user_following})


def notifications_view(request):
    notifications = Notification.objects.filter(Q(from_user=request.user) | Q(to_user=request.user)).order_by('-id')[:20]
    return render(request, 'notifications.html', {'notifications': notifications})


def hashtag_search(request, hashtag):
    posts = Post.objects.filter(text__icontains='#' + hashtag)
    return render(request, 'search.html', {'users': None, 'posts': posts})


class CommentDeleteView(DeleteView):
    model = Comment

    def get_success_url(self):
        post_id = self.object.post.id
        return reverse("post detail", kwargs={"post_id": post_id})


def send_message(request, receiver_id):
    user1 = request.user
    user2 = User.objects.get(id=receiver_id)
    chat = Chat.objects.get(Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1))
    if not chat:
        chat = Chat.objects.create(user1=user1, user2=user2)
    return redirect('chat', chat_id=chat.id)


def message_chat(request, chat_id):
    chat = Chat.objects.get(id=chat_id)
    messages = chat.messages.order_by("-id")
    unread_messages = chat.messages.filter(is_read=False)
    if unread_messages.exists():
        to_user = unread_messages[0].to_user
        if to_user == request.user:
            unread_messages.update(is_read=True)
    if request.method == 'POST':
        form = MessageForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.from_user = request.user
            message.to_user = chat.user2 if chat.user1 == request.user else chat.user1
            message.save()
            return redirect('chat', chat_id=chat.id)
    else:
        form = MessageForm()
    return render(request, 'chat.html', {'messages': messages, 'form': form})
