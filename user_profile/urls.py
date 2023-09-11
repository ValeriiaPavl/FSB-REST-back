from django.urls import path

from user_profile import views

urlpatterns = [
    path('users', views.UserInfoList.as_view()),
    path('users/extended', views.UserExtendedInfoList.as_view()),
    path('users/extended/<int:pk>', views.UserExtendedDetail.as_view()),
    path('likes/from', views.LikesFromUserView.as_view()),
    path('likes/to', views.LikesToUserView.as_view()),
    path('likes/mutual', views.MutualLikesView.as_view()),
    path('login', views.LoginView.as_view()),
    path('hashtags/add', views.HashtagView.as_view()),
    path('your_profile', views.UserFromTokenView.as_view())
]