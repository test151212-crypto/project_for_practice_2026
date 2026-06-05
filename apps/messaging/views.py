from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ChatMessage
from .serializers import ChatMessageSerializer

class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Возвращаем сообщения из заказов, где пользователь является участником
        # Заказы, где пользователь - заказчик
        customer_orders = user.orders.values_list('id', flat=True)
        # Заказы, где пользователь - принятый фрилансер
        freelancer_orders = user.responses.filter(status='accepted').values_list('order_id', flat=True)
        order_ids = set(customer_orders) | set(freelancer_orders)
        return ChatMessage.objects.filter(order_id__in=order_ids).order_by('-created_at')