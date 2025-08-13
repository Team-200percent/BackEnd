from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('개인 정보', {'fields': ('nickname','user_id', 'gender', 'email')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('중요 날짜', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nickname', 'gender', 'user_id', 'password1', 'password2'),
        }),
    )

    list_display = ('username', 'nickname', 'gender', 'is_staff')
    search_fields = ('username', 'nickname')
    ordering = ('username',)

admin.site.register(User, CustomUserAdmin)