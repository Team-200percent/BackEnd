from django.db import models
from accounts.models import User  # accounts 앱의 User 모델
from markets.models import Market  # markets 앱의 Market 모델

# Create your models here.
class Review(models.Model):

    RATING_SCORE = (
        (0.5, "0.5"),
        (1.0, "1.0"),
        (1.5, "1.5"),
        (2.0, "2.0"),
        (2.5, "2.5"),
        (3.0, "3.0"),
        (3.5, "3.5"),
        (4.0, "4.0"),
        (4.5, "4.5"),
        (5.0, "5.0"),
    )
    id = models.AutoField(primary_key=True)
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.FloatField(choices=RATING_SCORE)    
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True) # 객체를 생성할 때 날짜와 시간 저장


    taste_tag = models.BooleanField(default=False)  # 음식이 맛있어요
    cost_tag = models.BooleanField(default=False)   # 가성비가 좋아요
    solo_tag = models.BooleanField(default=False)   # 혼밥하기 좋아요
    fresh_tag = models.BooleanField(default=False)  # 재료가 신선해요
    clean_tag = models.BooleanField(default=False)  # 매장이 청결해요
    date_tag = models.BooleanField(default=False)   # 데이트하기 좋아요  
        
    def __str__(self):
        return f"Review {self.id} - {self.rating}"