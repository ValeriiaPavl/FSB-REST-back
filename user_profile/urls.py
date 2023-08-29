from django.urls import path

from user_profile import views

urlpatterns = [
    path('users/', views.UserInfoList.as_view()),
    path('users/<int:pk>', views.UserDetail.as_view())
]
