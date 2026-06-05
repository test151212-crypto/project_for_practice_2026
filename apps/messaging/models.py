from django.db import models
from apps.users.models import User
from apps.orders.models import Order

class ChatMessage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    text = models.TextField()
    file_attachment = models.JSONField(default=dict)  # {'filename': 'file.pdf', 'url': '...', 'size': 12345}
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Сообщение от {self.author.username} в заказе {self.order.id}"