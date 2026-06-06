from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Response, Review, Complaint
from .serializers import ResponseSerializer, ReviewSerializer, ComplaintSerializer
from apps.users.permissions import IsFreelancer, IsCustomer, IsModerator
from apps.orders.models import Order
from apps.notifications.utils import send_notification

class ResponseViewSet(viewsets.ModelViewSet):
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'freelancer':
            return Response.objects.filter(freelancer=user)
        elif user.role == 'customer':
            return Response.objects.filter(order__customer=user)
        elif user.role in ['moderator', 'admin']:
            return Response.objects.all()
        return Response.objects.none()

    def perform_create(self, serializer):
        order_id = self.request.data.get('order')
        order = get_object_or_404(Order, id=order_id, status='published')
        # Проверяем, нет ли уже принятого отклика
        if order.responses.filter(status='accepted').exists():
            raise PermissionError("На этот заказ уже выбран исполнитель")
        response = serializer.save(freelancer=self.request.user, order=order)
        # Уведомление заказчику
        send_notification(
            user=order.customer,
            title="Новый отклик",
            message=f"Фрилансер {self.request.user.username} откликнулся на ваш заказ '{order.title}'",
            notification_type='in_app'
        )
        # Уведомление фрилансеру (подтверждение)
        send_notification(
            user=self.request.user,
            title="Отклик отправлен",
            message=f"Вы откликнулись на заказ '{order.title}'",
            notification_type='in_app'
        )

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        response = self.get_object()
        user = request.user
        if user.role != 'customer' or response.order.customer != user:
            return Response({'error': 'Только заказчик может принять отклик'}, status=403)
        if response.status != 'sent':
            return Response({'error': 'Отклик нельзя принять'}, status=400)
        response.status = 'accepted'
        response.save()
        response.order.status = 'in_work'
        response.order.save()
        # Отклоняем остальные отклики
        Response.objects.filter(order=response.order).exclude(pk=response.pk).update(status='rejected')
        # Уведомления
        send_notification(
            user=response.freelancer,
            title="Отклик принят",
            message=f"Ваш отклик на заказ '{response.order.title}' принят. Можете начинать работу.",
            notification_type='in_app'
        )
        send_notification(
            user=response.order.customer,
            title="Исполнитель выбран",
            message=f"Вы приняли отклик от {response.freelancer.username} на заказ '{response.order.title}'",
            notification_type='in_app'
        )
        return Response({'status': 'accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        response = self.get_object()
        if request.user.role != 'customer' or response.order.customer != request.user:
            return Response({'error': 'Только заказчик может отклонить отклик'}, status=403)
        if response.status not in ['sent', 'viewed']:
            return Response({'error': 'Отклик нельзя отклонить'}, status=400)
        response.status = 'rejected'
        response.save()
        send_notification(
            user=response.freelancer,
            title="Отклик отклонён",
            message=f"Ваш отклик на заказ '{response.order.title}' отклонён заказчиком.",
            notification_type='in_app'
        )
        return Response({'status': 'rejected'})

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        response = self.get_object()
        if request.user.role != 'freelancer' or response.freelancer != request.user:
            return Response({'error': 'Только автор может отозвать отклик'}, status=403)
        if response.status in ['accepted', 'rejected']:
            return Response({'error': 'Нельзя отозвать принятый или отклонённый отклик'}, status=400)
        response.status = 'withdrawn'
        response.save()
        send_notification(
            user=response.order.customer,
            title="Отклик отозван",
            message=f"Фрилансер {request.user.username} отозвал свой отклик на заказ '{response.order.title}'",
            notification_type='in_app'
        )
        return Response({'status': 'withdrawn'})

    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        response = self.get_object()
        if request.user.role != 'customer' or response.order.customer != request.user:
            return Response({'error': 'Только заказчик может отметить просмотр'}, status=403)
        if response.status == 'sent':
            response.status = 'viewed'
            response.viewed_at = timezone.now()
            response.save()
        return Response({'status': 'viewed'})

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Review.objects.filter(author=user) | Review.objects.filter(target=user)

    def perform_create(self, serializer):
        order_id = self.request.data.get('order')
        order = get_object_or_404(Order, id=order_id)
        if order.status != 'completed':
            raise PermissionError("Отзыв можно оставить только после завершения заказа")
        # Проверка, что пользователь участвовал
        if self.request.user != order.customer and not order.responses.filter(freelancer=self.request.user, status='accepted').exists():
            raise PermissionError("Вы не участвовали в этом заказе")
        target_id = self.request.data.get('target')
        target = get_object_or_404(User, id=target_id)
        # Проверка, что target - другой участник
        if self.request.user == target:
            raise PermissionError("Нельзя оставить отзыв на самого себя")
        serializer.save(author=self.request.user)

class ComplaintViewSet(viewsets.ModelViewSet):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'moderator' or user.is_superuser:
            return Complaint.objects.all()
        return Complaint.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsModerator])
    def resolve(self, request, pk=None):
        complaint = self.get_object()
        complaint.resolved = True
        complaint.resolution_note = request.data.get('note', '')
        complaint.save()
        return Response({'status': 'resolved'})