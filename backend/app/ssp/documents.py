import datetime

import mongoengine as me
from app.configurator.constants import GameGoal
from app.configurator.documents import GameConfig
from app.core.base import ProjectBaseDocument
from app.ssp.util import generate_str_id, website_generator


def get_init_budget() -> int:
    from app.configurator.crud import get_game_config

    cfg = get_game_config()
    return cfg.budget


class BannerDocument(me.EmbeddedDocument):
    w = me.IntField(min_value=1, required=True)
    h = me.IntField(min_value=1, required=True)


class ImpDocument(me.EmbeddedDocument):
    banner = me.EmbeddedDocumentField(BannerDocument, required=True)


class ProbDocument(me.EmbeddedDocument):
    prob = me.DecimalField(min_value=0, max_value=1, required=True)


class DomainDocument(me.EmbeddedDocument):
    domain = me.StringField(required=True)


class StringIdDocument(me.EmbeddedDocument):
    id = me.StringField(required=True)


class UserFrequencyCapping(ProjectBaseDocument):
    uid = me.SequenceField(primary_key=True, sequence_name="user_imp_seq", required=True)
    user_id = me.StringField(required=True)
    team_id = me.IntField(required=True)
    creatives_id_list = me.ListField(me.StringField())
    times = me.IntField(default=0)


class Team(ProjectBaseDocument):
    tid = me.SequenceField(primary_key=True, sequence_name="team_id_seq", required=True)
    name = me.StringField(required=True)
    api_url = me.StringField(required=True)
    budget = me.DecimalField(min_value=0, required=True, default=get_init_budget)
    revenue = me.DecimalField(min_value=0, default=0)
    imp_count = me.IntField(default=0)
    click_count = me.IntField(default=0)
    conv_count = me.IntField(default=0)
    bearer_token = me.StringField(default="")
    is_active = me.BooleanField(default=True)

    @me.queryset_manager
    def active(docs_cls, queryset):
        return queryset.filter(is_active=True)

    @property
    def has_url(self) -> bool:
        return bool(self.api_url)

    @property
    def has_token(self) -> bool:
        return bool(self.bearer_token)

    @property
    def score(self) -> float:
        from app.configurator.crud import get_game_config

        game_cfg = get_game_config()
        if not game_cfg:
            return 0
        if game_cfg.game_goal == GameGoal.REVENUE.value:
            return float(self.revenue)
        else:
            spent_budget = game_cfg.budget - self.budget
            return float("{:.2f}".format((spent_budget / self.click_count) if self.click_count else 0))

    @classmethod
    def get_teams_state(cls, teams: list["Team"] | None = None, order_by_score=False) -> list[dict]:
        from app.configurator.crud import get_game_config
        from app.ssp import crud

        game_cfg = get_game_config()

        if not teams:
            teams = crud.get_teams()

        teams_state = [t.get_team_state() for t in teams]

        if order_by_score:
            is_revenue = game_cfg.game_goal == GameGoal.REVENUE.value
            return sorted(
                teams_state,
                key=lambda x: x["score"] if (x["score"] > 0 or is_revenue) else float('inf'),
                reverse=is_revenue,
            )
        else:
            return sorted(teams_state, key=lambda x: x["id"])

    def get_team_state(self) -> dict:
        return dict(
            id=self.id,
            name=self.name,
            budget=self.budget,
            score=self.score,
            impressions=self.imp_count,
            clicks=self.click_count,
            conversions=self.conv_count,
        )


class BidRequestFields:
    imp = me.EmbeddedDocumentField(ImpDocument, required=True)
    click = me.EmbeddedDocumentField(ProbDocument, required=True)
    conv = me.EmbeddedDocumentField(ProbDocument, required=True)
    site = me.EmbeddedDocumentField(DomainDocument, required=True)
    ssp = me.EmbeddedDocumentField(StringIdDocument, required=True)
    user = me.EmbeddedDocumentField(StringIdDocument, required=True)
    bcat = me.ListField(me.StringField())


class BidRequest(BidRequestFields, ProjectBaseDocument):
    rid = me.StringField(primary_key=True, required=True, default=generate_str_id)
    winner = me.ReferenceField(Team)
    round = me.IntField(min_value=1, required=True)
    created_at = me.DateTimeField(default=datetime.datetime.utcnow)


