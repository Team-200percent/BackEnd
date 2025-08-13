from django.urls import path
from .views import *

urlpatterns = [
    path('levelmission/<int:level>/<int:index>/', LevelMissionDetailView.as_view(), name='level_mission_detail'),
    path('weeklymission/', WeeklyMissionDetailView.as_view(), name='weekly_mission_detail'),
    path('levelmissioncommplete/', LevelMissionCompleteView.as_view(), name='level_mission_complete'),
    path('weeklymissioncommplete/', WeeklyMissionCompleteView.as_view(), name='weekly_mission_complete'),
]