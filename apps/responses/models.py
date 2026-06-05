from django.db import models
from simple_history.models import HistoricalRecords
from apps.users.models import User
from apps.orders.models import Order

class Response(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Отправлен'),
        ('viewed', 'Просмотрен'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонён'),
        ('withdrawn', 'Отозван'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='responses')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    message = models.TextField()
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    proposed_deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    sent_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('order', 'freelancer')  # один активный отклик на заказ

    def __str__(self):
        return f"Отклик {self.freelancer.username} на {self.order.title}"

class Review(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveSmallIntegerField()  # 1-5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('order', 'author', 'target')

    def __str__(self):
        return f"Отзыв от {self.author.username} о {self.target.username}"

class Complaint(models.Model):
    TYPE_CHOICES = (
        ('order', 'Заказ'),
        ('user', 'Пользователь'),
        ('external_order', 'Внешний заказ'),
    )
    complaint_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    object_id = models.PositiveIntegerField()
    reason = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    resolved = models.BooleanField(default=False)
    resolution_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Жалоба на {self.complaint_type} #{self.object_id}"