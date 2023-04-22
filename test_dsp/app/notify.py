from .app import Creative, BidObject, ConfigurationModel, db


def handle_win_notify_request(notity_data):
    conf = db.session.query(ConfigurationModel).where(ConfigurationModel.actual == True).first()
    bid_object_id = f"{conf.id}__{notity_data['id']}"

    bid_object = db.session.query(BidObject).where(BidObject.id == bid_object_id).first()
    if not bid_object:
        return

    bid_object.status = "win"
    creative = db.session.query(Creative).where(Creative.id == bid_object.creative_id).first()
    if not creative:
        return

    campaign = creative.campaign
    campaign.balance -= notity_data["price"]
    bid_object.real_revenue = notity_data["revenue"]



