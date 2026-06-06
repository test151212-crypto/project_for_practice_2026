from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    order_title = serializers.CharField(source='order.title', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ('id', 'order', 'order_title', 'author', 'author_name', 'text',
                  'file_attachment', 'created_at', 'is_read')
        read_only_fields = ('author', 'created_at', 'is_read')