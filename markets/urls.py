from django.urls import path
from .views import *

urlpatterns = [
    path('',MarketList.as_view()), #상권 정보 일괄 조회
    path('<int:market_id>/', MarketSimple.as_view()), #상권 정보 간단 개별 조회
    path('detail/<int:market_id>/', MarketDetail.as_view()) #상권 정보 상세 개별 조회
]