from django.contrib import admin
from .models import *

class MarketAdmin(admin.ModelAdmin):
    list_filter = ['type']  # type 필드 기준으로 필터 추가
    list_display = ['name', 'type']  # 필요한 필드 표시

# Register your models here.
admin.site.register(Market, MarketAdmin)
admin.site.register(FavoriteGroup)
admin.site.register(FavoriteItem)


