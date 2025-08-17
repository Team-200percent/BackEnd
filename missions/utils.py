import random
from django.contrib.auth import get_user_model
from .models import WeeklyMission, AccountWeeklyMission

User = get_user_model()

def assign_weekly_missions():
    users = User.objects.all()
    missions = list(WeeklyMission.objects.all())

    # 기존 데이터 삭제
    AccountWeeklyMission.objects.all().delete()

    for user in users:
        selected_missions = random.sample(missions, 5)  # 5개 랜덤 추출
        for mission in selected_missions:
            AccountWeeklyMission.objects.create(
                userId=user,
                weeklymissionId=mission,
                status="waiting",
                startedAt=None,
                completedAt=None,
            )