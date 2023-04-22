

class BidRequest:

    def __init__(self, data):
        self.bid_id = data["id"]
        self.w = int(data["imp"]["banner"]["w"])
        self.h = (data["imp"]["banner"]["h"])
        self.click_prob = float(data["click"]["prob"])
        self.conv_prob = float(data["conv"]["prob"])
        self.user_id = str(data["user"]["id"])
        self.blocked_categories = list(data["bcat"])
        self.site_domain = str(data["site"]["domain"])
        self.ssp_id = str(data["ssp"]["id"])
