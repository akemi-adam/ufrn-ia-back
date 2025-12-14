from json import loads, dumps
from channels.generic.websocket import AsyncWebsocketConsumer
from docs.factories.documents import DocumentsFactory, QdrantFactory
from docs.strategies.llm import PromptResponseStrategy, NvidiaResponse
from asyncio import sleep
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    '''
    WebSocket para processar as respostas do RAG em tempo real
    '''
    async def connect(self):
        user = self.scope['user']
        if not user or user.is_anonymous:
            await self.close(code=401)
            return
        self.user = user
        self.room_name = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.room_name}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        '''
        Fecha o grupo
        '''
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        '''
        Recebe o dado e envia ele para os membros do grupo
        '''
        if not self.scope["user"].is_authenticated:
            await self.close(code=401)
            return
        data = loads(text_data)
        message = data['message']
        chat_id = data['chat_id']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'chat_id': chat_id
            }
        )

    async def chat_message(self, event):
        '''
        Usa o RAG, devolve a resposta para o cliente e salva a mensagem no banco de dados
        '''
        from chat.models import Chat
        docs_handler: DocumentsFactory = QdrantFactory()
        user_prompt: str = event['message']
        chat_id: int = int(event['chat_id'])
        chat: Chat = await sync_to_async(Chat.objects.get)(id=chat_id, user=self.user)
        messages = await sync_to_async(list)(chat.messages.values('sender', 'content')[:10])
        memory = '\n'.join([f"{m['sender']}: {m['content']}" for m in messages])
        prompt = docs_handler.improve_prompt(user_prompt, memory)
        response_strategy: PromptResponseStrategy = NvidiaResponse()
        response: str = ''
        async for chunk in response_strategy.response(prompt):
            choice = chunk.choices[0].delta
            reasoning = getattr(choice, 'reasoning_content', None)
            content = getattr(choice, 'content', None)
            if reasoning or content:
                await self.send(text_data=dumps({
                    'message': (reasoning or content),
                    'type': 'answer',
                    'done': False
                }))
            await sleep(0.1)
        await self.save_message(chat, response)

    async def save_message(self, chat, content):
        '''
        Salva a mensagem no banco de dados
        '''
        from chat.models import Message
        message = Message(
            chat=chat,
            sender='ia',
            content=content
        )
        await sync_to_async(message.save)()