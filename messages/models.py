from mongoengine import Document, StringField, ReferenceField, DateTimeField
from users.models import User
from chat.models import Chat
from datetime import datetime

class Message(Document):
    chat = ReferenceField(Chat, required=True)
    sender = ReferenceField(User, required=False)
    role = StringField(choices=["user", "ia"], required=True)
    content = StringField(required=True)
    created_at = DateTimeField(default=datetime.now)
