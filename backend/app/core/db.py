import datetime

import mongoengine as me
from app.core.base import ProjectBaseDocument
from app.settings import get_app_settings


def connect_to_db():
    settings = get_app_settings()
    me.connect(
        host=settings.MONGODB_HOST,
        port=settings.MONGODB_PORT,
        db=settings.MONGODB_DB_NAME,
        username=settings.MONGO_ROOT_USER,
        password=settings.MONGO_ROOT_PASSWORD,
        alias="default",
    )


class Migrations(ProjectBaseDocument):
    revision = me.StringField(required=True)
    applied_at = me.DateTimeField(default=datetime.datetime.utcnow)
