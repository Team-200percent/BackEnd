from rest_framework import serializers
from .models import *

class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = "__all__"

class MarketSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = ['name', 'address', 'business_hours'] #평점이랑 영업중 여부 추가해야됨

class FavoriteGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteGroup
        fields = "__all__"
        read_only_fields = ['userId']
    

        
class FavoriteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteItem
        fields = "__all__"
        read_only_fields = ['favoriteGroupId', 'userId', 'marketId']