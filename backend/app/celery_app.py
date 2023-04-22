import mongoengine as me
from app.core.db import connect_to_db
from app.core.logging import configure_logging
from celery import Celery
from celery.signals import worker_process_init, worker_shutting_down
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

app = Celery("ssp-celery", include=["app.ssp.tasks"])
app.conf.broker_url = "redis://redis:6379/0"
app.conf.task_serializer = "json"
app.conf.worker_hijack_root_logger = False


@worker_process_init.connect
def setup_db(*args, **kwargs):
    connect_to_db()
    configure_logging()


@worker_shutting_down.connect
def shutdown(*args, **kwargs):
    me.disconnect()


@app.task(bind=True)
def debug_task(self):
    logger.info("Request: {0!r}".format(self.request))
    return str(self.request), "123"
