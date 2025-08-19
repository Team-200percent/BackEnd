from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from reviews.models import Review

# 회원가입용
class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    nickname = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'nickname']
    
    # create() 재정의
    def create(self, validated_data):
    
        # 비밀번호 분리
        password = validated_data.pop('password')

        # user 객체 생성
        user = User(**validated_data)

        # 비밀번호는 해싱해서 저장
        user.set_password(password)
        user.save()

        return user
   

# 로그인용
class AuthSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'password']
        
    # 로그인 유효성 검사 함수
    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)
		    
		# username으로 사용자 찾는 모델 함수
        user = User.get_user_by_username(username=username)
        
        # 존재하는 회원인지 확인
        if user is None:
            raise serializers.ValidationError("User does not exist.")
        else:
		    # 비밀번호 일치 여부 확인
            if not user.check_password(password):
                raise serializers.ValidationError("Wrong password.")
        
        token = RefreshToken.for_user(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        data = {
            "user": user,
            "refresh_token": refresh_token,
            "access_token": access_token,
        }

        return data


# 마이페이지 정보용 
class MypageSerializer(serializers.ModelSerializer):
    review_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["username", "nickname", "gender", "created", 
                "user_level", "user_xp", 
                "review_count", "following_count", "follower_count", "user_completedmissions"]
        
    def get_review_count(self, obj):
        return Review.objects.filter(user=obj).count()
    
    def get_following_count(self, obj):
        return obj.following.count()

    def get_follower_count(self, obj):
        return obj.followers.count()
    
class UserPreferenceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["cafePreference", "restaurantPreference", "sprotsLeisurePreference", "leisureCulturePreference"]


class FollowSerializer(serializers.Serializer):
    nickname = serializers.CharField()

    def validate(self, attrs):
        request = self.context["request"]
        me = request.user
        nickname = attrs["nickname"]

        target = User.objects.get(nickname__iexact=nickname)

        if target == me:
            raise serializers.ValidationError({"nickname": "자기 자신을 팔로우할 수 없습니다."})

        attrs["target"] = target
        return attrs

    def create(self, validated_data):
        me = self.context["request"].user
        target = validated_data["target"]
        follow, created = Follow.objects.get_or_create(follower=me, following=target)
        return follow
    
class FollowNumSerializer(serializers.Serializer):
    following_count = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_follower_count(self, obj):
        return obj.followers.count()