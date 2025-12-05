from mongoengine import Document, StringField, EmailField, DateTimeField
from datetime import datetime

class User(Document):
    name = StringField(required=True, max_length=50)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True, max_length=128)
    created_at = DateTimeField(default=datetime.now)

    meta = {
        "collection": "users"
    }

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_staff(self):
        return False

    @property
    def is_superuser(self):
        return False
