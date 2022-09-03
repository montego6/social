from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from . import views

urlpatterns = [
    path('', views.profile_my, name='profile my'),
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
    path('notifications', views.notifications_view, name='notifications'),
    path('search/hashtag/<str:hashtag>', views.hashtag_search, name='hashtag'),
    path('comment/<int:pk>/delete', views.CommentDeleteView.as_view(), name='comment delete'),
    path('message/<int:receiver_id>', views.send_message, name='message'),
    path('chat/<int:chat_id>', views.message_chat, name='chat'),
    path('chats', views.all_chats, name='all chats'),
    path('signup', views.signup, name='signup'),
    path('login', LoginView.as_view(template_name='login.html', extra_context={'title': 'Войти'}), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path("change-password",
         PasswordChangeView.as_view(template_name="form.html", title="Смена пароля"),
         name="change-password"),
    path("reset-password",
         PasswordResetView.as_view(template_name="form.html",
                                   subject_template_name="registration/reset_subject.txt",
                                   email_template_name="registration/reset_email.txt"),
         name="password_reset"),
    path("reset-password/sent",
         PasswordResetDoneView.as_view(template_name="message.html",
                                       extra_context={"message": "Запрос успешно отправлен"}),
         name="password_reset_done"),
    path("reset-password/<uidb64>/<token>",
         PasswordResetConfirmView.as_view(template_name="form.html"), name="password_reset_confirm"),
    path("reset-password/done", PasswordResetCompleteView.as_view(template_name="message.html",
                                                                  extra_context={"message": "Пароль успешно изменен"}),
         name="password_reset_complete")
]
