from enum import Enum
from functools import lru_cache

from pydantic import BaseSettings


class GameConfSettings(BaseSettings):
    DSP_RESPONSE_TIMEOUT: int = 5  # seconds
    DSP_CONFIG_ENDPOINT: str = "/game/configure/"
    DSP_CAMPAIGNS_ENDPOINT: str = "/api/campaigns/"
    DSP_CREATIVES_ENDPOINT: str = "/api/creatives/"

    class Config:
        env_file = ".env"


@lru_cache()
def get_game_settings():
    return GameConfSettings()


class AuctionType(int, Enum):
    FIRST_PRICE = 1
    SECOND_PRICE = 2


class GameMode(str, Enum):
    FREE = "free"
    SCRIPT = "script"


class GameGoal(str, Enum):
    REVENUE = "revenue"
    CPC = "cpc"


class DefaultGameConfig(BaseSettings):
    GAME_AUCTION_TYPE: int = 1
    GAME_MODE: str = GameMode.SCRIPT.value
    GAME_IMP_TOTAL: int = 10
    GAME_BUDGET: int = 100
    GAME_IMP_REVENUE: int = 5
    GAME_CLICK_REVENUE: int = 12
    GAME_CONV_REVENUE: int = 30
    GAME_GOAL: str = GameGoal.REVENUE.value
    GAME_BCAT_ENABLED: bool = False
    GAME_FREQ_CAP_ENABLED: bool = False
    GAME_ADS_TXT_ENABLED: bool = False

    class Config:
        env_file = ".env"


def get_default_game_config():
    return DefaultGameConfig()
