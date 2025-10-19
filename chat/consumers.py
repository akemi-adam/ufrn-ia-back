from json import loads, dumps
from channels.generic.websocket import AsyncWebsocketConsumer
from docs.factories.documents import DocumentsFactory, QdrantFactory
from docs.strategies.llm import PromptResponseStrategy, NvidiaResponse
from asyncio import sleep

class ChatConsumer(AsyncWebsocketConsumer):
    '''
    WebSocket para processar as respostas do RAG em tempo real
    '''
    async def connect(self):
        '''
        Cria um grupo e aceita a conexão
        '''
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
        data = loads(text_data)
        message = data['message']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        '''
        Usa o RAG e devolve a resposta para o cliente
        '''
        docs_handler: DocumentsFactory = QdrantFactory()
        user_prompt: str = event['message']
        prompt = docs_handler.improve_prompt(user_prompt)
        response_strategy: PromptResponseStrategy = NvidiaResponse()

        async for chunk in response_strategy.response(prompt):
            choice = chunk.choices[0].delta
            reasoning = getattr(choice, "reasoning_content", None)
            content = getattr(choice, "content", None)
            if reasoning:
                await self.send(text_data=dumps({
                    'message': reasoning,
                    'type': 'reasoning'
                }))
            if content:
                await self.send(text_data=dumps({
                    'message': content,
                    'type': 'answer'
                }))
            await sleep(0.1)
