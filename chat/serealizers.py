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


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'updated_at']
        
    def validate_sender(self, value):
        if value not in ['user', 'ia']:
            raise serializers.ValidationError("O campo 'sender' deve ser 'user' ou 'ia'.")
        return value
    
    def validate_chat(self, value):
        if not Chat.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("O chat especificado não existe.")
        return value
    