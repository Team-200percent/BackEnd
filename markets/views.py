from .serializers import MarketSerializer
from .models import *

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
    
    def get(self,request, format=None):
        markets = Market.objects.all()
        serializer = MarketSerializer(markets,many=True)
        return Response(serializer.data)
    
class MarketDetail(APIView):
    def get(self, request, market_id):
        markets = get_object_or_404(Market, id=market_id)
        serializer = MarketSerializer(markets)
        return Response(serializer.data)


    