from rest_framework import serializers
from .models import User

class MypageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "nickname", "gender", "created", "user_level", "user_xp", "user_completedmissions"]