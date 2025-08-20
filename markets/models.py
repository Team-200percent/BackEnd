from django.db import models
from accounts.models import User

# Create your models here.
class Market(models.Model):

    TYPE = (
        ('UNKNOWN', '미정'),
        ('RESTAURANT', '식당'),
        ('HOSPITAL', '병원'),
        ('CAFE', '카페'),
        ('CONVENIENCE_STORE', '편의점'),
        ('PHARMACY','약국'),
        ('COMMUNITY_CENTER', '생활기관'),
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=15)
    address = models.CharField(max_length=30)
    business_hours = models.CharField(max_length=50)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    url = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    type = models.CharField(max_length=30, choices=TYPE, default='UNKNOWN')
    lat = models.FloatField()
    lng = models.FloatField()
    created = models.DateTimeField(auto_now_add=True) # 객체를 생성할 때 날짜와 시간 저장

    
    def __str__(self): # 표준 파이썬 클래스 메서드, 사람이 읽을 수 있는 문자열을 반환하도록 함
        return self.name
    

class FavoriteGroup(models.Model):
    
    COLORS = (
        ('red', '빨강'),
        ('orange', '주황'),
        ('yellow', '노랑'),
        ('green', '초록'),
        ('blue', '파랑'),
        ('purple', '보라'),
        ('pink', '핑크'),
    )
    
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favoritegroup")
    name = models.CharField(max_length=15)
    color = models.CharField(max_length=15, choices=COLORS, default='blue') 
    visibility = models.BooleanField(default=True) # 공개 여부, 기본값은 True
    description = models.TextField(null=True, blank=True) # 그룹 설명
    relatedUrl = models.TextField(null=True, blank=True) # 관련 URL
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self): # 표준 파이썬 클래스 메서드, 사람이 읽을 수 있는 문자열을 반환하도록 함
        return self.name
    
    
class FavoriteItem(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favoriteitem")
    favoriteGroupId = models.ForeignKey(FavoriteGroup, on_delete=models.CASCADE, related_name="favoriteitem")
    marketId = models.ForeignKey(Market, on_delete=models.CASCADE, related_name="favoriteitem")
    createdAt = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): # 표준 파이썬 클래스 메서드, 사람이 읽을 수 있는 문자열을 반환하도록 함
        return self.marketId.name
    
class Image(models.Model):
    id = models.AutoField(primary_key=True)  # 기본 PK
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name="market_images")
    image_url = models.URLField(max_length=500)  # S3 URL
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image of {self.market.name}"