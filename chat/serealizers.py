from rest_framework import serializers
from chat.models import Chat, Message

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'title', 'user', 'updated_at']


class ChatCreateSerializer(serializers.Serializer):
    message = serializers.CharField(
        write_only=True,
        max_length=1000,
        style={'base_template': 'textarea.html'},
    )
    
    class Meta:
        fields = '__all__'

