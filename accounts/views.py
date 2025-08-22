from django.shortcuts import render
from django.http import JsonResponse 
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import check_password
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework import status

import json
from .models import *
from missions.models import *
from .serializers import *



# 회원가입 뷰
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        # 유효성 검사 
        if serializer.is_valid(raise_exception=True):
            
            # 유효성 검사 통과 후 객체 생성
            user = serializer.save()
            
            # 모든 레벨 미션 가져오기
            all_level_missions = LevelMission.objects.all()

            # AccountLevelMission 생성
            account_missions = []
            now = timezone.now()
            for mission in all_level_missions:
                initial_status = 'waiting' if mission.id == 1 else 'not_available'
                account_missions.append(
                    AccountLevelMission(
                        userId=user,
                        levelmissionId=mission,
                        status=initial_status,  # 조건에 따라 상태 지정
                        startedAt=now,
                        completedAt=None
                    )
                )
                
            # bulk_create로 한 번에 저장
            AccountLevelMission.objects.bulk_create(account_missions)

            # user에게 refresh token 발급
            token = RefreshToken.for_user(user)
            refresh_token = str(token)
            access_token = str(token.access_token)

            res = Response(
                {
                    "user": serializer.data,
                    "message": "성공적으로 등록하였습니다!",
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    }, 
                },
                status=status.HTTP_201_CREATED,
            )
            return res
  
      
class UsernameCheckView(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        if not username:
            return Response(
                {"message": "username을 입력해주세요."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"available": False, "message": "이미 사용 중인 아이디입니다."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"available": True, "message": "사용 가능한 아이디입니다."},
                status=status.HTTP_200_OK
            )
        

# 로그인 뷰
class AuthView(APIView):
    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        
        # 유효성 검사
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            access_token = serializer.validated_data['access_token']
            refresh_token = serializer.validated_data['refresh_token']

            res = Response(
                {
                    "user": {
                        "username": user.username,
                    },
                    "message": "login success!",
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    }, 
                },
                status=status.HTTP_200_OK,
            )

            res.set_cookie("access_token", access_token, httponly=True)
            res.set_cookie("refresh_token", refresh_token, httponly=True)
            return res
        
        # 유효성 검사 실패 시 오류 반환
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UserXpView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능
    
    # level, xp 입력용(테스트 API)
    def post(self, request, format=None):
        user_level = request.data.get('user_level')
        user_xp = request.data.get('user_xp')

        if user_level is None or user_xp is None:
            return Response(
                {"message": "level과 xp를 모두 입력해주세요."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_level = int(user_level)
            user_xp = int(user_xp)
        except ValueError:
            return Response(
                {"message": "level과 xp는 정수여야 합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"user_level": user_level, "user_xp": user_xp}, status=status.HTTP_200_OK)
    
    # 유저의 레벨을 반환해주는 API
    def get(self, request, format=None):
        user = request.user  # 요청한 사용자 객체
        user_level = user.user_level  # 유저의 레벨
        user_xp = user.user_xp  # 유저의 레벨
        return Response({"user_level": user_level, "user_xp": user_xp})
    

# 마이페이지 정보를 불러오는 뷰
class MyPageView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능
    
    # 마이페이지 정보를 반환해주는 API(한 개만 반환)
    def get(self, request, format=None):
        user = request.user  # 요청한 사용자 객체
        serializer = MypageSerializer(user)
        return Response(serializer.data)
    
    
class MyPagePreferenceView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능
    
    # 마이페이지 정보를 반환해주는 API(한 개만 반환)
    def get(self, request, format=None):
        user = request.user  # 요청한 사용자 객체
        serializer = UserPreferenceSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 유저 취향 수정
    def put(self, request, format=None):
        user = request.user
        serializer = UserPreferenceSerializer(user, data=request.data, partial=True)  # partial=True: 일부 필드만 수정 가능
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class FollowView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        nickname = request.GET.get('nickname')
        if nickname is None:
            return Response({"error" : "nickname is required"}, status = 400)
        
        serializer = FollowSerializer(
            data={"nickname": nickname},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        follow = serializer.save()
        return Response({"detail": "팔로우 완료", "following": follow.following.nickname}, status=status.HTTP_201_CREATED)

    def get(self, request):
        # 현재 사용자 기준으로 팔로잉/팔로워 숫자만 반환
        serializer = FollowNumSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)