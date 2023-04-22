import datetime
from collections import defaultdict

from app.configurator.constants import get_game_settings
from app.configurator.documents import GameConfig
from app.configurator.schemas import GameCfgDSPSchema, GameCfgSSPSchema
from app.core.services import SspApiAggregator
from app.ssp import metrics
from app.ssp.documents import Team, Website, UserFrequencyCapping
from app.ssp.fixtures import (
    IAB_CATEGORIES,
    IMG_DATA_CAT_0,
    IMG_DATA_CAT_1,
    IMG_DATA_WSJ_0,
    IMG_DATA_WSJ_1,
    IMG_DATA_KAGGLE_0,
    IMG_DATA_KAGGLE_1,
    IMG_DATA_300x200,
    IMG_DATA_300x300
)
from app.ssp.schemas import CampaignResponseSchema, CreativeResponseSchema
from app.ssp.services import get_common_api_aggregator_params
from app.ssp.util import generate_str_id, website_generator
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from starlette import status
from starlette.exceptions import HTTPException


def get_game_config() -> GameConfig:
    return GameConfig.objects.order_by("id").first()


def update_game_config(updated_cfg: GameCfgSSPSchema, cfg: GameConfig | None = None) -> GameConfig:
    if cfg is None:
        cfg = get_game_config()
    updated_attrs = updated_cfg.dict()
    recreate_websites = False
    reset_budget = False

    if not updated_attrs["frequency_capping_enabled"]:
        updated_attrs["frequency_capping"] = updated_attrs["impressions_total"]

    if cfg:
        if (cfg.impressions_total != updated_attrs["impressions_total"]) or (cfg.mode != updated_attrs["mode"]):
            recreate_websites = True
        if cfg.budget != updated_attrs["budget"]:
            reset_budget = True
        cfg.set_attrs(current_round=0, **updated_attrs)
    else:
        cfg = GameConfig(**updated_attrs)
        recreate_websites = True
    cfg.save()

    if reset_budget:
        for team in Team.objects.all():
            team.update(set__budget=cfg.budget)
            metrics.set_team_budget(team, cfg.budget, None)

    if recreate_websites:
        Website.recreate(cfg)

    UserFrequencyCapping.objects.delete()

    return cfg


async def send_cfg_to_dsps(teams: list[Team], game_cfg: GameConfig | None = None) -> dict:
    s = get_game_settings()
    if not game_cfg:
        game_cfg = get_game_config()

    teams_map, http_client_cfg, request_extra_kwargs = get_common_api_aggregator_params(teams)
    hosts = list(teams_map.keys())
    payload = jsonable_encoder(GameCfgDSPSchema.from_orm(game_cfg))

    service = SspApiAggregator(
        hosts, path=s.DSP_CONFIG_ENDPOINT, config=http_client_cfg, req_kwargs=request_extra_kwargs
    )
    response_map = await service.post(payload=payload)

    result = dict(errors=[])
    for host, data in response_map.items():
        resp = data["response"]
        resp_status = getattr(resp, "status_code", None)
        if resp_status != status.HTTP_200_OK:
            team = teams_map[host]
            result["errors"].append("Team {} responded with status code {}".format(team.name, resp_status))
    result["response_map"] = response_map

    if result["errors"]:
        raise HTTPException(status_code=400, detail="Config: " + ", ".join(result["errors"]))

    return result


def validate_campaigns_response(response, duration: datetime.timedelta | None) -> dict:
    result = dict(response=response, response_data=None, errors=[])
    if response and response.status_code == status.HTTP_201_CREATED:
        try:
            data = response.json()
        except Exception as ex:
            result["errors"].append("Invalid response body")
            result["response_data"] = response.text
            return result

        try:
            data = CampaignResponseSchema(**data)
        except ValidationError as ex:
            msg = ", ".join([str(i["loc"]) + ": " + i["msg"] for i in ex.errors()])
            result["errors"].append("Create Campaign response is not valid: " + msg)

        result["response_data"] = data
    return result


