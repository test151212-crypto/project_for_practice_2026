from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'author', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')