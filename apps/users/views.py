from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
import random
from .models import User, FreelancerProfile, CustomerProfile
from .serializers import UserSerializer, FreelancerProfileSerializer, CustomerProfileSerializer
from .permissions import IsFreelancer, IsCustomer, IsAdmin
from rest_framework import permissions
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer




class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def block(self, request, pk=None):
        user = self.get_object()
        user.is_blocked = True
        user.blocked_reason = request.data.get('reason', '')
        user.save()
        return Response({'status': 'blocked'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def unblock(self, request, pk=None):
        user = self.get_object()
        user.is_blocked = False
        user.blocked_reason = ''
        user.save()
        return Response({'status': 'unblocked'})

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def request_customer_role(self, request):
        user = request.user
        if user.role == 'customer':
            return Response({'error': 'Already customer'}, status=400)
        code = str(random.randint(100000, 999999))
        request.session['verification_code'] = code
        send_mail(
            'Подтверждение роли заказчика',
            f'Ваш код подтверждения: {code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return Response({'message': 'Код отправлен на email'})
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def verify_customer_role(self, request):
        user = request.user
        code = request.data.get('code')
        if code == request.session.get('verification_code'):
            user.role = 'customer'
            user.is_verified = True
            user.save()
            CustomerProfile.objects.get_or_create(user=user, defaults={'company_name': user.username})
            del request.session['verification_code']
            return Response({'status': 'Роль изменена на заказчика'})
        return Response({'error': 'Неверный код'}, status=400)

class FreelancerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = FreelancerProfileSerializer
    permission_classes = [IsFreelancer]

    def get_queryset(self):
        return FreelancerProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CustomerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        return CustomerProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)