from mongoengine import Document, StringField, ReferenceField, DateTimeField, ListField
from users.models import User
from datetime import datetime

class Chat(Document):
    user = ReferenceField(User, required=True)
    title = StringField(required=True)
    created_at = DateTimeField(default=datetime.now)
