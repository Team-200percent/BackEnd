from rest_framework import serializers
from django.db.models import Avg
from django.utils import timezone
from datetime import datetime
from .models import *
from math import radians, sin, cos, sqrt, atan2

class MarketSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Market
        fields = [
            "id", "name","address","business_hours","description","category","url","telephone","lat", "lng","created"    
        ]

class MarketSimpleSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    is_open = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Market
        fields = ['name', 'is_favorite','address','is_open', 'business_hours', 'avg_rating', 'images', "lat", "lng"]
    
    def get_is_favorite(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user is None or user.is_anonymous:
            return False  # 로그인 안 했으면 False

        return FavoriteItem.objects.filter(userId=user, marketId=obj).exists()
    
    def get_images(self, obj):
        # Image 모델의 related_name 이 'market_images' 라는 전제
        qs = obj.market_images.all().order_by("-id")  # 최신 먼저 보이게
        return ImageSerializer(qs, many=True).data
    
    # 해당 마켓에 연결된 리뷰의 평균 평점 계산
    def get_avg_rating(self, obj):
        avg = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 1) if avg is not None else None
    

    def get_is_open(self, obj):
        try:
            # business_hours 파싱
            start_str, end_str = obj.business_hours.split("~")
            start_str, end_str = start_str.strip(), end_str.strip()

            # 문자열을 시간으로 변환
            start = datetime.strptime(start_str, "%H:%M").time()
            end = datetime.strptime(end_str, "%H:%M").time()

            # 현재 시간 (서버 로컬타임)
            now = timezone.localtime().time()

            if start < end:
                return start <= now <= end
            else:
                return now >= start or now <= end

        except Exception:
            return False
    
class MarketDetailSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    is_open = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    close_hour = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    category = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Market
        fields = ['name','is_favorite','category','avg_rating', 'review_count','images','address','is_open', 'close_hour','telephone','url', "lat", "lng"]
    
    def get_is_favorite(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user is None or user.is_anonymous:
            return False  # 로그인 안 했으면 False

        return FavoriteItem.objects.filter(userId=user, marketId=obj).exists()
    
    def get_images(self, obj):
        # Image 모델의 related_name 이 'market_images' 라는 전제
        qs = obj.market_images.all().order_by("-id")  # 최신 먼저 보이게
        return ImageSerializer(qs, many=True).data
    
    # 상권에 연결된 리뷰 개수
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    def get_type_display(self, obj):
        return obj.get_type_display()
    
    def get_close_hour(self, obj):
        try:
            _, end_str = obj.business_hours.split("~")
            return end_str.strip()
        except Exception:
            return None
    
    # 해당 마켓에 연결된 리뷰의 평균 평점 계산
    def get_avg_rating(self, obj):
        avg = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 2) if avg is not None else None
    
    def get_is_open(self, obj):
        try:
            # business_hours 파싱
            start_str, end_str = obj.business_hours.split("~")
            start_str, end_str = start_str.strip(), end_str.strip()

            # 문자열을 시간으로 변환
            start = datetime.strptime(start_str, "%H:%M").time()
            end = datetime.strptime(end_str, "%H:%M").time()

            # 현재 시간 (서버 로컬타임)
            now = timezone.localtime().time()

            if start < end:
                return start <= now <= end
            else:
                return now >= start or now <= end

        except Exception:
            return False
        
class MarketTypeSerializer(MarketSimpleSerializer):
    avg_rating = serializers.SerializerMethodField()
    is_open = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    category = serializers.CharField(source='get_type_display', read_only=True)
    is_favorite = serializers.SerializerMethodField()


    class Meta:
        model = Market
        fields = ['name','is_favorite','category','is_open', 'avg_rating', 'review_count','images']
    
    def get_type_display(self, obj):
        return obj.get_type_display()
    
    def get_is_favorite(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user is None or user.is_anonymous:
            return False  # 로그인 안 했으면 False

        return FavoriteItem.objects.filter(userId=user, marketId=obj).exists()
    
    def get_images(self, obj):
        # Image 모델의 related_name 이 'market_images' 라는 전제
        qs = obj.market_images.all().order_by("-id")  # 최신 먼저 보이게
        return ImageSerializer(qs, many=True).data
    
    # 상권에 연결된 리뷰 개수
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    # 해당 마켓에 연결된 리뷰의 평균 평점 계산
    def get_avg_rating(self, obj):
        avg = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 2) if avg is not None else None
    
    def get_is_open(self, obj):
        try:
            # business_hours 파싱
            start_str, end_str = obj.business_hours.split("~")
            start_str, end_str = start_str.strip(), end_str.strip()

            # 문자열을 시간으로 변환
            start = datetime.strptime(start_str, "%H:%M").time()
            end = datetime.strptime(end_str, "%H:%M").time()

            # 현재 시간 (서버 로컬타임)
            now = timezone.localtime().time()

            if start < end:
                return start <= now <= end
            else:
                return now >= start or now <= end

        except Exception:
            return False

class FavoriteGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteGroup
        fields = "__all__"
        read_only_fields = ['userId']
    

        
class FavoriteItemSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(source='marketId.lat', read_only=True)
    lng = serializers.FloatField(source='marketId.lng', read_only=True)
    name = serializers.CharField(source='marketId.name', read_only=True)
    address = serializers.CharField(source='marketId.address', read_only=True)
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = FavoriteItem
        fields = "__all__"
        read_only_fields = ['favoriteGroupId', 'userId', 'marketId']

    def get_distance(self, obj):
        request = self.context.get("request")
        try:
            user_lat = float(request.query_params["lat"])
            user_lng = float(request.query_params["lng"])
        except (KeyError, TypeError, ValueError):
            return None

        # haversine formula (km)
        R = 6371
        dlat = radians(obj.marketId.lat - user_lat)
        dlng = radians(obj.marketId.lng - user_lng)
        a = sin(dlat/2)**2 + cos(radians(user_lat)) * cos(radians(obj.marketId.lat)) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return f"{round(R * c, 2)} km"

class FavoriteItemGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteItem
        fields = ['userId','favoriteGroupId','marketId']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


# 영현이가 요청한거 -> 실제 서비스에 반영 x
class TempSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "nickname")