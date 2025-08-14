from django.urls import path
from .views import *

urlpatterns = [
    path('',MarketList.as_view()), #상권 정보 일괄 조회
    path('<int:market_id>/', MarketDetail.as_view()) #상권 정보 개별 조회
]