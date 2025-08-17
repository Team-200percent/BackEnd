from django.urls import path
from .views import *

urlpatterns = [
    path('levelmission/', AccountLevelMissionView.as_view(), name='account_level_mission'),
    path('levelmission/<int:level>/<int:index>/', LevelMissionDetailView.as_view(), name='level_mission_detail'),
    path('weeklymission/', AccountWeeklyMissionView.as_view(), name='account_weekly_mission'),
    path('weeklymission/<int:weeklymissionid>/', WeeklyMissionDetailView.as_view(), name='weekly_mission_detail'),
    
    path('levelmissioncommplete/', LevelMissionCompleteView.as_view(), name='level_mission_complete'),
    path('weeklymissioncommplete/', WeeklyMissionCompleteView.as_view(), name='weekly_mission_complete'),
]