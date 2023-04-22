import mongoengine as me
from app.configurator.documents import GameConfig
from app.ssp.constants import GameState
from app.ssp.documents import BidRequest, Team, Website, UserFrequencyCapping
from app.ssp.schemas import TeamCreateBodySchema


def get_teams(**fltr_kwargs) -> me.QuerySet:
    return Team.active().filter(**fltr_kwargs).order_by("tid")


def create_team(team: TeamCreateBodySchema) -> Team:
    return Team.objects.create(**team.dict())


def delete_team(team_id: int) -> None:
    return Team.objects.filter(tid=team_id).delete()


def create_bid_request(cur_round: int, website: Website) -> BidRequest:
    website_data = website.to_mongo().to_dict()
    website_data.pop("_id", None)
    website_data.pop("is_active", None)
    website_data.pop("has_ssp_in_ads_txt", None)
    website_data.pop("ads_txt_data", None)

    bid_request = BidRequest.objects.create(round=cur_round, **website_data)
    return bid_request


def calculate_game_state(game_cfg: GameConfig, teams: list[Team]) -> dict:
    from app.ssp import services

    if not game_cfg:
        return {
            "state": GameState.NEW_GAME,
            "round": 0,
            "teams": Team.get_teams_state(teams),
        }

    if game_cfg.current_round == 0:
        state = GameState.NEW_GAME
    elif not services.check_next_round(game_cfg):
        state = GameState.FINISHED
    else:
        state = GameState.IN_PROGRESS

    return dict(
        state=state,
        round=game_cfg.current_round,
        teams=Team.get_teams_state(teams, order_by_score=True),
    )


def reset_current_game() -> GameConfig:
    from app.configurator.crud import get_game_config
    
    cfg = get_game_config()
    cfg.current_round = 0
    cfg.save()

    # TODO (LOW): remove all freq caps and do the same thing as save config does
    Website.recreate(cfg)
    Team.objects.all().update(
        set__budget=cfg.budget, set__revenue=0, set__imp_count=0, set__click_count=0, set__conv_count=0
    )
    return cfg
