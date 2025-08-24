from django.urls import path
from .views import *

urlpatterns = [
    path('levelmission/', AccountLevelMissionView.as_view(), name='account_level_mission'),
    path('levelmission/<int:mission_id>/', AccountLevelMissionView.as_view(), name='account_level_mission'),
    path('levelmission/<int:level>/<int:index>/', LevelMissionDetailView.as_view(), name='level_mission_detail'),
    path('weeklymission/', AccountWeeklyMissionView.as_view(), name='account_weekly_mission'),
    path('weeklymission/<int:weeklymissionid>/', WeeklyMissionDetailView.as_view(), name='weekly_mission_detail'),
    path('levelmissioncomplete/<int:mission_id>/', LevelMissionCompleteView.as_view(), name='level_mission_complete'),
    path('weeklymissioncomplete/<int:weeklymissionid>/', WeeklyMissionCompleteView.as_view(), name='weekly_mission_complete'),
]