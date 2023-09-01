from django.urls import path

from user_profile import views
from .views import LoginView

urlpatterns = [
    path('users/', views.UserInfoList.as_view()),
    path('users/<int:pk>', views.UserDetail.as_view()),
    path('likes/', views.LikesView.as_view()),
    path('login', LoginView.as_view())
]
