from django.contrib import admin
from .models import TelegramUser, Channel, Referral, JoinRequest

class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_name', 'username', 'is_admin', 'date_joined', 'last_active')  # Jadval ustunlari
    list_filter = ('is_admin',)  # Filtrlash uchun ustunlar
    search_fields = ('user_id', 'first_name', 'username')  # Qidiruv uchun ustunlar

admin.site.register(TelegramUser, TelegramUserAdmin)

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'url', 'channel_id')  # Jadval ustunlari
    list_filter = ('type',)  # Filtrlash uchun ustunlar
    search_fields = ('name', 'channel_id')  # Qidiruv uchun ustunlar

admin.site.register(Channel, ChannelAdmin)
