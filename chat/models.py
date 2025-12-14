from django.db.models import Model, CharField, TextField, DateTimeField, ForeignKey, CASCADE


class Chat(Model):
    title = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    user = ForeignKey('auth.User', on_delete=CASCADE, related_name='chats')

    def __str__(self):
        return self.title


class Message(Model):
    chat = ForeignKey(Chat, on_delete=CASCADE, related_name='messages')
    sender = CharField(max_length=255)
    content = TextField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.sender}: {self.content[:50]}'