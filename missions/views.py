# APIView를 사용하기 위해 import
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import *
from .serializers import *
from .utils import assign_weekly_missions

# 계정별 레벨별 미션 불러오는 뷰
class AccountLevelMissionView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능
    
    # 유저의 레벨별 미션을 모두 불러오는 뷰
    def get(self, request, format=None):
        user = request.user
        missions = AccountLevelMission.objects.filter(userId=user)  # 해당 유저의 레벨별 미션 조회
        serializer = AccountLevelMissionSerializer(missions, many=True)
            
        return Response({
            "user_xp": user.user_xp,
            "all_missions": serializer.data
        })
    
    def put(self, request, mission_id, format=None):
        user = request.user
        
        mission = get_object_or_404(
            AccountLevelMission,
            userId=user,
            levelmissionId=mission_id
        )
        
        # 상태 업데이트
        mission.status = 'in_progress'
        mission.startedAt = timezone.now()
        mission.save()

        return Response(
            {
                "message": f"Mission (id={mission_id}) status updated to in_progress",
                "startedAt": mission.startedAt
            },
            status=status.HTTP_200_OK
        )

# 계정별 주간 미션 불러오는 뷰
class AccountWeeklyMissionView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능
    
    def get(self, request, format=None):
        user = request.user
        missions = AccountWeeklyMission.objects.filter(userId=user)  # 해당 유저의 레벨별 미션 조회
        serializer = AccountWeeklyMissionSerializer(missions, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        assign_weekly_missions()
        return Response({"message": "Weekly missions assigned!"})
    
    
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
            mission = LevelMission.objects.get(assignedlevel=level, assignedindex=index) # level과 index로 조회 (조건에 맞는 1개)
        except LevelMission.DoesNotExist:
            return Response({"error": "Mission not found"}, status=404)

        serializer = LevelMissionSerializer(mission)
        return Response(serializer.data)
    

# 주간 미션을 하나씩 불러오는 뷰
class WeeklyMissionDetailView(APIView):
    # post는 api 테스트 용으로 만들은 것(추후 삭제할 수도 있음.)
    def post(self, request, format=None):
        serializer = WeeklyMissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 미션 인덱스를 넣어주면 해당 미션을 반환해주는 API(한 개만 반환)
    def get(self, request, weeklymissionid, format=None):
        try:
            mission = WeeklyMission.objects.get(id=weeklymissionid) # 미션 id로 조회
        except WeeklyMission.DoesNotExist:
            return Response({"error": "Mission not found"}, status=404)

        serializer = WeeklyMissionSerializer(mission)
        return Response(serializer.data)
    
    def put(self, request, weeklymissionid, format=None):
        user = request.user
        
        mission = get_object_or_404(
            AccountWeeklyMission,
            userId=user,
            weeklymissionId=weeklymissionid
        )
        
        # 상태 업데이트
        mission.status = 'in_progress'
        mission.startedAt = timezone.now()
        mission.save()

        return Response(
            {
                "message": f"Mission (id={weeklymissionid}) status updated to in_progress",
                "startedAt": mission.startedAt
            },
            status=status.HTTP_200_OK
        )


# 레벨별 미션 완료 뷰
class LevelMissionCompleteView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능

    def post(self, request, mission_id, format=None):
        user = request.user
        
        mission = get_object_or_404(
            AccountLevelMission,
            userId=user,
            levelmissionId=mission_id
        )
        
        # 상태 업데이트
        mission.status = 'completed'
        mission.startedAt = timezone.now()
        mission.save()
        
        # 경험치, 완료 미션 수 증가
        user.user_xp += 20
        user.user_completedmissions += 1  

        # 레벨 계산
        LEVEL_THRESHOLDS = [200, 700, 1600, 3100]
        level = 1
        for threshold in LEVEL_THRESHOLDS:
            if user.user_xp >= threshold:
                level += 1
            else:
                break

        # 레벨 변경 감지 및 새로운 미션 해금
        if user.user_level < level:
            user.user_level = level

            start_id = (level - 1) * 10 + 1
            end_id = level * 10

            AccountLevelMission.objects.filter(
                userId=user,
                levelmissionId__id__gte=start_id,
                levelmissionId__id__lte=end_id
            ).update(status="waiting")

        user.save()
        serializer = MissionCompleteSerializer(user)
        return Response(serializer.data)


# 주간 미션 완료 뷰 
class WeeklyMissionCompleteView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능
     
    def post(self, request, weeklymissionid, format=None):
        user = request.user
        
        mission = get_object_or_404(
            AccountWeeklyMission,
            userId=user,
            weeklymissionId=weeklymissionid
        )
        
        # 상태 업데이트
        mission.status = 'completed'
        mission.startedAt = timezone.now()
        mission.save()
        
        # 경험치, 완료 미션 수 증가
        user.user_xp += 20
        user.user_completedmissions += 1  

        # 레벨 계산
        LEVEL_THRESHOLDS = [200, 700, 1600, 3100]
        level = 1
        for threshold in LEVEL_THRESHOLDS:
            if user.user_xp >= threshold:
                level += 1
            else:
                break

        # 레벨 변경 감지 및 새로운 미션 해금
        if user.user_level < level:
            user.user_level = level

            start_id = (level - 1) * 10 + 1
            end_id = level * 10

            AccountLevelMission.objects.filter(
                userId=user,
                levelmissionId__id__gte=start_id,
                levelmissionId__id__lte=end_id
            ).update(status="waiting")

        user.save()
        serializer = MissionCompleteSerializer(user)
        return Response(serializer.data)