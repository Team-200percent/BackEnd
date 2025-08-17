from .models import *
from .serializers import ReviewSerializer, ReviewShowSerializer

# APIView를 사용하기 위해 import
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.shortcuts import get_object_or_404

from django.db.models import Count, Q

class ReviewList(APIView):
    def post(self, request,market_id, format=None):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(market_id=market_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, market_id):
        reviews = Review.objects.filter(market_id=market_id).order_by('-created')
        serializer = ReviewShowSerializer(reviews, many=True)

        tag_summary = reviews.aggregate(
            taste_count=Count('id', filter=Q(taste_tag=True)),
            cost_count=Count('id', filter=Q(cost_tag=True)),
            solo_count=Count('id', filter=Q(solo_tag=True)),
            fresh_count=Count('id', filter=Q(fresh_tag=True)),
            clean_count=Count('id', filter=Q(clean_tag=True)),
            date_count=Count('id', filter=Q(date_tag=True)),
        )

        return Response({
            "tag_sum": tag_summary,
            "reviews": serializer.data,
        })

