from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    chat = serializers.CharField()
    sender = serializers.CharField(allow_null=True, required=False)
    role = serializers.CharField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Message(**validated_data).save()

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
