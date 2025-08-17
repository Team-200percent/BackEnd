from django.urls import path
from .views import *

urlpatterns = [
    path('',MarketList.as_view()), #상권 정보 일괄 조회
    path('simple/', MarketSimple.as_view()), #상권 정보 간단 개별 조회 (lat, lng 기반)
    path('detail/', MarketDetail.as_view()), #상권 정보 상세 개별 조회 (lat, lng 기반)
    path('favoritegroup/', FavoriteGroupView.as_view()), #찜 목록 그룹 (post, get 용도)
    path('favoritegroup/<int:group_id>/', FavoriteGroupView.as_view()), #찜 목록 그룹 생성 (delete 용도)
    path('favoriteitem/<int:group_id>/', FavoriteItemView.as_view()), #찜 목록 아이템 (get 용도)
    path('favoriteitem/<int:group_id>/<int:item_id>/', FavoriteItemView.as_view()), #찜 목록 아이템 (post, delete 용도)
]