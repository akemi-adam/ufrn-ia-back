from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from chat.models import Chat, Message
from chat.serealizers import ChatSerializer, ChatCreateSerializer, MessageSerializer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.luhn import LuhnSummarizer

class ChatView(ModelViewSet):
    '''
    ViewSet para listar e criar chats
    '''
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user).order_by('-updated_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ChatCreateSerializer
        return ChatSerializer
    
    def create(self, request, *args, **kwargs):
        # Trocar essa lógica por um serviço
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = request.data.get('message')
        parser = PlaintextParser.from_string(message, Tokenizer("portuguese"))
        summarizer = LuhnSummarizer()
        title = summarizer(parser.document, 1)
        chat = Chat()
        chat.title = ' '.join([str(sentence) for sentence in title])
        chat.user = request.user
        chat.save()
        chat.messages.create(
            sender='user',
            content=message
        )
        response = ChatSerializer(chat)
        return Response(
            response.data,
            status=status.HTTP_201_CREATED
        )
    

class MessageViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    '''
    ViewSet para listar, recuperar e criar mensagens
    '''
    queryset = Message.objects.all().order_by('-created_at')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # import logging
        messages = Chat.objects.get(id=serializer.data['chat']).messages
        # logging.warning(f"Mensagem criada: {messages}")
        print(f"Mensagem criada: {messages}")
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def messages_by_chat(request, chat_id):
    '''
    Retorna as mensagens de um chat específico
    '''
    messages = Message.objects.filter(chat_id=chat_id).order_by('created_at')
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def first_message_by_chat(request, chat_id):
    '''
    Retorna a primeira mensagem de um chat específico
    '''
    try:
        message = Message.objects.filter(chat_id=chat_id).earliest('created_at')
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Message.DoesNotExist:
        return Response({"detail": "Message not found."}, status=status.HTTP_404_NOT_FOUND)