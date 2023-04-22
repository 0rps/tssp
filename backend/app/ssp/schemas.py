from app.core.base import ProjectBaseSchema
from app.ssp.constants import GameState
from pydantic import AnyHttpUrl, Field, condecimal


class TeamBaseSchema(ProjectBaseSchema):
    name: str = Field(max_length=32)

    class Config(ProjectBaseSchema.Config):
        orm_mode = True


class TeamCreateBodySchema(TeamBaseSchema):
    api_url: str
    bearer_token: str


class TeamListSchema(TeamBaseSchema):
    id: int


class TeamListReadSchema(TeamBaseSchema):
    budget: float
    revenue: float


class TeamFullReadSchema(TeamListReadSchema):
    has_url: bool
    has_token: bool


class BannerSchema(ProjectBaseSchema):
    w: int
    h: int


class BannerStrictSchema(ProjectBaseSchema):
    w: int = Field(ge=1)
    h: int = Field(ge=1)


class ImpSchema(ProjectBaseSchema):
    banner: BannerStrictSchema


class ProbSchema(ProjectBaseSchema):
    prob: condecimal(ge=0, le=1, max_digits=2, decimal_places=2)


class DomainSchema(ProjectBaseSchema):
    domain: str


class StringIdSchema(ProjectBaseSchema):
    id: str


class BidRequestSchema(ProjectBaseSchema):
    id: str
    imp: ImpSchema
    click: ProbSchema
    conv: ProbSchema
    site: DomainSchema
    ssp: StringIdSchema
    user: StringIdSchema
    bcat: list[str] = list()

    class Config(ProjectBaseSchema.Config):
        orm_mode = True
        allow_population_by_field_name = True


class BidResponseSchema(ProjectBaseSchema):
    external_id: str
    price: float = Field(gt=0)
    image_url: AnyHttpUrl
    cat: list[str] | None


class BidResponseFullSchema(BidResponseSchema):
    team: str
    click: bool
    conversion: bool
    final_pctr: float
    final_pcvr: float
    final_price: float
    image_size: BannerSchema


class LogSchema(ProjectBaseSchema):
    team_name: str
    message: str

    class Config(ProjectBaseSchema.Config):
        orm_mode = True


class TeamStateSchema(TeamBaseSchema):
    budget: float
    score: float
    impressions: int
    clicks: int
    conversions: int


class AdResponseSchema(ProjectBaseSchema):
    round: int
    has_next_round: bool
    bidrequest: BidRequestSchema | None
    bidresponse: BidResponseFullSchema | None
    teams: list[TeamStateSchema]
    logs: list[LogSchema]


class GameStateSchema(ProjectBaseSchema):
    state: GameState
    round: int
    teams: list[TeamStateSchema]


class BaseNotificationSchema(ProjectBaseSchema):
    id: str  # BidRequest.id
    win: bool

    class Config(ProjectBaseSchema.Config):
        orm_mode = True


class LossNotificationSchema(BaseNotificationSchema):
    ...


class WinNotificationSchema(BaseNotificationSchema):
    price: condecimal(ge=0, decimal_places=2)
    click: bool
    conversion: bool
    revenue: int = Field(ge=0)


class CategoryShortSchema(ProjectBaseSchema):
    code: str


class CategorySchema(ProjectBaseSchema):
    id: int
    code: str


class CampaignCreateSchema(ProjectBaseSchema):
    name: str
    budget: int = Field(gt=0)


class CampaignResponseSchema(ProjectBaseSchema):
    id: int
    name: str
    budget: int = Field(gt=0)


class CampaignIdSchema(ProjectBaseSchema):
    id: int


class CampaignShortSchema(ProjectBaseSchema):
    id: int
    name: str | None


class CreativeBaseSchema(ProjectBaseSchema):
    external_id: str
    name: str


class CreativeCreateSchema(CreativeBaseSchema):
    campaign: CampaignIdSchema
    categories: list[CategoryShortSchema]
    file: str


class CreativeResponseSchema(CreativeBaseSchema):
    id: int
    campaign: CampaignShortSchema
    categories: list[CategorySchema]
    url: AnyHttpUrl
