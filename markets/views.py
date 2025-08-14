import json
from django.shortcuts import render
from django.http import JsonResponse 
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import *

# Create your views here.

@require_http_methods(["POST"])
def market_post(request):
    
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))

        market_id = body.get('id')
        market = get_object_or_404(Market, pk=market_id)
        
        new_market = Market.objects.create(
            name = body['name'],
            description = body['description'],
            type = body['type'],
        )
    
        new_market_json = {
            "id": new_market.id,
            "name" : new_market.name,
            "description": new_market.description,
            "type": new_market.type,
        }

        return JsonResponse({
            'status': 200,
            'message': '게시글 생성 성공',
            'data': new_market_json
        })
    
@require_http_methods(["GET"])
def get_market_detail(reqeust, id):
    market = get_object_or_404(Market, pk=id)
    market_detail_json = {
        "id" : market.id,
        "name" : market.name,
        "description" : market.description,
        "type" : market.type,
    }
    return JsonResponse({
        "status" : 200,
        "data": market_detail_json})
    