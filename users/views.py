from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken

from .auth import SimpleJWTAuthentication
from .models import User
from .serializers import RegisterSerializer, LoginSerializer

@api_view(["GET"])
@authentication_classes([SimpleJWTAuthentication])
@permission_classes([IsAuthenticated])
def protected_route(request):
    user = request.user
    return Response({
        "message": "Acesso permitido", 
        "user": str(user.id),
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at
    })


@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "Usuário criado com sucesso"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def login(request):
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]

    user = User.objects(email=email).first()
    if not user:
        return Response({"error": "Usuário não encontrado"}, status=404)

    if not check_password(password, user.password):
        return Response({"error": "Senha incorreta"}, status=400)
    
    refresh = RefreshToken.for_user(user)
    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    })

