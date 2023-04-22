import mongoengine as me
from app.configurator.constants import AuctionType, GameGoal, GameMode, get_default_game_config
from app.core.base import ProjectBaseDocument


class AdsTxtRow(me.EmbeddedDocument):
    ssp_name = me.StringField(required=True)
    ssp_id = me.StringField(required=True)
    account_type = me.StringField(default="DIRECT")
    publisher_id = me.StringField(required=True)


class GameConfig(ProjectBaseDocument):
    # available for teams, used for DSPs configuration
    auction_type = me.EnumField(AuctionType, required=True)
    mode = me.EnumField(GameMode, required=True)
    impressions_total = me.IntField(min_value=1, required=True, verbose_name="number of auction rounds")
    budget = me.IntField(min_value=1, required=True, verbose_name="initial budget of teams")
    impression_revenue = me.IntField(min_value=0, required=True)
    click_revenue = me.IntField(min_value=0, required=True)
    conversion_revenue = me.IntField(min_value=0, required=True)

    # internal
    game_goal = me.EnumField(GameGoal, required=True)
    current_round = me.IntField(min_value=0, default=0, verbose_name="last played round")

    # features
    blocked_categories_enabled = me.BooleanField(default=False)
    frequency_capping_enabled = me.BooleanField(default=False)
    frequency_capping = me.IntField(min_value=0, default=0)
    ads_txt_enabled = me.BooleanField(default=False)
    ads_txt_cfg = me.ListField(me.EmbeddedDocumentField(AdsTxtRow))

    @classmethod
    def apply_template(cls):
        cls.objects.all().delete()
        default = get_default_game_config()
        return cls.objects.create(
            auction_type=default.GAME_AUCTION_TYPE,
            mode=default.GAME_MODE,
            impressions_total=default.GAME_IMP_TOTAL,
            budget=default.GAME_BUDGET,
            impression_revenue=default.GAME_IMP_REVENUE,
            click_revenue=default.GAME_CLICK_REVENUE,
            conversion_revenue=default.GAME_CONV_REVENUE,
            game_goal=default.GAME_GOAL,
            current_round=0,
            blocked_categories_enabled=default.GAME_BCAT_ENABLED,
            frequency_capping_enabled=default.GAME_FREQ_CAP_ENABLED,
            frequency_capping=default.GAME_IMP_TOTAL,
            ads_txt_enabled=default.GAME_ADS_TXT_ENABLED,
            ads_txt_cfg=[],
        )
