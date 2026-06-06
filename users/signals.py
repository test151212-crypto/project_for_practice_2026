from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import User, FreelancerProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Назначить роль фрилансера по умолчанию
        instance.role = 'freelancer'
        instance.save()
        # Создать пустой профиль фрилансера
        FreelancerProfile.objects.create(
            user=instance,
            display_name=instance.username,
            specialization='',
            skills=[],
            contacts={}
        )
        # Добавить в группу (если используются группы)
        freelancer_group, _ = Group.objects.get_or_create(name='Freelancer')
        instance.groups.add(freelancer_group)