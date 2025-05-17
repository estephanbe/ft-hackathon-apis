from datetime import datetime

from passlib.hash import bcrypt
from mongoengine import (
    Document,
    EmbeddedDocument,
    StringField,
    EmailField,
    ReferenceField,
    ListField,
    EmbeddedDocumentField,
    FloatField,
    BooleanField,
    IntField,
    DateTimeField,
    CASCADE,
)


# ——— Users Collection ———
class User(Document):
    meta = {'collection': 'users'}
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)  # to be moved to blockchain
    role = StringField(required=True, choices=("OM", "DISCIPLE"))
    om_ref = ReferenceField('User')  # points to the OM who invited this disciple

    # disciple-specific profile
    location = StringField()
    language = StringField()
    dialect = StringField()
    spiritual_level = IntField(min_value=0, max_value=5)
    trust_score = FloatField(default=50.0, min_value=0.0, max_value=100.0)
    is_removed = BooleanField(default=False)  # OM “soft delete”
    created_at = DateTimeField(default=datetime.utcnow)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)


class OneTimeCode(Document):
    code = StringField(required=True, unique=True, regex=r"^\d{6}$")
    om = ReferenceField(User, required=True)  # OM who issued it
    expires_at = DateTimeField(required=True)
    claimed_by = ReferenceField(User)  # null until used
    created_at = DateTimeField(default=datetime.utcnow)


# ——— Embedded Member Sub-Document ———
class CircleMember(EmbeddedDocument):
    user = ReferenceField(User, required=True)  # <-- Removed reverse_delete_rule
    trust_score = FloatField(default=0.0, min_value=0.0, max_value=100.0)
    is_flagged = BooleanField(default=False)
    flag_score = IntField(default=0)
    connection_date = DateTimeField(default=datetime.utcnow)
    relationship_type = StringField(choices=("NONE", "VIRTUAL", "IN_PERSON"), default="NONE")
    last_trust_change_desc = StringField()  # explanation when drop ≥ 25 %


# ——— Circles Collection ———
class Circle(Document):
    meta = {'collection': 'circles'}

    owner = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    members = ListField(EmbeddedDocumentField(CircleMember), default=[])
    created_at = DateTimeField(default=datetime.utcnow)
