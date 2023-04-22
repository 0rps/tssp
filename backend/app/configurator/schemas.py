from app.configurator.constants import AuctionType, GameGoal, GameMode
from app.core.base import ProjectBaseSchema
from pydantic import Field


class GameCfgBase(ProjectBaseSchema):
    auction_type: AuctionType
    mode: GameMode
    game_goal: GameGoal
    impressions_total: int = Field(gt=0)
    budget: int = Field(gt=0)
    impression_revenue: int = Field(ge=0)
    click_revenue: int = Field(ge=0)
    conversion_revenue: int = Field(ge=0)
    frequency_capping: int = Field(default=0, ge=0)

    class Config(ProjectBaseSchema.Config):
        orm_mode = True


class GameCfgDSPSchema(GameCfgBase):
    pass


class GameCfgSSPSchema(GameCfgBase):
    blocked_categories_enabled: bool = False
    frequency_capping_enabled: bool = False
    ads_txt_enabled: bool = False


class SetDspConfigRespSchema(ProjectBaseSchema):
    errors: list[str]


class TestRespSchema(SetDspConfigRespSchema):
    status_code: str
    content: str
