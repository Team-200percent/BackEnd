from django.shortcuts import render
from django.http import JsonResponse # 추가 
from django.shortcuts import get_object_or_404 # 추가
from django.views.decorators.http import require_http_methods
import json
from .models import User
from django.contrib.auth.hashers import check_password


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



@require_http_methods(["POST"])
def login(request):
    try:
        # Body에서 JSON 파싱
        body = json.loads(request.body)
        user_id = body.get("user_id")
        password = body.get("password")

        if not user_id or not password:
            return JsonResponse({
                'status': 400,
                'message': 'user_id와 password를 모두 전달해야 합니다.'
            }, status=400)

        # 유저 조회
        account = get_object_or_404(User, user_id=user_id)

        # 비밀번호 확인
        if check_password(password, account.password):
            account_json = {
                "ID": account.user_id,
                "name": account.username,
                "nickname": account.nickname,
                "gender": account.gender,
            }
            return JsonResponse({
                'status': 200,
                'message': '로그인 성공',
                'data': account_json
            })
        else:
            return JsonResponse({
                'status': 401,
                'message': '비밀번호가 일치하지 않습니다.'
            }, status=401)

    except Exception:
        return JsonResponse({
            'status': 404,
            'message': '해당 사용자를 찾을 수 없습니다.'
        }, status=404)