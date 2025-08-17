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

# 마이페이지 정보를 불러오는 뷰
class MyPageView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능
    
    # 마이페이지 정보를 반환해주는 API(한 개만 반환)
    def get(self, request, format=None):
        user = request.user  # 요청한 사용자 객체
        serializer = MypageSerializer(user)
        return Response(serializer.data)


# @require_http_methods(["POST"])
# def login(request):
#     try:
#         # Body에서 JSON 파싱
#         body = json.loads(request.body)
#         user_id = body.get("user_id")
#         password = body.get("password")

#         if not user_id or not password:
#             return JsonResponse({
#                 'status': 400,
#                 'message': 'user_id와 password를 모두 전달해야 합니다.'
#             }, status=400)

#         # 유저 조회
#         account = get_object_or_404(User, user_id=user_id)

#         # 비밀번호 확인
#         if check_password(password, account.password):
#             account_json = {
#                 "ID": account.user_id,
#                 "name": account.username,
#                 "nickname": account.nickname,
#                 "gender": account.gender,
#             }
#             return JsonResponse({
#                 'status': 200,
#                 'message': '로그인 성공',
#                 'data': account_json
#             })
#         else:
#             return JsonResponse({
#                 'status': 401,
#                 'message': '비밀번호가 일치하지 않습니다.'
#             }, status=401)

#     except Exception:
#         return JsonResponse({
#             'status': 404,
#             'message': '해당 사용자를 찾을 수 없습니다.'
#         }, status=404)
        
# 유저 목록 전체 조회
# @require_http_methods(["GET"])
# def login(request):

#        if request.method == "GET":
#         account_all = User.objects.all()
    
#         account_json_all = []
        
#         for account in account_all:
#             account_json = {
#                 "id": account.id,
#                 "username" : account.username,
#                 "password": account.password,
#             }
#             account_json_all.append(account_json)

#         return JsonResponse({
#             'status': 200,
#             'message': '유저 목록 조회 성공',
#             'data': account_json_all
#         })