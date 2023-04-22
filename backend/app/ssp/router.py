import logging

from app.configurator.constants import GameMode
from app.configurator.crud import (
    get_game_config,
    send_cfg_to_dsps,
    set_dsp_campaigns,
    set_dsp_creatives,
)
from app.configurator.documents import GameConfig
from app.core.middleware import x_current_round
from app.ssp import crud, services
from app.ssp.dependencies import get_random_website, get_team, get_teams
from app.ssp.documents import GameLog, Team, Website
from app.ssp.schemas import (
    AdResponseSchema,
    GameStateSchema,
    TeamCreateBodySchema,
    TeamListSchema,
)

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import Response

from . import metrics
from app.metrics import reset_metrics

logger = logging.getLogger(__name__)

ssp_router = r = APIRouter()


@r.post("/game/adrequest/", tags=["game"], response_model=AdResponseSchema, status_code=200)
async def get_advertisement(
    game_cfg: GameConfig = Depends(get_game_config),
    website: Website = Depends(get_random_website),
    teams: list[Team] = Depends(get_teams),
):

    now_playing_round = game_cfg.current_round + 1
    x_current_round.set(now_playing_round)
    if now_playing_round == 1:
        if game_cfg.mode == GameMode.SCRIPT.value:
            result = await set_dsp_campaigns(teams, game_cfg)
            user_ids = set(x.user.id for x in Website.objects())
            await set_dsp_creatives(teams, campaigns_response=result["response_maps"], users=user_ids, game_cfg=game_cfg)

    if now_playing_round > game_cfg.impressions_total or not services.check_budgets():
        return dict(
            round=game_cfg.current_round,
            has_next_round=False,
            teams=Team.get_teams_state(teams, order_by_score=True),
            logs=[],
        )

    bid_request = crud.create_bid_request(now_playing_round, website)
    bid_responses = await services.get_bid_responses(bid_request, teams)

    metrics.handle_bid_response_time_metrics(bid_responses)

    auction = services.Auction(game_cfg, bid_request, bid_responses)
    win, losses = auction.run()

    metrics.handle_win_and_loss_notifications(win, losses)

    services.send_notifications(win, *losses)

    website.update(set__is_active=False)
    if now_playing_round <= game_cfg.impressions_total:
        # cannot use `game_cfg.update(inc__current_round=1)` due to a
        # mongoengine validator bug, see https://github.com/MongoEngine/mongoengine/issues/2339
        game_cfg.update(__raw__={"$inc": {"current_round": 1}})
        game_cfg.reload()

    has_next_round = services.check_next_round(game_cfg)

    bid_response_data = None
    if win:
        bid_response_data = win.bid_response.to_mongo().to_dict()
        win_data = win.to_mongo().to_dict()
        win_data["final_price"] = win_data.pop("price")
        bid_response_data.update(**win_data)
        bid_response_data["team"] = win.bid_response.team.name
        bid_response_data["image_size"] = auction.image_size

    return dict(
        round=game_cfg.current_round,
        has_next_round=has_next_round,
        bidrequest=bid_request.to_mongo_patched().to_dict(),
        bidresponse=bid_response_data,
        teams=Team.get_teams_state(order_by_score=not has_next_round),
        logs=list(GameLog.get_round_logs(bid_request.id)),
    )


@r.get("/teams/", tags=["teams"], response_model=list[TeamListSchema])
async def read_teams():
    logger.info("getting teams")
    teams = crud.get_teams()
    logger.info("end getting teams")
    return list(teams)


@r.post("/teams/", tags=["teams"], response_model=TeamListSchema, status_code=201)
async def create_team(team: TeamCreateBodySchema):
    new_team = crud.create_team(team)
    return new_team


@r.delete("/teams/{team_id}/", tags=["teams"], status_code=204)
async def delete_team(team_id: int):
    crud.delete_team(team_id)
    return


@r.get("/game/state/", tags=["game"], response_model=GameStateSchema)
async def get_game_state(game_cfg: GameConfig = Depends(get_game_config), teams: list[Team] = Depends(get_teams)):
    return crud.calculate_game_state(game_cfg, teams)


@r.post("/game/reset/", tags=["game"])
async def reset_game(teams: list[Team] = Depends(get_teams)):

    # NOTE: reset metrics on reset. Prometheus has a delay between deletion and new metrics collection (~ 20s-30s).
    # That is why it is needed to make reset as early as possible
    reset_metrics()

    cfg = crud.reset_current_game()
    await send_cfg_to_dsps(teams, game_cfg=cfg)
    return Response(status_code=status.HTTP_200_OK)


##################################


@r.get("/test/config/")
async def test_config(team: Team = Depends(get_team)):
    from app.configurator import crud

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    resp = await crud.send_cfg_to_dsps([team])
    response_map = resp.pop("response_map", None)
    api_resp = list(response_map.values())[0]["response"]
    resp["status_code"] = api_resp.status_code
    resp["content"] = api_resp.text
    return resp


@r.get("/test/notify/")
async def test_notify(win: bool, team: Team = Depends(get_team)):
    from urllib.parse import urljoin

    from app.ssp.constants import get_ssp_settings
    from app.ssp.schemas import LossNotificationSchema, WinNotificationSchema
    from app.ssp.tasks import _notify

    ssp_settings = get_ssp_settings()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    url = urljoin(team.api_url, ssp_settings.DSP_NOTIFY_ENDPOINT)
    schema = WinNotificationSchema if win else LossNotificationSchema
    default_payload = dict(id="QWERTY", win=win, price="12.34", click=True, conversion=False, revenue="20.0")

    resp = _notify(url, schema(**default_payload).json(), win=win)
    return resp.text


@r.get("/test/bid/")
async def test_bid_request(team: Team = Depends(get_team)):
    from app.ssp.documents import BidRequest
    from app.ssp.util import generate_str_id

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    bid_request = BidRequest(
        rid=generate_str_id(),
        round=1,
        imp=dict(banner=dict(w=200, h=300)),
        click=dict(prob="0.5"),
        conv=dict(prob="0.5"),
        site=dict(domain="https://habr.com/"),
        ssp=dict(id="TEST_SSP_ID"),
        user=dict(id="TEST_USER_ID"),
        bcat=[],
    )

    try:
        bid_responses = await services.get_bid_responses(bid_request, [team])
    finally:
        bid_request.delete()

    api_result = list(bid_responses.values())[0]
    return dict(status_code=api_result["status"], content=api_result["response_data"])
