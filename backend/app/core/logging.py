import logging.config
from functools import partial, partialmethod
from typing import Optional

from app.core.middleware import x_request_id, x_current_round
from app.settings import LOGGING_CFG

SUPERINFO_LEVEL = 25


class RequestIdFilter(logging.Filter):
    def __init__(self, name: str = "", default_value: Optional[str] = "-"):
        super().__init__(name=name)
        self.default_value = default_value

    def filter(self, record: logging.LogRecord) -> bool:
        record.x_request_id = x_request_id.get(self.default_value)
        return True


class CurrentRoundFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        default_value = ""
        round_value = x_current_round.get(default_value)

        if round_value and not getattr(record, "x_current_round", default_value):
            record.x_current_round = round_value
            record.msg = f"[ROUND: {round_value}] " + record.msg

        return True


class OnlySuperInfoFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == SUPERINFO_LEVEL


def configure_logging():
    logging.SUPERINFO = SUPERINFO_LEVEL
    logging.addLevelName(logging.SUPERINFO, "SUPERINFO")
    logging.getLoggerClass().superinfo = partialmethod(logging.getLoggerClass().log, logging.SUPERINFO)
    logging.superinfo = partial(logging.log, logging.SUPERINFO)

    logging.config.dictConfig(LOGGING_CFG)
