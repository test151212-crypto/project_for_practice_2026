from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Order, Category
from .serializers import OrderSerializer, CategorySerializer
from .filters import OrderFilter
from apps.users.permissions import IsCustomer, IsModerator, IsAdmin, IsFreelancer
from apps.notifications.utils import send_notification

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['title', 'description']
    ordering_fields = ['published_at', 'budget_min', 'deadline', 'customer__customer_profile__rating']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Order.objects.none()
        if user.role == 'customer':
            return Order.objects.filter(customer=user)
        elif user.role == 'freelancer':
            return Order.objects.filter(status='published')
        elif user.role in ['moderator', 'admin']:
            return Order.objects.all()
        return Order.objects.none()

    def perform_create(self, serializer):
        order = serializer.save(customer=self.request.user, status='moderation')
        # Уведомление модераторам (упрощённо – можно отправить админу)
        # Здесь можно вызвать send_notification для группы модераторов

    def perform_update(self, serializer):
        order = self.get_object()
        if order.customer != self.request.user or order.status not in ['draft', 'rework']:
            raise PermissionError("Нельзя редактировать этот заказ")
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsModerator])
    def request_rework(self, request, pk=None):
        order = self.get_object()
        if order.status != 'moderation':
            return Response({'error': 'Заказ не на модерации'}, status=400)
        order.status = 'rework'
        order.rejection_reason = request.data.get('reason', '')
        order.save()
        send_notification(
            user=order.customer,
            title="Заказ отправлен на доработку",
            message=f"Ваш заказ '{order.title}' требует доработки: {order.rejection_reason}",
            notification_type='in_app'
        )
        return Response({'status': 'rework'})

    @action(detail=True, methods=['post'], permission_classes=[IsModerator])
    def approve(self, request, pk=None):
        order = self.get_object()
        if order.status != 'moderation':
            return Response({'error': 'Заказ не на модерации'}, status=400)
        order.status = 'published'
        order.published_at = timezone.now()
        order.save()
        send_notification(
            user=order.customer,
            title="Заказ опубликован",
            message=f"Ваш заказ '{order.title}' опубликован и доступен фрилансерам",
            notification_type='in_app'
        )
        return Response({'status': 'published'})

    @action(detail=True, methods=['post'], permission_classes=[IsModerator])
    def reject(self, request, pk=None):
        order = self.get_object()
        if order.status != 'moderation':
            return Response({'error': 'Заказ не на модерации'}, status=400)
        order.status = 'rejected'
        order.rejection_reason = request.data.get('reason', '')
        order.save()
        send_notification(
            user=order.customer,
            title="Заказ отклонён",
            message=f"Ваш заказ '{order.title}' отклонён: {order.rejection_reason}",
            notification_type='in_app'
        )
        return Response({'status': 'rejected'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def change_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        allowed_statuses = ['in_work', 'on_review', 'needs_rework', 'completed', 'cancelled']
        if new_status not in allowed_statuses:
            return Response({'error': 'Недопустимый статус'}, status=400)
        # Проверка, что пользователь участник заказа
        is_participant = (order.customer == request.user)
        if not is_participant:
            accepted_response = order.responses.filter(status='accepted').first()
            if accepted_response and accepted_response.freelancer == request.user:
                is_participant = True
        if not is_participant:
            return Response({'error': 'Вы не участник этого заказа'}, status=403)
        order.status = new_status
        order.save()
        # Уведомление другому участнику
        other_user = order.customer if request.user != order.customer else (accepted_response.freelancer if accepted_response else None)
        if other_user:
            send_notification(
                user=other_user,
                title="Статус заказа изменён",
                message=f"Заказ '{order.title}' изменил статус на {order.get_status_display()}",
                notification_type='in_app'
            )
        return Response({'status': 'changed'})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]  # только админ может управлять категориями