from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ChatView, MessageViewSet, messages_by_chat, first_message_by_chat

router = DefaultRouter()
router.register(r'chats', ChatView, basename='chat')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = router.urls

urlpatterns += [
    path('chats/<int:chat_id>/messages/', messages_by_chat, name='messages-by-chat'),
    path('chats/<int:chat_id>/messages/first/', first_message_by_chat, name='first-message-by-chat'),
]