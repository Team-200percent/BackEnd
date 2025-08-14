# APIView를 사용하기 위해 import
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import Http404
from .serializers import *


from .serializers import *

# 레벨별 미션을 하나씩 불러오는 뷰
class LevelMissionDetailView(APIView):
    # post는 api 테스트 용으로 만들은 것(추후 삭제할 수도 있음.)
    def post(self, request, format=None):
        serializer = LevelMissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 레벨, 인덱스를 넣어주면 해당 미션을 반환해주는 API(한 개만 반환)
    def get(self, request, level, index, format=None):
        try:
            mission = LevelMission.objects.get(level=level, index=index) # level과 index로 조회 (조건에 맞는 1개)
        except LevelMission.DoesNotExist:
            return Response({"error": "Mission not found"}, status=404)

        serializer = LevelMissionSerializer(mission)
        return Response(serializer.data)
    

class WeeklyMissionDetailView(APIView):
    # post는 api 테스트 용으로 만들은 것(추후 삭제할 수도 있음.)
    def post(self, request, format=None):
        serializer = WeeklyMissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 레벨, 인덱스를 넣어주면 해당 미션을 반환해주는 API(한 개만 반환)
    def get(self, request, level, index, format=None):
        try:
            missions = WeeklyMission.objects.order_by('?')[:5]
        except WeeklyMission.DoesNotExist:
            return Response({"error": "Mission not found"}, status=404)

        serializer = WeeklyMissionSerializer(mission)
        return Response(serializer.data)
    
class LevelMissionCompleteView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능
     
    def post(self, request):
        user = request.user
        user.user_xp = (user.user_xp) + 10
        user.save()
        serializer = MissionCompleteSerializer(user)
        return Response(serializer.data)
    
class WeeklyMissionCompleteView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능
     
    def post(self, request):
        user = request.user
        user.user_xp = (user.user_xp) + 20
        user.save()
        serializer = MissionCompleteSerializer(user)
        return Response(serializer.data)
