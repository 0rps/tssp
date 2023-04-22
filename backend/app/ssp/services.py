import random
import datetime
from decimal import Decimal
from io import BytesIO
from urllib.parse import urljoin

import httpx
from app.configurator.constants import AuctionType, get_game_settings
from app.configurator.documents import GameConfig
from app.core.const import (
    LOSS_REASON_NO_BID,
    LOSS_REASON_BID_RESPONSE_ERROR,
    LOSS_REASON_FORBIDDEN, HTTP_CODE_DSP_RESPONSE_TIMEOUT, LOSS_REASON_BID_RESPONSE_TIMEOUT_ERROR
)
from app.core.services import SspApiAggregator
from app.ssp import crud, tasks
from app.ssp.constants import get_ssp_settings
from app.ssp.documents import (
    BidRequest,
    BidResponse,
    GameLog,
    Notification,
    Team,
    Website,
    UserFrequencyCapping,
)
from app.ssp.schemas import (
    BidRequestSchema,
    BidResponseSchema,
    LossNotificationSchema,
    WinNotificationSchema,
)
from fastapi.encoders import jsonable_encoder
from PIL import Image
from starlette import status
from . import metrics


class NoBidException(Exception):
    def __init__(self, reason, *args, **kwargs):
        self.reason = reason
        super().__init__(*args, kwargs)


def extract_status_and_json(response, duration: datetime.timedelta | None) -> dict:
    result = dict(response=response, status=None, response_data=None, request_duration=duration)
    if response:
        result["status"] = response.status_code
        try:
            data = response.json()
        except Exception:
            data = response.text
        result["response_data"] = data
    return result


async def get_bid_responses(bid_request: BidRequest, teams: list[Team]) -> dict:
    ssp_settings = get_ssp_settings()

    teams_map, http_client_cfg, request_extra_kwargs = get_common_api_aggregator_params(teams)
    hosts = list(teams_map.keys())

    payload = bid_request.to_mongo_patched().to_dict()
    payload = jsonable_encoder(BidRequestSchema(**payload))

    service = SspApiAggregator(
        hosts,
        path=ssp_settings.DSP_BID_ENDPOINT,
        config=http_client_cfg,
        req_kwargs=request_extra_kwargs,
        response_handler=extract_status_and_json,
    )
    response_map = await service.post(payload=payload)
    for host in list(response_map.keys()):
        response_map[host]["team"] = teams_map[host]

    return response_map


def decide_probability_result(probability: float):
    return random.random() <= probability


