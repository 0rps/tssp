import random
import requests

from .app import Creative, BidObject, ConfigurationModel, UserModel, db
from .bid_request import BidRequest
from .configuration import get_current_configuration
from .const import ADS_TXT_SITE
from .creative import generate_creative_url
from .utils import should_happen


class DecisionOption:

    def __init__(self, creative: Creative, conf: ConfigurationModel, bid_request: BidRequest):
        self.creative = creative

        self.revenue_imp = conf.impression_revenue
        self.revenue_click = conf.click_revenue
        self.revenue_conv = conf.conversion_revenue

        self.base_pclick = bid_request.click_prob
        self.base_pconv = bid_request.conv_prob

        self.pclick = self.base_pclick
        self.pconv = self.base_pconv

    def get_balance(self):
        return self.creative.campaign.balance

    def get_potential_revenue(self):
        return self.revenue_imp + self.pclick * self.revenue_click + self.pclick * self.pconv * self.revenue_conv

    def apply_freq_capping(self, user_id, freq_cap):
        count = db.session.query(UserModel).where(UserModel.user_id == user_id, UserModel.campaign_id == self.creative.campaign_id).count()
        if count >= freq_cap:
            self.pclick -= 0.05
        if self.pclick < 0:
            self.pclick = 0

    def apply_ads_txt(self, ssp_in_ads_txt):
        if not ssp_in_ads_txt:
            self.revenue_imp = 0

    def is_allowed_creative(self, blocked_categories):
        return self.creative.is_allowed(blocked_categories)


class BidEngine:

    def __init__(self, bid_request_data):
        self.bid_request = BidRequest(bid_request_data)
        self.conf = get_current_configuration()

    def optimize(self, options) -> [DecisionOption, float]:
        options = sorted(options, key=lambda x: min(x.get_balance(), x.get_potential_revenue()))

        winner = options[-1]
        bid = min(winner.get_balance(), winner.get_potential_revenue())

        perc = float(random.randrange(25, 75))
        bid = int(bid * perc) / 100.0

        return winner, bid

    def is_ssp_in_ads_txt(self, ssp_id, publisher_domain):
        request = requests.get(ADS_TXT_SITE, params={'publisher': publisher_domain})
        if request.status_code == 200:
            return ssp_id in str(request.content)

        return True

    def process_request(self):
        self.conf.current_impression += 1

        creatives = db.session.query(Creative)
        options = [DecisionOption(x, self.conf, self.bid_request) for x in creatives]
        options = [x for x in options if x.is_allowed_creative(self.bid_request.blocked_categories)]

        is_in_ads_txt = self.is_ssp_in_ads_txt(self.bid_request.ssp_id, self.bid_request.site_domain)
        for option in options:
            option.apply_freq_capping(self.bid_request.user_id, self.conf.frequency_capping)
            option.apply_ads_txt(is_in_ads_txt)

        if not options:
            print('No allowed creatives')
            return None

        winner, bid_value = self.optimize(options)
        win_creative = winner.creative

        bo = BidObject()
        bo.id = f"{self.conf.id}__{self.bid_request.bid_id}"
        bo.configuration_id = self.conf.id
        bo.impression_index = self.conf.current_impression
        bo.status = 'loss'
        bo.bid = bid_value
        bo.creative_id = win_creative.id
        bo.real_revenue = 0

        user = UserModel()
        user.user_id = self.bid_request.user_id
        user.campaign_id = win_creative.campaign_id

        db.session.add(bo)
        db.session.add(user)

        return {
            "external_id": win_creative.external_id,
            "price": bid_value,
            "image_url": generate_creative_url(win_creative, self.bid_request.w, self.bid_request.h),
            "cat": [x.code for x in win_creative.categories]
        }

