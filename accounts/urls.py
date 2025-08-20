from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("join/", RegisterView.as_view()),
    path("login/", AuthView.as_view()), 
    path("xp/", UserXpView.as_view()),
    path('mypage/', MyPageView.as_view(), name='mypage'),
    path('mypage/preference/', MyPagePreferenceView.as_view(), name='mypage_preference'),
    path('follow/',FollowView.as_view())
]