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
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from .models import *
from .serializers import *
import numpy as np
from math import log1p
from openai import OpenAI
from reviews.models import Review
from markets.models import Market
import re
from django.db.models import Avg, Count



class MarketList(APIView):
    def post(self, request, format=None):
        serializer = MarketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 상권 정보 전체 조회
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
        serializer = MarketSimpleSerializer(markets, many=True, context={'request': request})
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
        serializer = MarketDetailSerializer(markets, many=True, context={'request': request})
        return Response(serializer.data)

class MarketByType(APIView):
    def get(self, request):
        market_type = request.GET.get('type')
        markets = Market.objects.all()

        # 한글 → 코드 매핑
        type_map = {
            "unknown": "UNKNOWN",
            "food": "RESTAURANT",
            "cafe": "CAFE",
            "store": "CONVENIENCE_STORE",
            "hos": "HOSPITAL",
            "phar": "PHARMACY",
            "life": "COMMUNITY_CENTER",
        }
        if market_type:
            db_value = type_map.get(market_type, market_type)
            markets = markets.filter(type=db_value)

        serializer = MarketTypeSerializer(markets, many=True, context={"request": request})
        return Response(serializer.data)
    
class MarketSearch(APIView):
    def get(self, request):
        name = request.GET.get("name", "")
        qs = Market.objects.filter(name__icontains=name)
        qs = qs.prefetch_related("market_images")

        serializer = MarketSimpleSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)
    
    
class SearchHistoryView(APIView):
    def post(self, request, format=None):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        if lat is None or lng is None:
            return Response({"error": "lat and lng are required"}, status=400)

        lat = float(lat)
        lng = float(lng)

        # 위도/경도로 Market 검색
        market = get_object_or_404(Market, lat=lat, lng=lng)

        # SearchHistory 생성
        search_history = SearchHistory.objects.create(
            userId=request.user,
            marketId=market
        )

        # 직렬화해서 응답
        serializer = SearchHistorySerializer(search_history)
        return Response(serializer.data, status=201)
    
    def get(self, request, format=None):
        user = request.user
        histories = SearchHistory.objects.filter(userId=user).order_by('-createdAt')
        
        # 같은 marketId 중 최신 하나만 남기기
        unique_histories = []
        seen_markets = set()
        for h in histories:
            if h.marketId_id not in seen_markets:
                unique_histories.append(h)
                seen_markets.add(h.marketId_id)
        
        serializer = SearchHistorySerializer(unique_histories, many=True)
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
        sort = request.query_params.get('sort', 'latest')

        if sort == 'oldest':
            groups = FavoriteGroup.objects.filter(userId=user).order_by('createdAt')
        else:
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
        
        serializer = FavoriteItemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # lat/lng와 일치하는 Market 찾기
            market = get_object_or_404(Market, lat=lat, lng=lng)
            
            # 이미 group_id에 동일한 market이 있는지 확인
            exists = FavoriteItem.objects.filter(
                favoriteGroupId_id=group_id,
                userId=user,
                marketId=market
            ).exists()
            
            if exists:
                return Response(
                    {"error": "이미 해당 그룹에 이 마켓이 존재합니다."},
                    status=400
                )
            
            # FavoriteItem 저장
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
        sort = request.query_params.get('sort', 'latest')
        
        if sort == 'oldest':
            items = FavoriteItem.objects.filter(favoriteGroupId=group_id).order_by('createdAt')
        else:
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
    
class FavoriteItemGroupView(APIView):
    # 아이템 기반으로 그룹 조회
    def get(self, request, format=None):
        user = request.user
        
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        if lat is None or lng is None:
            return Response({"error": "lat and lng are required"}, status=400)
        
        lat = float(lat)
        lng = float(lng)
        
        # 해당 사용자의 즐겨찾기 중에서 좌표가 같은 아이템 찾기
        items = FavoriteItem.objects.filter(
            userId=user,
            marketId__lat=lat,
            marketId__lng=lng
        )

        if not items.exists():
            return Response({"error": "해당 가게는 사용자의 즐겨찾기 그룹에 포함되어 있지 않습니다."}, status=404)

        serializer = FavoriteItemGroupSerializer(items, many=True)

        return Response(serializer.data, status=200)
    
    
   
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
        file_path = f"uploads/market/{image_file.name}"
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

client = OpenAI()

def extract_terms_from_preference(pref_text: str) -> list[str]:
    # "사용자 RESTAURANT 선호: 일식, 스시" → ["일식","스시"]
    tail = pref_text.split(":", 1)[1].strip() if ":" in pref_text else pref_text.strip()
    return [t for t in re.split(r"[,\s/]+", tail) if t]

def keyword_signal(market, terms: list[str]) -> float:
    if not terms:
        return 0.0
    name = (market.name or "")
    desc = (market.description or "")

    hits = 0.0
    for kw in terms:
        if kw in name: hits += 2.0   # 이름 매칭은 강하게
        if kw in desc: hits += 1.0   # 설명 매칭은 보조로

    # 정규화(0~1): 키워드가 많아도 과도하게 치우치지 않게
    denom = max(1.0, 2.0*len(terms))
    return float(min(hits / denom, 1.0))

