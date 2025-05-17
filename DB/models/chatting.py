import uuid
from mongoengine import DateTimeField, StringField, ListField, BooleanField, ReferenceField, CASCADE, Document, \
    UUIDField, DictField
from datetime import datetime, timezone


class Chat(Document):
    chat_id = UUIDField(
        default=uuid.uuid4,
        unique=True,
        required=True,
        description="Unique chat identifier (UUID)",
        binary=False
    )
    participants = ListField(
        StringField(),
        required=True,
        description="List of participant user UUIDs as strings"
    )
    is_group = BooleanField(
        default=False,
        description="Indicates if the chat is a group chat"
    )
    unread_message_counts = DictField(
        default=dict,
        description="Dictionary mapping participant UUIDs to their unread message count"
    )
    created_at = DateTimeField(
        required=True,
        default=lambda: datetime.now(timezone.utc),
        description="Timestamp when the chat was created"
    )
    updated_at = DateTimeField(
        required=True,
        default=lambda: datetime.now(timezone.utc),
        description="Timestamp when the chat was last updated"
    )

    meta = {
        'collection': 'chats',
        'indexes': [
            {'fields': ['participants', 'updated_at']},  # Compound index for efficient querying
            'chat_id',  # Unique index on chat_id
            'is_group',  # Index on is_group
            'created_at'  # Index on created_at
        ]
    }


class ChatMessage(Document):
    message_id = UUIDField(
        default=uuid.uuid4,
        unique=True,
        required=True,
        description="Unique message identifier (UUID)",
        binary=False
    )
    chat = ReferenceField(
        Chat,
        reverse_delete_rule=CASCADE,
        required=True,
        description="Reference to the associated Chat"
    )
    sender_id = StringField(
        required=True,
        description="User UUID of the message sender"
    )
    content = StringField(
        required=True,
        description="Text content of the message"
    )
    created_at = DateTimeField(
        required=True,
        default=lambda: datetime.now(timezone.utc),
        description="Timestamp when the message was created"
    )
    deleted = BooleanField(
        default=False,
        description="Flag to indicate if the message is deleted"
    )

    read_by = ListField(
        StringField(),
        default=list,
        description="List of participant UUIDs who have read the message"
    )

    meta = {
        'collection': 'chat_messages',
        'indexes': [
            ('chat', 'created_at'),  # Compound index for efficient message retrieval
            'message_id',  # Unique index on message_id
            'sender_id',  # Index on sender_id
            'deleted',  # Index on deleted flag
            'read_by'  # Index on read_by for efficient queries
        ]
    }
