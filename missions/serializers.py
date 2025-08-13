from rest_framework import serializers
from .models import LevelMission, WeeklyMission
from accounts.models import User

class LevelMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelMission
        fields = "__all__"
        
        
class WeeklyMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyMission
        fields = "__all__"
        
class MissionCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_xp'] 