# 유저의 취향을 문장 형태로 변환 -> AI 임베딩 모델은 문장을 벡터로 변환함
def user_pref_text(user, ai_type: str) -> str:
    if ai_type == "CAFE":
        return f"사용자 CAFE 선호: {getattr(user, 'cafePreference', '') or ''}"
    if ai_type == "RESTAURANT":
        return f"사용자 RESTAURANT 선호: {getattr(user, 'restaurantPreference', '') or ''}"
    if ai_type == "SPORTS_LEISURE":
        return f"사용자 SPORTS_LEISURE 선호: {getattr(user, 'sportsLeisurePreference', '') or ''}"
    if ai_type == "LEISURE_CULTURE":
        return f"사용자 LEISURE_CULTURE 선호: {getattr(user, 'leisureCulturePreference', '') or ''}"
    return ""
    
# 서비스에서 추천해줄 카테고리 → 실제 Market.type 매핑
AI_TYPE_TO_MARKET_TYPES = {
    "RESTAURANT": ["RESTAURANT"],
    "CAFE": ["CAFE"],
    "SPORTS_LEISURE": ["COMMUNITY_CENTER"],
    "LEISURE_CULTURE": ["COMMUNITY_CENTER"],
}

#  마켓의 임베딩을 만들기 위한 텍스트 생성
def build_market_text(market, max_reviews=8, max_chars_each=120):
    description = market.description or ""
    reviews = (Review.objects
               .filter(market=market)
               .order_by('-created')
               .values_list('description', flat=True)[:max_reviews])
    snips = [ (r or "")[:max_chars_each] for r in reviews if r ]
    return (
        f"[이름]{market.name}\n"
        f"[종류]{market.get_type_display()}\n"
        f"[설명]{description}\n"
        f"[리뷰]{' / '.join(snips)}"
    )

# OPEN AI 임베딩 API 호출
def embed_text(text: str):
    return client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding

# 유저 선호도와 마켓을 비교하기 위한 함수
def cosine_sim(a, b):
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-9
    return float(np.dot(a, b) / denom)


class AIRecommend(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ai_types = ["RESTAURANT", "CAFE", "SPORTS_LEISURE", "LEISURE_CULTURE"]
        payload = {}

        for t in ai_types:
            pref_text = user_pref_text(request.user, t)
            if not pref_text.strip():
                payload[t] = {"preference_text": pref_text, "results": []}
                continue

            user_pref_emb = embed_text(pref_text)

            types = AI_TYPE_TO_MARKET_TYPES.get(t, [])
            market_qs = Market.objects.filter(type__in=types)

            # ⬇️ 추가: 유저 선호 키워드 추출(모든 타입에 적용해도 되고, 식당에만 해도 됨)
            terms = extract_terms_from_preference(pref_text)

            candidates = []
            for m in market_qs.iterator():
                if not m.embedding:
                    try:
                        doc = build_market_text(m)
                        m.embedding = embed_text(doc)
                        m.save(update_fields=["embedding"])
                    except Exception:
                        continue

                sim = cosine_sim(user_pref_emb, m.embedding)

                market_qs = Market.objects.filter(type__in=types).annotate(
                    _avg_rating=Avg('reviews__rating'),
                    _review_count=Count('reviews')
                )

                # 사용 시:
                avg_rating = float(getattr(m, "_avg_rating", 0.0) or 0.0)
                review_cnt = int(getattr(m, "_review_count", 0) or 0)
                quality = (avg_rating / 5.0) + 0.05 * log1p(review_cnt)

                # ⬇️ 추가: 키워드 점수
                kw = keyword_signal(m, terms)

                # ⬇️ 최종 점수: 비율은 필요 시 조정 (예: kw 0.15 ~ 0.5 사이 튜닝)
                score = 0.70 * sim + 0.15 * quality + 0.15 * kw

                serializer = MarketDetailSerializer(m, context={"request": request})
                data = serializer.data
                data["score"] = round(score, 4)
                data["parts"] = {
                    "sim": round(sim, 4),
                    "quality": round(quality, 4),
                    "kw": round(kw, 4),
                }
                candidates.append(data)

            candidates.sort(key=lambda r: r["score"], reverse=True)
            payload[t] = {"preference_text": pref_text, "results": candidates[:5]}

        return Response({"types": payload}, status=200)
    

class MarketFavoriteGroup(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        lat = request.GET.get("lat")
        lng = request.GET.get("lng")
        if lat is None or lng is None:
            return Response({"error": "lat and lng are required"}, status=400)

        lat = float(lat); lng = float(lng)

        try:
            market = Market.objects.get(lat=lat, lng=lng)
        except Market.DoesNotExist:
            return Response({"error": "no market found at given coordinates"}, status=404)

        groups = (
            FavoriteGroup.objects
            .filter(favoriteitem__userId=request.user, favoriteitem__marketId=market)
            .distinct()
        )

        data = TempSerializer(groups, many=True).data
        return Response({
            "market": {"id": market.id, "name": market.name},
            "group_count": len(data),
            "groups": data,
        }, status=200)