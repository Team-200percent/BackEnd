from django.db import models

# 레벨별 미션
class LevelMission(models.Model):

    id = models.AutoField(primary_key=True) # id -> 자동 키 생성
    assignedlevel = models.IntegerField()   # 미션에 부여된 레벨
    assignedindex = models.IntegerField()   # 미션에 부여된 인덱스
    title = models.CharField()              # 미션 제목
    description = models.TextField(null=True, blank=True)    # 미션에 대한 설명
    requirements = models.TextField(null=True, blank=True)   # 미션 완료 요구사항

    def __str__(self):
        return self.name
    
# 주간 미션 
class WeeklyMission(models.Model):
    
    id = models.AutoField(primary_key=True)    # id -> 자동 키 생성
    title = models.CharField()                 # 미션 제목
    description = models.TextField(null=True, blank=True)  # 미션에 대한 설명
    requirements = models.TextField(null=True, blank=True) # 미션 완료 요구사항
    category = models.CharField(max_length=15, null=True, blank=True) # 주간 미션 대분류 (나중에 추천 위해서 필요할지도 몰라서)
    
    def __str__(self):
        return self.name