import os
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import BaseSettings


class AppSettings(BaseSettings):
    PROJECT_NAME: str = "aca-ssp"
    MONGODB_HOST: str = "mongodb"
    MONGODB_PORT: int = 27017
    MONGODB_DB_NAME: str = "defaultdb"
    MONGO_ROOT_USER: str = "defaultuser"
    MONGO_ROOT_PASSWORD: str = "defaultpassword"
    BUILD_ENV: str = "dev"
    VALID_PASSKEY: str = "test_passkey"
    VALID_PASSWORD: str = "test_password"
    SESSION_COOKIE: str = "passkey"

    class Config:
        env_file = ".env"


@lru_cache()
def get_app_settings():
    return AppSettings()


def get_mongo_uri():
    s = get_app_settings()
    usr = quote_plus(s.MONGO_ROOT_USER)
    pwd = quote_plus(s.MONGO_ROOT_PASSWORD)
    return f"mongodb://{usr}:{pwd}@{s.MONGODB_HOST}:{s.MONGODB_PORT}"


BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BACKEND_DIR, "logs", "server.log")

LOGGING_CFG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "x_request_id": {
            "()": "app.core.logging.RequestIdFilter",
        },
        "x_current_round": {
            "()": "app.core.logging.CurrentRoundFilter",
        },
        "only_super_info": {
            "()": "app.core.logging.OnlySuperInfoFilter",
        },
    },
    "formatters": {
        "web": {
            "class": "logging.Formatter",
            "format": "[%(x_request_id)s] %(levelname)s %(asctime)s [PID:%(process)d] %(message)s",
            "datefmt": '"%Y-%m-%d %H:%M:%S"',
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["x_request_id", "x_current_round"],
            "formatter": "web",
        },
        "file": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": LOG_FILE,
            "formatter": "web",
            "filters": ["x_request_id", "x_current_round"],
            "level": "INFO",
        },
        "mongo": {
            "class": "log4mongo.handlers.MongoHandler",
            "filters": ["x_request_id", "x_current_round", "only_super_info"],
            "level": "SUPERINFO",
            "host": get_mongo_uri(),
            "database_name": get_app_settings().MONGODB_DB_NAME,
        },
    },
    "loggers": {
        "app": {
            "handlers": ["console", "mongo", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "celery": {
            "handlers": ["console", "mongo", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
