from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Credenciais inválidas')
        user = authenticate(
            username=user.username,
            password=data['password']
        )
        if not user: raise serializers.ValidationError('Credenciais inválidas')
        data['user'] = user
        return data

