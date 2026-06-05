from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Review
from apps.users.models import User
from django.db.models import Avg

@receiver(post_save, sender=Review)
def update_user_rating(sender, instance, **kwargs):
    target = instance.target
    # Вычисляем средний рейтинг
    avg_rating = Review.objects.filter(target=target).aggregate(Avg('rating'))['rating__avg']
    total = Review.objects.filter(target=target).count()
    # Обновляем профиль в зависимости от роли
    if hasattr(target, 'freelancer_profile'):
        target.freelancer_profile.rating = avg_rating or 0
        target.freelancer_profile.total_reviews = total
        target.freelancer_profile.save()
    if hasattr(target, 'customer_profile'):
        target.customer_profile.rating = avg_rating or 0
        target.customer_profile.total_reviews = total
        target.customer_profile.save()