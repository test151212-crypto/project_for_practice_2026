from django.contrib import admin
from .models import Notification, SavedSearch

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'is_read', 'notification_type', 'created_at')
    list_filter = ('is_read', 'notification_type', 'created_at')
    search_fields = ('title', 'message')

@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('id', 'freelancer', 'name', 'created_at', 'last_notified_at')
    search_fields = ('name',)