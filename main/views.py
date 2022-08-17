from django.contrib.auth import login, authenticate
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse

from .forms import SignUpForm, ProfileForm, PostForm
from .models import Profile, Post
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
    return render(request, 'profile.html')


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
    return render(request, 'post_detail.html', {'post': post})


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
    else:
        post.like.add(request.user)
    return redirect("profile my")


def search(request):
    search_query = request.POST["search_input"]
    users = User.objects.filter(username__icontains=search_query)
    posts = Post.objects.filter(text__icontains=search_query)
    return render(request, 'search.html', {'users':users, 'posts': posts})