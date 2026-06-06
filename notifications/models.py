from django.db import models
from apps.users.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('in_app', 'В интерфейсе'),
        ('email', 'Email'),
        ('both', 'Оба'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='in_app')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} -> {self.user.username}"

class SavedSearch(models.Model):
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100)
    filters = models.JSONField()  # Хранит параметры поиска: {'category': 1, 'skills': [...], 'budget_min': 100, ...}
    created_at = models.DateTimeField(auto_now_add=True)
    last_notified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Поиск {self.name} от {self.freelancer.username}"