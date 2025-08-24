from rest_framework import serializers
from .models import *
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
        
class AccountLevelMissionSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='levelmissionId.category', read_only=True)
    requireverification = serializers.BooleanField(source='levelmissionId.requireverification', read_only=True)
    reward_xp = serializers.IntegerField(source='levelmissionId.reward_xp', read_only=True)
    
    class Meta:
        model = AccountLevelMission
        fields = "__all__"
        
class AccountWeeklyMissionSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='weeklymissionId.category', read_only=True)
    requireverification = serializers.BooleanField(source='weeklymissionId.requireverification', read_only=True)
    reward_xp = serializers.IntegerField(source='weeklymissionId.reward_xp', read_only=True)
    
    class Meta:
        model = AccountWeeklyMission
        fields = "__all__"