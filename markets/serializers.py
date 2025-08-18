from rest_framework import serializers
from django.db.models import Avg
from django.utils import timezone
from datetime import datetime
from .models import *

class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = "__all__"

class MarketSimpleSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    is_open = serializers.SerializerMethodField()

    class Meta:
        model = Market
        fields = ['name', 'address', 'business_hours', 'avg_rating', 'is_open']
    
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

    class Meta:
        model = Market
        fields = ['name','type','avg_rating', 'review_count','address','is_open', 'close_hour','telephone','url']
    
    # 상권에 연결된 리뷰 개수
    def get_review_count(self, obj):
        return obj.reviews.count()
    
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


class FavoriteGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteGroup
        fields = "__all__"
        read_only_fields = ['userId']
    

        
class FavoriteItemSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(source='marketId.lat', read_only=True)
    lng = serializers.FloatField(source='marketId.lng', read_only=True)
    
    class Meta:
        model = FavoriteItem
        fields = "__all__"
        read_only_fields = ['favoriteGroupId', 'userId', 'marketId']