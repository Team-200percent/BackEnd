from django.db import models
from accounts.models import User

# 레벨별 미션
class LevelMission(models.Model):
    
    STICKER = (
        ('heart', '즐겨찾기 관련')
        ('like', 'ai 추천 관련')
        ('pencil', '리뷰 관련')
        ('map', '방문 인증 관련')
        ('person', '소셜 기능 관련')
        ('facility', '생활기관 관련')
    )

    id = models.AutoField(primary_key=True) # id -> 자동 키 생성
    assignedlevel = models.IntegerField()   # 미션에 부여된 레벨
    assignedindex = models.IntegerField()   # 미션에 부여된 인덱스
    title = models.CharField(max_length=100)              # 미션 제목
    description = models.TextField(null=True, blank=True)    # 미션에 대한 설명
    requirements = models.TextField(null=True, blank=True)   # 미션 완료 요구사항
    category = models.CharField(max_length=15, choices=STICKER, default='heart') # 레벨별 미션 대분류
    requireverification = models.BooleanField(default=False)  # 미션 완료 인증 필요 여부

    def __str__(self):
        return self.title


# 주간 미션 
class WeeklyMission(models.Model):
    
    id = models.AutoField(primary_key=True)    # id -> 자동 키 생성
    title = models.CharField(max_length=100)               # 미션 제목
    description = models.TextField(null=True, blank=True)  # 미션에 대한 설명
    requirements = models.TextField(null=True, blank=True) # 미션 완료 요구사항
    category = models.CharField(max_length=15, null=True, blank=True) # 주간 미션 대분류
    requireverification = models.BooleanField(default=False)  # 미션 완료 인증 필요 여부
    
    def __str__(self):
        return self.title


class AccountLevelMission(models.Model):

    STATUS = (
        ('completed', '미션 완료'),
        ('in_progress', '미션 진행 중'),
        ('waiting', '미션 시작 대기'),
        ('not_available', '미션 시작 불가')
    )
    
    id = models.AutoField(primary_key=True)  
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accountlevelmission")
    levelmissionId = models.ForeignKey(LevelMission, on_delete=models.CASCADE, related_name="accountlevelmission")
    status = models.CharField(max_length=15, choices=STATUS, default='not_available') # 미션 상태
    startedAt = models.DateTimeField(null=True, blank=True) # 미션 시작 시간
    completedAt = models.DateTimeField(null=True, blank=True) # 미션 완료 시간
    
    def __str__(self):
        return f"{self.userId} - {self.levelmissionId}"


class AccountWeeklyMission(models.Model):

    STATUS = (
        ('completed', '미션 완료'),
        ('in_progress', '미션 진행 중'),
        ('waiting', '미션 시작 대기')
    )
    
    id = models.AutoField(primary_key=True)  
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accountweeklymission")
    weeklymissionId = models.ForeignKey(WeeklyMission, on_delete=models.CASCADE, related_name="accountweeklymission")
    status = models.CharField(max_length=15, choices=STATUS, default='waiting') # 미션 상태
    startedAt = models.DateTimeField(null=True, blank=True) # 미션 시작 시간
    completedAt = models.DateTimeField(null=True, blank=True) # 미션 완료 시간
    
    def __str__(self):
        return f"{self.userId} - {self.weeklymissionId}"