from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage  
from .serializers import ImageSerializer
from django.conf import settings
import boto3
from uuid import uuid4
from rest_framework.parsers import MultiPartParser, FormParser


from .models import *
from .serializers import *

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
        serializer = MarketDetailSerializer(markets, many=True)
        return Response(serializer.data)

class MarketByType(APIView):
    def get(self, request):
        market_type = request.GET.get('type')
        qs = Market.objects.all()
        if market_type:
            qs = qs.filter(type=market_type)
        serializer = MarketTypeSerializer(qs, many=True)
        return Response(serializer.data)
    
class MarketSearch(APIView):
    def get(self, request):
        name = request.GET.get("name")
        markets = Market.objects.filter(name__icontains=name)
        serializer = MarketSimpleSerializer(markets, many=True)
        return Response(serializer.data)

# 찜 목록 관련 api
class FavoriteGroupView(APIView):
    # 관련 모든 정보 넘어오도록 설정
    def post(self, request, format=None):
        serializer = FavoriteGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(userId=request.user)  # user 필드 직접 할당
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    # 유저의 찜 목록 조회
    def get(self, request, format=None):
        user = request.user
        # 기본은 등록순, 최신순은 쿼리 파라미터로 지정 가능
        sort = request.query_params.get('sort', 'latest')  # ?sort=latest or ?sort=oldest

        if sort == 'oldest':
            groups = FavoriteGroup.objects.filter(userId=user).order_by('createdAt')
        else:  # latest
            groups = FavoriteGroup.objects.filter(userId=user).order_by('-createdAt')
            
        serializer = FavoriteGroupSerializer(groups, many=True)
        return Response(serializer.data)
    
    # 유저의 찜 목록 업데이트
    def put(self, request, group_id, format=None):
        user = request.user
        try:
            group = FavoriteGroup.objects.get(id=group_id, userId=user)
        except FavoriteGroup.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
        
        serializer = FavoriteGroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save(userId=user)
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
    # 유저의 찜 목록 삭제
    def delete(self, request, group_id, format=None):
        user = request.user
        group = get_object_or_404(FavoriteGroup, id=group_id)
        group.delete()
        return Response({"detail": "성공적으로 삭제하였습니다."}, status=status.HTTP_204_NO_CONTENT)


# 찜 목록 그룹의 item관련 api
class FavoriteItemView(APIView):
    # 찜 목록 그룹에 아이템 추가
    def post(self, request, group_id, format=None):
        user = request.user
    
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        if lat is None or lng is None:
            return Response({"error": "lat and lng are required"}, status=400)
        
        lat = float(lat)
        lng = float(lng)
        
        serializer = FavoriteItemSerializer(data=request.data)
        if serializer.is_valid():
            # 1. lat/lng와 일치하는 Market 찾기
            market = get_object_or_404(Market, lat=lat, lng=lng)
            
            # 2. FavoriteItem 저장
            serializer.save(
                favoriteGroupId_id=group_id,
                userId=user,
                marketId=market
            )
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
        
    
    # 찜 목록 그룹의 아이템 조회
    def get(self, request, group_id, format=None):
        user = request.user
        
        # 기본은 등록순, 최신순은 쿼리 파라미터로 지정 가능
        sort = request.query_params.get('sort', 'latest')  # ?sort=latest or ?sort=oldest
        
        if sort == 'oldest':
            items = FavoriteItem.objects.filter(favoriteGroupId=group_id).order_by('createdAt')
        else:  # latest
            items = FavoriteItem.objects.filter(favoriteGroupId=group_id).order_by('-createdAt')
    
        serializer = FavoriteItemSerializer(items, many=True, context={"request": request})
        return Response({
        "count": items.count(),
        "results": serializer.data
    })
    
    # 찜 목록 그룹의 아이템 삭제
    def delete(self, request, group_id, format=None):
        user = request.user
        
        try:
            lat = float(request.query_params["lat"])
            lng = float(request.query_params["lng"])
        except (KeyError, TypeError, ValueError):
            return Response({"error": "lat and lng are required and must be valid numbers"}, status=400)
        
        # lat/lng에 해당하는 Market 가져오기 (여러 개면 첫 번째 선택)
        market = Market.objects.filter(lat=lat, lng=lng).first()
        if not market:
            return Response({"error": "Market not found"}, status=404)
        
        # FavoriteItem 가져오기
        favorite_item = FavoriteItem.objects.filter(
            userId=user,
            favoriteGroupId_id=group_id,
            marketId=market
        ).first()
        
        if not favorite_item:
            return Response({"error": "FavoriteItem not found"}, status=404)
        
        favorite_item.delete()
        return Response({"detail": "성공적으로 삭제하였습니다."}, status=204)
      
class ImageUploadView(APIView):
    def post(self, request):
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        if lat is None or lng is None:
            return Response({"error": "lat and lng are required"}, status=400)
        
        lat = float(lat)
        lng = float(lng)
        market = Market.objects.get(lat=lat, lng=lng)
        if 'image' not in request.FILES:
            return Response({"error": "No image file"}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

        # S3에 파일 저장
        file_path = f"uploads/{image_file.name}"
        # S3에 파일 업로드
        try:
            s3_client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_path,
                Body=image_file.read(),
                ContentType=image_file.content_type,
            )
        except Exception as e:
            return Response({"error": f"S3 Upload Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 업로드된 파일의 URL 생성
        image_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_path}"

        # DB에 저장
        image_instance = Image.objects.create(
            market=market,
            image_url=image_url,   # FileField라면 file=key
            # role/order/width/height 등 메타 있으면 추가
        )
        serializer = ImageSerializer(image_instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
