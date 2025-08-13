from django.urls import path
from .views import *

urlpatterns = [
    path('', login, name = 'account_info'),
    path('mypage/', MyPageView.as_view(), name='mypage'),
]