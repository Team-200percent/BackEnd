from django.db import models
from accounts.models import User

# 레벨별 미션
class LevelMission(models.Model):

    id = models.AutoField(primary_key=True) # id -> 자동 키 생성
    assignedlevel = models.IntegerField()   # 미션에 부여된 레벨
    assignedindex = models.IntegerField()   # 미션에 부여된 인덱스
    title = models.CharField()              # 미션 제목
    description = models.TextField(null=True, blank=True)    # 미션에 대한 설명
    requirements = models.TextField(null=True, blank=True)   # 미션 완료 요구사항
    requireverification = models.BooleanField(default=False)  # 미션 완료 인증 필요 여부

    def __str__(self):
        return self.name
    
# 주간 미션 
class WeeklyMission(models.Model):
    
    id = models.AutoField(primary_key=True)    # id -> 자동 키 생성
    title = models.CharField()                 # 미션 제목
    description = models.TextField(null=True, blank=True)  # 미션에 대한 설명
    requirements = models.TextField(null=True, blank=True) # 미션 완료 요구사항
    category = models.CharField(max_length=15, null=True, blank=True) # 주간 미션 대분류 (나중에 추천 위해서 필요할지도 몰라서)
    requireverification = models.BooleanField(default=False)  # 미션 완료 인증 필요 여부
    
    def __str__(self):
        return self.name
    
class AccountLevelMission(models.Model):

    STATUS = (
        ('completed', '미션 완료'),
        ('in_progress', '미션 진행 중'),
        ('waiting', '미션 시작 대기'),
        ('not_available', '미션 시작 불가'),
    )
    
    id = models.AutoField(primary_key=True)  
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favoritegroup")
    levelmissionId = models.ForeignKey(LevelMission, on_delete=models.CASCADE)  # 수행한 레벨 미션
    status = models.CharField(max_length=15, choices=STATUS, default='not_available') # 미션 상태
    startedAt = models.DateTimeField() # 미션 시작 시간
    completedAt = models.DateTimeField() # 미션 완료 시간
    
    def __str__(self):
        return f"{self.account.username} - {self.levelmission.title}"