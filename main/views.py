from django.contrib.auth import login, authenticate
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import SignUpForm, ProfileForm

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