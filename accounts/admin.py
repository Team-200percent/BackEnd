from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm

User = get_user_model() 

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('개인 정보', {
            'fields': (
                'nickname', 'gender',
                'relocationDate', 'movedInReported', 'residenceType', 'residentCount',
                'localInfrastructure', 'localLivingExperience',
                'cafePreference', 'restaurantPreference', 'sportsLeisurePreference', 'leisureCulturePreference',
            )
        }),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('중요 날짜', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'nickname', 'gender', 'email', 'password1', 'password2',
                'relocationDate', 'movedInReported', 'residenceType', 'residentCount',
                'localInfrastructure', 'localLivingExperience',
                'cafePreference', 'restaurantPreference', 'sportsLeisurePreference', 'leisureCulturePreference',
            ),
        }),
    )

    list_display = ('username', 'nickname', 'gender', 'is_staff')
    search_fields = ('username', 'nickname')
    ordering = ('username',)
