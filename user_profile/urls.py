from django.urls import path

from user_profile import views

urlpatterns = [
    path('users/', views.UserInfoList.as_view()),
    path('users/<int:pk>', views.UserDetail.as_view()),
    path('likes/from', views.LikesFromUserView.as_view()),
    path('likes/to', views.LikesToUserView.as_view()),
    path('likes/mutual', views.MutualLikesView.as_view()),
    path('login', views.LoginView.as_view()),
    path('register', views.RegisterView.as_view()),
    path('hashtags/add', views.HashtagView.as_view())
]