class BidResponse(ProjectBaseDocument):
    external_id = me.StringField()
    price = me.DecimalField()
    image_url = me.URLField()
    cat = me.ListField(me.StringField())
    bid_request = me.ReferenceField(BidRequest)
    team = me.ReferenceField(Team)
    no_bid = me.BooleanField(default=False)
    no_bid_reason = me.StringField()
    created_at = me.DateTimeField(default=datetime.datetime.utcnow)


class Notification(ProjectBaseDocument):
    # both win/loss
    bid_response = me.ReferenceField(BidResponse)
    win = me.BooleanField(required=True)
    # win only
    price = me.DecimalField(min_value=0)
    click = me.BooleanField(default=False)
    conversion = me.BooleanField(default=False)
    revenue = me.IntField(min_value=0)
    # internal
    final_pctr = me.DecimalField(min_value=0, max_value=1)
    final_pcvr = me.DecimalField(min_value=0, max_value=1)
    created_at = me.DateTimeField(default=datetime.datetime.utcnow)


class Website(BidRequestFields, ProjectBaseDocument):
    is_active = me.BooleanField(default=True)

    has_ssp_in_ads_txt = me.BooleanField(default=True)
    ads_txt_data = me.StringField()

    @me.queryset_manager
    def active_sites(docs_cls, queryset):
        return queryset.filter(is_active=True)

    @classmethod
    def get_random_active(cls):
        result = list(
            Website.objects().aggregate(
                [
                    {"$match": {"is_active": True}},
                    {"$sample": {"size": 1}},
                    {"$project": {"_id": 1}},
                ]
            )
        )
        result = result[0] if result else None
        if result:
            return Website.objects.filter(id=result["_id"]).first()

    @classmethod
    def recreate(cls, cfg: GameConfig):
        cls.objects.all().delete()
        for domain, w, h, click, conv, ssp_id, user_id, bcat, has_ssp_in_ads_txt, ads_txt_data in website_generator(cfg):
            Website.objects.create(
                imp=dict(banner=dict(w=w, h=h)),
                click=dict(prob=click),
                conv=dict(prob=conv),
                site=dict(domain=domain),
                ssp=dict(id=ssp_id),
                user=dict(id=user_id),
                bcat=bcat,
                has_ssp_in_ads_txt=has_ssp_in_ads_txt,
                ads_txt_data=ads_txt_data,
            )


class GameLog(ProjectBaseDocument):
    team_id = me.IntField()
    team_name = me.StringField()
    bid_request_id = me.StringField()
    message = me.StringField()
    created_at = me.DateTimeField(default=datetime.datetime.utcnow)

    @classmethod
    def _log(cls, *, team_obj: Team, bid_request_id: str, msg: str):
        cls.objects.create(team_id=team_obj.id, team_name=team_obj.name, bid_request_id=bid_request_id, message=msg)
        return msg

    @classmethod
    def log_nobid_reason(cls, team_obj: Team, bid_request_id: str, **kwargs):
        msg = f"Nobid: {kwargs['reason']}"
        return cls._log(team_obj=team_obj, bid_request_id=bid_request_id, msg=msg)

    @classmethod
    def log_price(cls, team_obj: Team, bid_request_id: str, **kwargs):
        msg = f"Bid response: price {kwargs['price']}"
        return cls._log(team_obj=team_obj, bid_request_id=bid_request_id, msg=msg)

    @classmethod
    def log_winner(cls, team_obj: Team, bid_request_id: str, **kwargs):
        msg = f"is winner: bid price = {kwargs['price']}"
        return cls._log(team_obj=team_obj, bid_request_id=bid_request_id, msg=msg)

    @classmethod
    def log_bad_image(cls, team_obj: Team, bid_request_id: str, **kwargs):
        msg = f"Could not download image"
        return cls._log(team_obj=team_obj, bid_request_id=bid_request_id, msg=msg)

    @classmethod
    def log_penalty_reason(cls, team_obj: Team, bid_request_id: str, **kwargs):
        msg = f"Penalty: {kwargs['reason']}"
        return cls._log(team_obj=team_obj, bid_request_id=bid_request_id, msg=msg)

    @classmethod
    def get_round_logs(cls, bid_request_id=bid_request_id):
        return GameLog.objects.filter(bid_request_id=bid_request_id).order_by("created_at")