async def set_dsp_campaigns(teams: list[Team], game_cfg: GameConfig | None = None) -> dict:
    s = get_game_settings()
    if not game_cfg:
        game_cfg = get_game_config()

    teams_map, http_client_cfg, request_extra_kwargs = get_common_api_aggregator_params(teams)
    hosts = list(teams_map.keys())

    service = SspApiAggregator(
        hosts,
        path=s.DSP_CAMPAIGNS_ENDPOINT,
        config=http_client_cfg,
        req_kwargs=request_extra_kwargs,
        response_handler=validate_campaigns_response,
    )

    result = dict(errors=[], response_maps=[])
    campaigns_data = get_campaigns_payload(game_cfg)
    for payload in campaigns_data:
        response_map = await service.post(payload=payload)
        for host, data in response_map.items():
            resp = data["response"]
            resp_status = getattr(resp, "status_code", None)
            if resp_status != status.HTTP_201_CREATED:
                team = teams_map[host]
                result["errors"].append("Team {} responded with status code {}".format(team.name, resp_status))
            if data["errors"]:
                result["errors"].extend(data["errors"])
        result["response_maps"].append(response_map)

    if result["errors"]:
        raise HTTPException(status_code=400, detail="Campaigns: " + ", ".join(result["errors"]))

    return result


def get_campaigns_payload(game_cfg: GameConfig) -> list[dict]:
    kaggle_budget = int(game_cfg.budget * 0.40)
    wsj_budgdet = kaggle_budget
    books_budget = game_cfg.budget - wsj_budgdet - kaggle_budget

    return [
        {"name": "[script campaign] Kaggle CTR contests", "budget": kaggle_budget},
        {"name": "[script campaign] Cat book publisher", "budget": books_budget},
        {"name": "[script campaign] Wall Street Journal", "budget": wsj_budgdet},
    ]


def validate_creatives_response(response, duration: datetime.timedelta | None) -> dict:
    result = dict(response=response, response_data=None, errors=[])
    if response and response.status_code == status.HTTP_201_CREATED:
        try:
            data = response.json()
        except Exception as ex:
            result["errors"].append("Invalid response body")
            result["response_data"] = response.text
            return result

        try:
            data = CreativeResponseSchema(**data)
        except ValidationError as ex:
            msg = ", ".join([str(i["loc"]) + ": " + i["msg"] for i in ex.errors()])
            result["errors"].append("Create Creative response is not valid: " + msg)

        result["response_data"] = data
    return result


# async def set_dsp_creatives(teams: list[Team], campaigns_response: list[dict], users: {str}, game_cfg: GameConfig | None = None):
#     s = get_game_settings()
#     if not game_cfg:
#         game_cfg = get_game_config()
#
#     teams_map, http_client_cfg, request_extra_kwargs = get_common_api_aggregator_params(teams)
#     hosts = list(teams_map.keys())
#
#     service = SspApiAggregator(
#         hosts,
#         path=s.DSP_CREATIVES_ENDPOINT,
#         config=http_client_cfg,
#         req_kwargs=request_extra_kwargs,
#         response_handler=validate_creatives_response,
#     )
#
#     errors = []
#     for counter, campaign_resp_map in enumerate(campaigns_response):
#         payload_map = {
#             host: get_creatives_payload(game_cfg, campaign_resp_map[host]["response_data"], counter) for host in hosts
#         }
#
#         response_map = await service.post(payload_map=payload_map)
#         for host, data in response_map.items():
#             resp = data["response"]
#             resp_status = getattr(resp, "status_code", None)
#             if resp_status != status.HTTP_201_CREATED:
#                 team = teams_map[host]
#                 errors.append("Team {} responded with status code {}".format(team.name, resp_status))
#
#             if data["errors"]:
#                 errors.extend(data["errors"])
#             else:
#                 payload = payload_map[host]
#                 external_id = payload['external_id']
#                 team = teams_map[host]
#
#                 for user in users:
#                     UserFrequencyCapping.objects.create(
#                         team_id=team.tid,
#                         creatives_id_list=[external_id],
#                         user_id=user
#                     )
#
#     if errors:
#         raise HTTPException(status_code=400, detail="Creatives: " + ", ".join(errors))


