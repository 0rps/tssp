import datetime
from typing import Dict, List

from app import metrics
from app.configurator.documents import GameConfig
from app.core.const import HTTP_CODE_DSP_RESPONSE_UNKNOWN_ERROR, LOSS_REASON_SMALL_BID
from app.ssp.documents import Notification, BidResponse, BidRequest, Team


def handle_bid_response_time_metrics(data: Dict[str, object]):
    for _, data in data.items():
        dsp_name = data["team"].name
        if data['status'] is not None and data['status'] != HTTP_CODE_DSP_RESPONSE_UNKNOWN_ERROR:
            request_duration: datetime.timedelta = data['request_duration']
            metrics.dsp_http_bid_response_time_histogram.add({'dsp': dsp_name}, request_duration.total_seconds())
            metrics.dsp_http_bid_time_gauge.set({'dsp': dsp_name}, request_duration.total_seconds())


def handle_bid(game_configuration: GameConfig, bid_request: BidRequest, has_ads_txt_penalty: bool, bid_response: BidResponse):
    if bid_response.no_bid:
        return

    pclick = bid_request.click.prob
    pconv = bid_request.conv.prob

    imp_revenue = 0 if has_ads_txt_penalty else game_configuration.impression_revenue

    potential_revenue = (
            imp_revenue
            + game_configuration.click_revenue * pclick
            + game_configuration.conversion_revenue * pclick * pconv
    )

    metrics.dsp_bid_ratio_gauge.set({'dsp': bid_response.team.name}, bid_response.price / potential_revenue)
    metrics.dsp_bid_value_histogram.add({"dsp": bid_response.team.name}, float(bid_response.price))


def handle_win_and_loss_notifications(win: Notification | None, losses: List[Notification] | None):
    if win:
        labels = {"dsp": win.bid_response.team.name}
        metrics.dsp_win_counter.add(labels, 1)

        if win.final_pcvr > 0.001 or win.final_pctr > 0.001 or win.revenue > 0.001:
            metrics.dsp_impression_counter.add(labels, 1)

        if win.click:
            metrics.dsp_click_counter.add(labels, 1)

        if win.conversion:
            metrics.dsp_conversion_counter.add(labels, 1)

        metrics.dsp_revenue_gauge.add(labels, win.revenue)

    losses = losses or []
    for loss in losses:
        bid_response = loss.bid_response
        reason = LOSS_REASON_SMALL_BID
        if bid_response.no_bid:
            reason = bid_response.no_bid_reason
        metrics.dsp_loss_counter.add({"dsp": bid_response.team.name, "reason": reason}, 1)


def set_team_budget(team: Team, cur_budget: float, win_price: float | None):
    labels = {'dsp': team.name}
    metrics.dsp_budget_gauge.set(labels, cur_budget)
    if win_price is None:
        metrics.dsp_spent_budget_gauge.set(labels, 0)
    else:
        metrics.dsp_spent_budget_gauge.add(labels, win_price)
