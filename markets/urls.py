from django.urls import path
from .views import *

urlpatterns = [
    path('',MarketList.as_view()), #상권 정보 일괄 조회
    path('simple/', MarketSimple.as_view()), #상권 정보 간단 개별 조회 (lat, lng 기반)
    path('detail/', MarketDetail.as_view()) #상권 정보 상세 개별 조회 (lat, lng 기반)
]