async def set_dsp_creatives(teams: list[Team], campaigns_response: list[dict], users: {str}, game_cfg: GameConfig | None = None):
    s = get_game_settings()
    teams_map, http_client_cfg, request_extra_kwargs = get_common_api_aggregator_params(teams)
    hosts = list(teams_map.keys())

    service = SspApiAggregator(
        hosts,
        path=s.DSP_CREATIVES_ENDPOINT,
        config=http_client_cfg,
        req_kwargs=request_extra_kwargs,
        response_handler=validate_creatives_response,
    )

    errors = []
    for counter, campaign_response_map in enumerate(campaigns_response):
        if counter == 0:
            creative_func = get_kaggle_creative
        elif counter == 1:
            creative_func = get_cat_book_publisher_creative
        else:
            creative_func = get_wsj_creative

        team_data = defaultdict(list)

        for creative_index in range(2):
            payload_map = {host: creative_func(campaign_response_map[host]["response_data"], creative_index) for host in hosts}

            response_map = await service.post(payload_map=payload_map)
            for host, data in response_map.items():
                resp = data["response"]
                resp_status = getattr(resp, "status_code", None)
                if resp_status != status.HTTP_201_CREATED:
                    team = teams_map[host]
                    errors.append("Team {} responded with status code {}".format(team.name, resp_status))

                if data["errors"]:
                    errors.extend(data["errors"])
                else:
                    payload = payload_map[host]
                    team = teams_map[host]
                    team_data[team.tid].append(payload['external_id'])

        for tid, data in team_data.items():
            for user in users:
                UserFrequencyCapping.objects.create(
                    team_id=tid,
                    creatives_id_list=data,
                    user_id=user
            )

    if errors:
        raise HTTPException(status_code=400, detail="Creatives: " + ", ".join(errors))


# def get_creatives_payload(game_cfg: GameConfig, campaign_data: CampaignResponseSchema, counter: int) -> dict:
#     if counter == 0:
#         categories = [{"code": "IAB5"}, {"code": "IAB19"}]
#         name = ""
#     elif counter == 1:
#         categories = [{"code": "IAB1"}, {"code": "IAB5"}, {"code": "IAB14"}]
#     else:
#         categories = [{"code": "IAB12"}, {"code": "IAB1"}, {"code": "IAB14"}]
#
#     return dict(
#         external_id=generate_str_id(),
#         name="Creative #1",
#         campaign=dict(id=campaign_data.id),
#         categories=categories,
#         file=(IMG_DATA_300x200, IMG_DATA_300x300)[counter],
#     )

def get_kaggle_creative(campaign_data: CampaignResponseSchema, counter: int) -> dict:
    categories = [{"code": "IAB5"}, {"code": "IAB19"}]
    return dict(
        external_id=generate_str_id(),
        name=f"Creative kaggle #{counter+1}",
        campaign=dict(id=campaign_data.id),
        categories=categories,
        file=(IMG_DATA_KAGGLE_0, IMG_DATA_KAGGLE_1)[counter],
    )


def get_cat_book_publisher_creative(campaign_data: CampaignResponseSchema, counter: int) -> dict:
    categories = [{"code": "IAB1"}, {"code": "IAB5"}, {"code": "IAB14"}]
    return dict(
        external_id=generate_str_id(),
        name=f"Creative cat book #{counter+1}",
        campaign=dict(id=campaign_data.id),
        categories=categories,
        file=(IMG_DATA_CAT_0, IMG_DATA_CAT_1)[counter],
    )


def get_wsj_creative(campaign_data: CampaignResponseSchema, counter: int) -> dict:
    categories = [{"code": "IAB12"}, {"code": "IAB1"}, {"code": "IAB14"}]
    return dict(
        external_id=generate_str_id(),
        name=f"Creative WSJ #{counter+1}",
        campaign=dict(id=campaign_data.id),
        categories=categories,
        file=(IMG_DATA_WSJ_0, IMG_DATA_WSJ_1)[counter],
    )
