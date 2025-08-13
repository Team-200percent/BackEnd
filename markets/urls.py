from django.urls import path
from .views import *

urlpatterns = [
    path('<int:id>', get_market_detail) # 추가
]