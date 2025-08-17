from .models import *
from .serializers import ReviewSerializer, ReviewTagSerializer

# APIView를 사용하기 위해 import
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.shortcuts import get_object_or_404

from django.db.models import Count, Q
from rest_framework.permissions import IsAuthenticated, AllowAny


class ReviewList(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]
    def post(self, request, format=None):
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')

        if lat is None or lng is None:
            return Response({"error": "lat and lng are required"}, status=400)
        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            return Response({"error": "invalid lat/lng"}, status=400)
        # 경도, 위도로 상권 찾기
        try:
            market = Market.objects.get(lat=lat, lng=lng)
        except Market.DoesNotExist:
            return Response({"error": "no market found at given coordinates"}, status=404)
        # 리뷰 저장
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, market=market)  # market, user 연결
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, format=None):
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')

        if lat is None or lng is None:
            return Response({"error": "lat and lng are required"}, status=400)

        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            return Response({"error": "invalid lat/lng"}, status=400)

        # 경도/위도로 상권 찾기
        try:
            market = Market.objects.get(lat=lat, lng=lng)
        except Market.DoesNotExist:
            return Response({"error": "no market found at given coordinates"}, status=404)

        # 해당 상권 리뷰 불러오기
        reviews = Review.objects.filter(market=market).order_by('-created')
        serializer = ReviewTagSerializer(reviews, many=True)

        # 태그 카운트 요약
        tag_summary = reviews.aggregate(
            taste_count=Count('id', filter=Q(taste_tag=True)),
            cost_count=Count('id', filter=Q(cost_tag=True)),
            solo_count=Count('id', filter=Q(solo_tag=True)),
            fresh_count=Count('id', filter=Q(fresh_tag=True)),
            clean_count=Count('id', filter=Q(clean_tag=True)),
            date_count=Count('id', filter=Q(date_tag=True)),
        )

        return Response({
            "market": market.name,
            "tag_sum": tag_summary,
            "reviews": serializer.data,
        })
