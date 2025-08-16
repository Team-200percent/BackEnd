from rest_framework import serializers
from .models import Market

class MarketSerializer(serializers.ModelSerializer):

  class Meta:
		# 어떤 모델을 시리얼라이즈할 건지
    model = Market
		# 모델에서 어떤 필드를 가져올지
		# 전부 가져오고 싶을 때
    fields = "__all__"

class MarketSimpleSerializer(serializers.ModelSerializer):
  class Meta:
    model = Market
    fields = ['name', 'address', 'business_hours'] #평점이랑 영업중 여부 추가해야됨