class Auction:
    def __init__(self, game_cfg: GameConfig, bid_request: BidRequest, bid_responses: dict):
        self.game_cfg = game_cfg
        self.bid_request = bid_request
        self.bid_responses = bid_responses
        self.image_size = dict(w=0, h=0)
        self.winner = None

    def run(self) -> tuple[Notification | None, list[Notification]]:
        win_notification = None
        loss_notifications = []
        has_imp = has_click = has_conversion = False

        valid_bids, invalid_bids = self.validate_bids()
        for b in invalid_bids:
            n = Notification.objects.create(bid_response=b, win=False)
            loss_notifications.append(n)

        if not valid_bids:
            return win_notification, loss_notifications

        bids = sorted(valid_bids, key=lambda x: x.price)

        has_ads_txt_penalty = False
        if self.game_cfg.ads_txt_enabled:
            ws = Website.objects(site__domain=self.bid_request.site.domain)
            has_ads_txt_penalty = (ws.count() == 0) or (not ws.first().has_ssp_in_ads_txt)

        for bid in bids:
            metrics.handle_bid(self.game_cfg, self.bid_request, has_ads_txt_penalty, bid)

        win_price = self.pick_win_price(bids)
        winner_bid = self.choose_winner(bids)
        self.winner = winner_bid.team
        GameLog.log_winner(team_obj=self.winner, bid_request_id=self.bid_request.rid, price=win_price)
        lost_bids = bids

        for b in lost_bids:
            n = Notification.objects.create(bid_response=b, win=False)
            loss_notifications.append(n)

        bid_request_data = self.bid_request.to_mongo().to_dict()

        img = self.get_image(winner_bid.image_url)
        if img:
            has_imp = True
            width, height = img.size
            self.apply_size_penalties(bid_request_data, width, height)
            self.apply_freq_cap_penalties(winner_bid, bid_request_data)
            has_click = decide_probability_result(bid_request_data["click"]["prob"])
            if has_click:
                has_conversion = decide_probability_result(bid_request_data["conv"]["prob"])
            revenue = self.calculate_revenue(
                imp_count=int(has_imp), click_count=int(has_click), conv_count=int(has_conversion)
            )
            revenue = self.apply_ads_txt_penalties(has_ads_txt_penalty, revenue)
            self.image_size = dict(w=width, h=height)
        else:
            revenue = 0
            bid_request_data["click"]["prob"] = 0
            bid_request_data["conv"]["prob"] = 0
            GameLog.log_bad_image(team_obj=self.winner, bid_request_id=self.bid_request.rid)

        # cannot use `.update(dec__budget=win_price, inc__revenue=revenue)` due to a
        # mongoengine validator bug, see https://github.com/MongoEngine/mongoengine/issues/2339

        metrics.set_team_budget(winner_bid.team, float(winner_bid.team.budget - Decimal(win_price)), float(win_price))

        Team.objects(tid=winner_bid.team.id).update(
            __raw__={
                "$inc": {
                    "budget": -float(win_price),
                    "imp_count": int(has_imp),
                    "click_count": int(has_click),
                    "conv_count": int(has_conversion),
                    "revenue": revenue,
                },
            }
        )

        win_notification = Notification.objects.create(
            bid_response=winner_bid,
            win=True,
            price=win_price,
            click=has_click,
            conversion=has_conversion,
            revenue=revenue,
            final_pctr=bid_request_data["click"]["prob"],
            final_pcvr=bid_request_data["conv"]["prob"],
        )

        return win_notification, loss_notifications

    def choose_winner(self, sorted_bids: list[BidResponse]) -> BidResponse | None:
        return sorted_bids.pop() if sorted_bids else None

    def pick_win_price(self, sorted_bids: list[BidResponse]) -> Decimal | None:
        if not sorted_bids:
            return None
        if self.game_cfg.auction_type == AuctionType.SECOND_PRICE and len(sorted_bids) > 1:
            return sorted_bids[-2].price
        else:
            return sorted_bids[-1].price

    def calculate_revenue(self, *, imp_count: int, click_count: int, conv_count: int) -> int:
        return (
            imp_count * self.game_cfg.impression_revenue
            + click_count * self.game_cfg.click_revenue
            + conv_count * self.game_cfg.conversion_revenue
        )

    def apply_size_penalties(self, bid_data: dict, width: int, height: int):
        if bid_data["imp"]["banner"]["w"] != width or bid_data["imp"]["banner"]["h"] != height:
            ssp_settings = get_ssp_settings()
            bid_data["click"]["prob"] = max(bid_data["click"]["prob"] - ssp_settings.WRONG_SIZE_CLICK_FINE, 0)
            bid_data["conv"]["prob"] = max(bid_data["conv"]["prob"] - ssp_settings.WRONG_SIZE_CONVERSION_FINE, 0)
            GameLog.log_penalty_reason(
                team_obj=self.winner, bid_request_id=self.bid_request.rid, reason="wrong creative resolution"
            )

    def get_image(self, url: str) -> Image:
        game_settings = get_game_settings()

        try:
            r = httpx.get(url, timeout=game_settings.DSP_RESPONSE_TIMEOUT)
            img = Image.open(BytesIO(r.content))
        except Exception:
            img = None
        return img

    def apply_freq_cap_penalties(self, winner_bid: BidResponse, bid_data: dict):
        is_applicable = False
        if self.game_cfg.frequency_capping_enabled:
            fc_list = UserFrequencyCapping.objects(team_id=self.winner.tid, user_id=bid_data['user']['id'])
            for fc in fc_list:
                if winner_bid.external_id in fc.creatives_id_list:
                    if fc.times + 1 > self.game_cfg.frequency_capping:
                        is_applicable = True
                    fc.update(__raw__={"$inc": {"times": 1}})
                    break

        if is_applicable:
            ssp_settings = get_ssp_settings()
            bid_data["click"]["prob"] = max(
                bid_data["click"]["prob"] - ssp_settings.FREQUENCY_CAPPING_CLICK_FINE, 0
            )
            GameLog.log_penalty_reason(
                team_obj=self.winner, bid_request_id=self.bid_request.rid, reason="frequency capping limit"
            )

    def apply_ads_txt_penalties(self, has_ads_txt_penalty: bool, revenue: int) -> int:
        if has_ads_txt_penalty:
            revenue -= self.game_cfg.impression_revenue
            GameLog.log_penalty_reason(
                team_obj=self.winner,
                bid_request_id=self.bid_request.rid,
                reason="SSP is not authorized to sell this ad (ads.txt)",
            )
            return revenue
        return revenue

    def validate_bids(self) -> tuple:
        valid, invalid = [], []
        for host, data in self.bid_responses.items():
            team = data["team"]
            resp_status, resp_json = data["status"], data["response_data"]

            bid_data = dict()
            try:
                self.validate_response_status(resp_status)
                bid_schema = self.validate_bid_response_data(resp_json)
                self.validate_bid_price(bid_schema, team)
                self.validate_bcat(bid_schema)
                bid_data = bid_schema.dict()
                no_bid = False
            except NoBidException as ex:
                GameLog.log_nobid_reason(team_obj=team, bid_request_id=self.bid_request.rid, reason=str(ex))
                no_bid = True

                bid_data["no_bid_reason"] = ex.reason

            bid_response = BidResponse.objects.create(
                bid_request=self.bid_request, team=team, no_bid=no_bid, **bid_data
            )
            if bid_response.no_bid:
                invalid.append(bid_response)
            else:
                valid.append(bid_response)
                GameLog.log_price(team_obj=team, bid_request_id=self.bid_request.rid, price=bid_response.price)

        return valid, invalid

    def validate_response_status(self, resp_status: int | None) -> bool:
        if resp_status == status.HTTP_204_NO_CONTENT:
            raise NoBidException(LOSS_REASON_NO_BID, f"response status = {resp_status}")

        if resp_status != status.HTTP_200_OK:
            if resp_status == HTTP_CODE_DSP_RESPONSE_TIMEOUT:
                raise NoBidException(LOSS_REASON_BID_RESPONSE_TIMEOUT_ERROR, f"response timeout")
            else:
                raise NoBidException(LOSS_REASON_BID_RESPONSE_ERROR, f"response status = {resp_status}")
        return True

    def validate_bid_response_data(self, resp_json: dict) -> BidResponseSchema:
        try:
            return BidResponseSchema(**resp_json)
        except Exception:
            raise NoBidException(LOSS_REASON_BID_RESPONSE_ERROR, "response schema validation error")

    def validate_bid_price(self, bid: BidResponseSchema, team: Team) -> bool:
        if bid.price > team.budget:
            raise NoBidException(LOSS_REASON_FORBIDDEN, "price exceeds available budget")
        return True

    def validate_bcat(self, bid: BidResponseSchema) -> bool:
        if not self.game_cfg.blocked_categories_enabled:
            return True
        if set(bid.cat) & set(self.bid_request.bcat):
            raise NoBidException(LOSS_REASON_FORBIDDEN, "forbidden category")
        return True


