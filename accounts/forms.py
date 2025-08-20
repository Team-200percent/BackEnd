from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="비밀번호",
        strip=False,
        widget=forms.PasswordInput,
        help_text="비밀번호를 입력하세요.",
    )
    password2 = forms.CharField(
        label="비밀번호 확인",
        strip=False,
        widget=forms.PasswordInput,
        help_text="비밀번호를 다시 한 번 입력하세요.",
    )

    class Meta:
        model = User
        fields = ('username', 'nickname', 'gender')
        
        labels = {
            'username': '사용자 이름',
            'nickname': '닉네임',
            'gender': '성별',
            'user_id': '아이디',
        }