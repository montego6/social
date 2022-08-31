from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('login', LoginView.as_view(template_name='form.html', extra_context={'title': 'Войти'}), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile', views.profile_my, name='profile my'),
    path('profile/add-bio', views.add_profile_bio, name='profile add bio'),
    path('profile/change-bio/<int:pk>', views.ProfileUpdateView.as_view(), name='profile change bio'),
    path('profile/<int:profile_id>', views.profile, name='profile'),
    path('post/add', views.add_post, name='post add'),
    path('post/<int:post_id>', views.detail_post, name='post detail'),
    path('post/<int:pk>/delete', views.PostDeleteView.as_view(), name='post delete'),
    path('post/<int:pk>/update', views.PostUpdateView.as_view(), name='post update'),
    path('post/<int:pk>/like', views.like_post, name='post like'),
    path('search', views.search, name='search'),
    path('follow/<int:profile_id>', views.follow, name='follow'),
    path('feed', views.feed, name='feed'),
    path('followers/<int:profile_id>', views.followers, name='followers'),
    path('following/<int:profile_id>', views.following, name='following'),
    path('notifications', views.notifications_view, name='notifications')
]
