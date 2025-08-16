from .models import *
from .serializers import MarketSerializer, MarketSimpleSerializer

# APIView를 사용하기 위해 import
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.shortcuts import get_object_or_404


class MarketList(APIView):
    def post(self, request, format=None):
        serializer = MarketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 상권 정보 전체 조회 -- 모든 정보를 한번에 출력하는건데 필요한가?
    def get(self,request, format=None):
        markets = Market.objects.all()
        serializer = MarketSerializer(markets,many=True)
        return Response(serializer.data)
    
# 간단 조회 -- 이름, 주소, 영업중 여부, 영업 시간, 평점
class MarketSimple(APIView):
    def get(self, request):
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        if lat is None or lng is None:
            return Response({"error": "lat and lng are required"}, status=400)
        
        lat = float(lat)
        lng = float(lng)
        markets = Market.objects.filter(lat=lat, lng=lng)
        serializer = MarketSimpleSerializer(markets, many=True)
        return Response(serializer.data)

# 상세 조회
class MarketDetail(APIView):
    def get(self, request):
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        if lat is None or lng is None:
            return Response({"error": "lat and lng are required"}, status=400)
        
        lat = float(lat)
        lng = float(lng)
        markets = Market.objects.filter(lat=lat, lng=lng)
        serializer = MarketSerializer(markets, many=True)
        return Response(serializer.data)
