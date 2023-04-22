from enum import Enum
from functools import lru_cache

from pydantic import BaseSettings

SCALED_BANNER_SIZE_PROB = 0.1
RANDOM_BANNER_SIZE_PROB = 0.1
BCAT_RATE = 0.2

THE_SAME_USER_ID = "THE_SAME_USER_ID"
SSP_ID = "eeb7e854a053d23467d36dda1592ee76"  # "the best ssp ever" | md5sum


class SSPSettings(BaseSettings):
    DSP_BID_ENDPOINT: str = "/rtb/bid/"
    DSP_NOTIFY_ENDPOINT: str = "/rtb/notify/"

    WRONG_SIZE_CLICK_FINE: float = 0.05  # decrease click probability
    WRONG_SIZE_CONVERSION_FINE: float = 0.03  # decrease conversion probability
    FREQUENCY_CAPPING_CLICK_FINE: float = 0.05  # decrease click probability

    USERID_GENERATION_PROBABILITY: float = 0.999
    ADSTXT_GENERATION_PROBABILITY: float = 0.8

    ADD_ONE_BLOCKED_CATEGORY: float = 0.3
    ADD_SECOND_BLOCKED_CATEGORY: float = 0.2

    IGNORE_PROMETHEUS_ERRORS: bool = True
    PROMETHEUS_URL = "http://prometheus:9090"

    class Config:
        env_file = ".env"


@lru_cache()
def get_ssp_settings():
    return SSPSettings()


class GameState(str, Enum):
    NEW_GAME = "new_game"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
