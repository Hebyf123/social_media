from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Chat, Message,Notification
from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'
        self.user = self.scope['user']

        
        chat = await self.get_chat(self.chat_id)
        
    
        already_connected = False

        if chat.is_group:
            invite_link = self.scope['url_route']['kwargs'].get('invite_link')
            if invite_link and await self.is_invited_to_chat(chat, invite_link):
                await self.add_user_to_chat(chat, self.user)
                already_connected = True  
            else:
                
                if await self.is_user_in_chat(chat, self.user.id):
                    already_connected = True 
                else:
                    raise DenyConnection("Access denied")
        else:
         
            if await self.is_user_in_chat(chat, self.user.id):
                already_connected = True 
            else:
                raise DenyConnection("Access denied")

     
        if not already_connected:
            await self.accept()
        
        # Добавляем пользователя в группу
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        media = data.get('media')  
        action = data.get('action')  # 'send', 'edit', or 'delete'
        user = self.scope['user']

        # Handle actions
        if action == 'send':
            chat = await self.get_chat(self.chat_id)
            new_message = await self.save_message(chat, user, message, media)
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'message': new_message.content,
                    'user': user.username,
                    'timestamp': str(new_message.timestamp),
                    'media': new_message.media,  
                }
            )
        elif action == 'edit':
            message_id = data.get('message_id')
            updated_content = data.get('updated_content')
            await self.update_message_content(message_id, updated_content)
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'edit_message',
                    'message_id': message_id,
                    'updated_content': updated_content,
                }
            )
        elif action == 'delete':
            message_id = data.get('message_id')
            await self.delete_message(message_id)
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'delete_message',
                    'message_id': message_id,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'user': event['user'],
            'timestamp': event['timestamp'],
            'media': event['media'],  
        }))

    async def edit_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'edit',
            'message_id': event['message_id'],
            'updated_content': event['updated_content'],
        }))

    async def delete_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'delete',
            'message_id': event['message_id'],
        }))

    @database_sync_to_async
    def get_chat(self, chat_id):
        return Chat.objects.get(pk=chat_id)

    @database_sync_to_async
    def is_user_in_chat(self, chat, user_id):
        return chat.users.filter(id=user_id).exists()

    @database_sync_to_async
    def save_message(self, chat, user, message, media=None):
        return Message.objects.create(chat=chat, sender=user, content=message, media=media)

    @database_sync_to_async
    def update_message_content(self, message_id, updated_content):
        message = Message.objects.get(id=message_id)
        message.content = updated_content
        message.save()

    @database_sync_to_async
    def delete_message(self, message_id):
        if type(message_id) != int:
            message_id1 = message_id['message_id'] 
            Message.objects.filter(id=message_id1).delete()
        else:
            Message.objects.filter(id=message_id).delete()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'notifications_{self.user_id}'


        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
  
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        notification = text_data_json['notification']

        await self.send(text_data=json.dumps({
            'notification': notification
        }))


    async def send_notification(self, event):
        notification = event['notification']

        await self.send(text_data=json.dumps({
            'notification': notification
        }))
