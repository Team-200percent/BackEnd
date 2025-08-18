from rest_framework import serializers
from .models import *
from django.db.models import Avg


class ReviewSerializer(serializers.ModelSerializer):

  class Meta:
		# 어떤 모델을 시리얼라이즈할 건지
    model = Review
		# 모델에서 어떤 필드를 가져올지
		# 전부 가져오고 싶을 때
    fields = "__all__"
    read_only_fields = ['market']  # POST 시 필수 검증에서 제외

class ReviewGetSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    nickname = serializers.CharField(source='user.nickname', read_only=True)  # user의 nickname 가져오기
    review_count = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['nickname','rating','review_count','rating', 'images','description', 'created', 'tags']

    def get_tags(self, obj):
        tag_map = {
            "taste_tag": "음식이 맛있어요",
            "cost_tag": "가성비가 좋아요",
            "solo_tag": "혼밥하기 좋아요",
            "fresh_tag": "재료가 신선해요",
            "clean_tag": "매장이 청결해요",
            "date_tag": "데이트하기 좋아요",
        }
        return [label for field, label in tag_map.items() if getattr(obj, field)]
    
    # user가 작성한 모든 리뷰 개수
    def get_review_count(self, obj):
      return obj.user.reviews.count()
    
    def get_images(self, obj):
        # 리뷰에 연결된 모든 이미지의 URL 리스트 반환
        return [image.image_url for image in obj.images.all()]

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
