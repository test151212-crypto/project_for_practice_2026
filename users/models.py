from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('freelancer', 'Фрилансер'),
        ('customer', 'Заказчик'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='freelancer')
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True)

    def __str__(self):
        return self.username

class FreelancerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    display_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    experience = models.TextField(blank=True)
    skills = models.JSONField(default=list)          # список строк
    portfolio = models.JSONField(default=list)       # ссылки на работы
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contacts = models.JSONField(default=dict)        # {email, phone, telegram...}
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Профиль {self.user.username}"

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    company_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    contacts = models.JSONField(default=dict)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Компания {self.company_name}"