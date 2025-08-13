from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

class User(AbstractUser):

    GENDER_CHOICES = (
        ('MALE', '남성'),
        ('FEMALE', '여성'),
    )
    user_id = models.CharField(max_length=15)
    nickname = models.CharField(max_length=15)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nickname  # 또는 self.username 등 원하는 필드로 변경 가능