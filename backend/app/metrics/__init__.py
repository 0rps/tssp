import httpx
from aioprometheus import Counter, Gauge, Histogram

dsp_win_counter = Counter(
    "dsp_wins_total",
    "Total number of wins",
)

dsp_loss_counter = Counter(
    "dsp_losses_total",
    "Total number of impressions",
)

dsp_impression_counter = Counter(
    "dsp_impressions_total",
    "Total number of win impressions",
)

dsp_click_counter = Counter(
    "dsp_clicks_total",
    "Total number of clicks",
)

dsp_conversion_counter = Counter(
    "dsp_conversions_total",
    "Total number of conversions",
)

dsp_revenue_gauge = Gauge(
    "dsp_revenue",
    "tDSP revenue"
)

dsp_budget_gauge = Gauge(
    "dsp_budget",
    "DSP current budget",
)

dsp_spent_budget_gauge = Gauge(
    "dsp_spent_budget",
    "DSP spent budget",
)

dsp_bid_ratio_gauge = Gauge(
    "dsp_bid_ratio",
    "Bid value divided by potential revenue amount"
)

dsp_http_bid_time_gauge = Gauge(
    "dsp_response_time",
    "Response time of tDSP"
)

dsp_http_notify_time_gauge = Gauge(
    "dsp_response_time_gauge",
    "Response time of tDSP"
)

dsp_http_bid_response_time_histogram = Histogram(
    "dsp_response_time_histogram",
    "Response time of tDSP",
    buckets=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.9, 6.0]
)

dsp_bid_value_histogram = Histogram(
    "dsp_bid_value_histogram",
    "Bid value for tDSP",
    buckets=[2.5, 5.0, 7.5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30, 35, 40, 45, 50, 60, 75, 100, 150, 200]
)


def reset_collector(counter):
    from aioprometheus.metricdict import MetricDict
    counter.values = MetricDict()


def reset_local_registries():
    counters = [
        dsp_win_counter,
        dsp_click_counter,
        dsp_loss_counter,
        dsp_impression_counter,
        dsp_conversion_counter
    ]
    for counter in counters:
        reset_collector(counter)

    gauges = [
        dsp_budget_gauge,
        dsp_revenue_gauge,
        dsp_bid_ratio_gauge,
        dsp_http_bid_time_gauge,
        dsp_http_notify_time_gauge,
        dsp_spent_budget_gauge,
    ]

    for gauge in gauges:
        reset_collector(gauge)

    histograms = [dsp_bid_value_histogram, dsp_http_bid_response_time_histogram]
    for hist in histograms:
        reset_collector(hist)


def reset_prometheus_server():
    from app.ssp.constants import get_ssp_settings
    ssp_settings = get_ssp_settings()
    url = ssp_settings.PROMETHEUS_URL

    if url[-1] == '/':
        url = url[:-1]

    reset_params = {"match[]": '{__name__=~"dsp_.*"}'}
    reset_url = f"{url}/api/v1/admin/tsdb/delete_series"
    clean_tombstones_url = f"{url}/api/v1/admin/tsdb/clean_tombstones"

    try:
        response = httpx.post(reset_url, params=reset_params)
        response.raise_for_status()

        response = httpx.post(clean_tombstones_url)
        response.raise_for_status()
    except Exception as ex:
        if not ssp_settings.IGNORE_PROMETHEUS_ERRORS:
            raise ex
        print("Exception is happened", ex)


def reset_metrics():
    reset_local_registries()
    reset_prometheus_server()
