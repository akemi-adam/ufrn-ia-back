from django.urls import path
from .views import register, login, protected_route

urlpatterns = [
    path("register/", register),
    path("login/", login),
    path("protected/", protected_route),
]
