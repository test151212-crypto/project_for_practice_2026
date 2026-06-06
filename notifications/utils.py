from .models import Notification
from .tasks import send_email_notification

def send_notification(user, title, message, notification_type='in_app'):
    """
    Универсальная функция отправки уведомления.
    notification_type: 'in_app', 'email', 'both'
    """
    # Создаём запись в БД для in-app уведомлений
    if notification_type in ('in_app', 'both'):
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type
        )
    # Отправляем email, если нужно
    if notification_type in ('email', 'both'):
        send_email_notification.delay(user.email, title, message)