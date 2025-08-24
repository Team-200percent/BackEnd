from rest_framework import serializers
from .models import *
from django.db.models import Avg
from markets.models import FavoriteItem


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
    user_follower = serializers.SerializerMethodField()


    class Meta:
        model = Review
        fields = ['nickname','rating','user_follower','review_count','rating', 'images','description', 'created', 'tags']

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
    
    def get_user_follower(self, obj):
        return obj.user.followers.count()
    
    def get_images(self, obj):
        # 리뷰에 연결된 모든 이미지의 URL 리스트 반환
        return [image.image_url for image in obj.images.all()]

class ReviewRecommendSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    market_name = serializers.CharField(source='market.name', read_only=True)
    market_type = serializers.CharField(source='market.get_type_display', read_only=True)
    lat = serializers.FloatField(source='market.lat',read_only=True)
    lng = serializers.FloatField(source='market.lng',read_only=True)

    is_favorite = serializers.SerializerMethodField()
    market_review_count = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    user_review_count = serializers.SerializerMethodField()
    user_follower = serializers.SerializerMethodField()

    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id',
            'nickname',
            'market_name',
            'market_type',
            'lat',
            'lng',
            'is_favorite',
            'market_review_count',
            'avg_rating',
            'user_review_count',
            'user_follower',
            'rating',
            'images',
            'description',
            'created',
            'tags',
        ]

    def get_is_favorite(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or user.is_anonymous:
            return False
        return FavoriteItem.objects.filter(userId=user, marketId=obj.market).exists()

    def get_market_review_count(self, obj):
        return obj.market.reviews.count()

    def get_avg_rating(self, obj):
        avg = obj.market.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 2) if avg is not None else None

    def get_user_review_count(self, obj):
        return obj.user.reviews.count()

    def get_user_follower(self, obj):
        return obj.user.followers.count()

    def get_images(self, obj):
        return [im.image_url for im in obj.images.all()]

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
    

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
