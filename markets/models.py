from django.db import models

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
    business_hours = models.CharField(max_length=15)
    description = models.TextField()
    type = models.CharField(max_length=30, choices=TYPE, default='UNKNOWN')
    lat = models.FloatField()
    lng = models.FloatField()
    created = models.DateTimeField(auto_now_add=True) # 객체를 생성할 때 날짜와 시간 저장

    
    def __str__(self): # 표준 파이썬 클래스 메서드, 사람이 읽을 수 있는 문자열을 반환하도록 함
        return self.name