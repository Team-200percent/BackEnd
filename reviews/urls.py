from django.urls import path
from .views import *

urlpatterns = [
    path('', ReviewList.as_view()), #상권별 리뷰 정보 조회
    #path('upload/', ImageUploadView.as_view(), name='image-upload')
]