def send_notifications(*notifications: Notification):
    ssp_settings = get_ssp_settings()

    for n in notifications:
        if not n:  # first notification (win) might be None
            continue
        url = urljoin(n.bid_response.team.api_url, ssp_settings.DSP_NOTIFY_ENDPOINT)
        bid_request_id = n.bid_response.bid_request.rid
        if n.win:
            s = WinNotificationSchema(
                id=bid_request_id,
                win=True,
                price=n.price,
                click=n.click,
                conversion=n.conversion,
                revenue=n.revenue,
            )
        else:
            s = LossNotificationSchema(
                id=bid_request_id,
                win=False,
            )

        bearer_token = n.bid_response.team.bearer_token
        tasks.notify.apply_async(kwargs=dict(url=url, payload=s.json(), win=s.win, bearer_token=bearer_token))


def check_game_state() -> bool:
    has_next_site = bool(Website.active_sites().first())
    return check_budgets() and has_next_site


def check_next_round(game_cfg: GameConfig) -> bool:
    return (game_cfg.current_round < game_cfg.impressions_total) and check_game_state()


def check_budgets():
    return crud.get_teams().filter(budget__gt=0).count() > 0


def get_common_api_aggregator_params(teams: list[Team]) -> (dict, dict, dict):
    s = get_game_settings()

    teams_map = dict()
    request_extra_kwargs = dict()
    for team in teams:
        teams_map[team.api_url] = team
        if team.bearer_token:
            request_extra_kwargs[team.api_url] = dict(headers={"Authorization": "Bearer " + team.bearer_token})

    http_client_cfg = dict(timeout=s.DSP_RESPONSE_TIMEOUT)
    return teams_map, http_client_cfg, request_extra_kwargs
