from pathlib import Path
from uuid import uuid4
from .models import *
from .serializers import ReviewSerializer, ReviewGetSerializer

# APIView를 사용하기 위해 import
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.shortcuts import get_object_or_404

from django.db.models import Count, Q
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.files.storage import default_storage  
from django.conf import settings
import boto3


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
            lat = float(lat); lng = float(lng)
        except ValueError:
            return Response({"error": "invalid lat/lng"}, status=400)

        try:
            market = Market.objects.get(lat=lat, lng=lng)
        except Market.DoesNotExist:
            return Response({"error": "no market found at given coordinates"}, status=404)

        # 1) 리뷰 먼저 저장
        serializer = ReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        review = serializer.save(user=request.user, market=market)

        # 2) 이미지 여러 장 받기 (images 키). 단일 업로드는 image 키도 허용
        files = request.FILES.getlist('images')
        if not files and 'image' in request.FILES:
            files = [request.FILES['image']]

        if files:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=getattr(settings, "AWS_S3_REGION_NAME", getattr(settings, "AWS_REGION", None)),
            )

            bucket = settings.AWS_STORAGE_BUCKET_NAME
            region = getattr(settings, "AWS_S3_REGION_NAME", getattr(settings, "AWS_REGION", "ap-northeast-2"))

            urls = []
            for f in files:
                ext = (Path(f.name).suffix or ".jpg").lower()
                key = f"uploads/reviews/{review.id}/{uuid4()}{ext}"
                try:
                    # 파일을 통째로 read()하지 말고 스트림 업로드
                    s3_client.upload_fileobj(
                        f, bucket, key,
                        ExtraArgs={
                            "ContentType": f.content_type or "image/jpeg",
                        }
                    )
                except Exception as e:
                    return Response({"error": f"S3 Upload Failed: {str(e)}"},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                urls.append(f"https://{bucket}.s3.{region}.amazonaws.com/{key}")

            # Image(review FK)로 일괄 저장
            Image.objects.bulk_create([Image(review=review, image_url=u) for u in urls])

        # 3) 최종 응답 (중복 save 제거)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
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
        serializer = ReviewGetSerializer(reviews, many=True)

        # 태그 카운트 요약
        tag_summary = reviews.aggregate(
            taste_count=Count('id', filter=Q(taste_tag=True)),
            cost_count=Count('id', filter=Q(cost_tag=True)),
            solo_count=Count('id', filter=Q(solo_tag=True)),
            fresh_count=Count('id', filter=Q(fresh_tag=True)),
            clean_count=Count('id', filter=Q(clean_tag=True)),
            date_count=Count('id', filter=Q(date_tag=True)),
        )

        images_all = list(
            Image.objects.filter(review__market=market)
            .order_by('-created')
            .values_list('image_url', flat=True)
        )

        return Response({
            "market": market.name,
            "tag_sum": tag_summary,
            "images": images_all,
            "reviews": serializer.data,
        })

class ReviewPhotoList(APIView):
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

        images_all = list(
            Image.objects.filter(review__market=market)
            .order_by('-created')
            .values_list('image_url', flat=True)
        )

        return Response({
            "market": market.name,
            "images": images_all,
        })