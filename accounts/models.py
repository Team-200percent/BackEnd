from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    GENDER_CHOICES = (
        ('MALE', '남성'),
        ('FEMALE', '여성'),
    )

    # username을 user_id로 사용
    nickname = models.CharField(max_length=15, null=True, blank=True)  # 유저 닉네임
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, null=True, blank=True) # 유저 성별
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # 계정 생성 시간
    user_level = models.IntegerField(default=1, null=True, blank=True) # 유저 레벨
    user_xp = models.IntegerField(default=0, null=True, blank=True)    # 유저 경험치
    user_completedmissions = models.IntegerField(default=0, null=True, blank=True) # 유저가 완료한 미션 수
    
    relocationDate = models.CharField(max_length=20, null=True, blank=True) # 이사시기
    movedInReported = models.BooleanField(default=False, null=True, blank=True) # 전입 신고 여부
    residenceType = models.CharField(max_length=20, null=True, blank=True) # 거주형태
    residentCount = models.IntegerField(default=1, null=True, blank=True)  # 거주인원
    
    localInfrastructure = models.CharField(max_length=200, null=True, blank=True)  # 동네 인프라
    
    localLivingExperience = models.CharField(max_length=200, null=True, blank=True) # 동네 생활 겸험
    
    cafePreference = models.CharField(max_length=200, null=True, blank=True)       # 카페 취향
    restaurantPreference = models.CharField(max_length=200, null=True, blank=True) # 식당 선호
    sportsLeisurePreference = models.CharField(max_length=200, null=True, blank=True)  # 운동 레저 선호
    leisureCulturePreference = models.CharField(max_length=200, null=True, blank=True) # 여가 문화 선호

    def __str__(self):
        return self.username  # 또는 self.username 등 원하는 필드로 변경 가능
    
    @staticmethod
    def get_user_by_username(username):
        try:
            return User.objects.get(username=username)
        except Exception:
            return None

       
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")  # 내가 팔로우하는 대상들
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers") # 나를 팔로우하는 사람들
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("follower", "following")
        constraints = [
            models.CheckConstraint(
                name="no_self_follow",
                check=~models.Q(follower=models.F("following"))
            ),
        ]
        indexes = [
            models.Index(fields=["follower"]),
            models.Index(fields=["following"]),
        ]

    def __str__(self):
        return f"{self.follower} → {self.following}"
