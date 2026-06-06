import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.orders.models import Order
from .models import ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'chat_{self.order_id}'
        user = self.scope['user']

        # Проверка аутентификации
        if not user.is_authenticated:
            await self.close()
            return

        # Проверка, что пользователь участвует в заказе
        if not await self.is_participant(user):
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message', '')
        file_data = data.get('file_attachment', {})

        user = self.scope['user']
        # Сохраняем сообщение в БД
        saved_msg = await self.save_message(user, message_text, file_data)

        # Отправляем всем в группу
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'username': user.username,
                'user_id': user.id,
                'created_at': saved_msg.created_at.isoformat(),
                'file_attachment': saved_msg.file_attachment,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def is_participant(self, user):
        try:
            order = Order.objects.get(id=self.order_id)
        except Order.DoesNotExist:
            return False
        # Заказчик или принятый фрилансер
        if order.customer == user:
            return True
        accepted_response = order.responses.filter(status='accepted').first()
        if accepted_response and accepted_response.freelancer == user:
            return True
        return False

    @database_sync_to_async
    def save_message(self, user, text, file_attachment):
        order = Order.objects.get(id=self.order_id)
        return ChatMessage.objects.create(
            order=order,
            author=user,
            text=text,
            file_attachment=file_attachment
        )