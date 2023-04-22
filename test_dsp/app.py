import random
import time

from flask import request
from app.app import app, db
from app import creative
from app import campaign
from app import configuration
from app import bid_engine
from app import notify
from app.utils import should_happen
from app.bid_engine import BidEngine


@app.route('/rtb/bid/', methods=['POST'])
def rtb_bid():
    engine = BidEngine(request.json)
    data = engine.process_request()
    db.session.commit()

    time.sleep(0.4)

    if data:
        print(f"Bid Response for bid_id = {request.json['id']}: {data}")
        return data, 200
    print(f"No Bid for bid_id = {request.json['id']}")
    return "", 204


@app.route('/rtb/notify/', methods=['POST'])
def rtb_notify():
    if not request.json["win"]:
        print(f"Notify for bid_id = {request.json['id']}: LOSS")
        return "", 200

    notify.handle_win_notify_request(request.json)
    print(f"Notify for bid_id = {request.json['id']}: WIN, data = {request.json}")
    db.session.commit()
    return "", 200


@app.route('/game/configure/', methods=['GET', 'POST'])
def configure():
    if request.method == 'GET':
        data = configuration.get_configuration_data()
        return data, 200
    else:
        cfg = configuration.handle_configuration_request(request.json)
        print(f"Configuration is set up, id: {cfg.id}")
        db.session.commit()
        return "", 200


@app.route('/api/campaigns/', methods=['GET','POST'])
def campaigns():
    if request.method == 'GET':
        return campaign.select_campaigns()

    campaign_instance = campaign.create_campaign(request.json)
    db.session.commit()

    data = {
        'id': campaign_instance.id,
        'name': campaign_instance.name,
        'budget': campaign_instance.budget,
    }
    print(f"Campaign is created: {data}")
    return data, 201


@app.route('/api/creatives/', methods=['GET', 'POST'])
def creatives():
    if request.method == 'GET':
        return creative.select_creatives()

    cr = creative.create_creative(request.json)
    db.session.commit()

    data = {
        'id': cr.id,
        'name': cr.name,
        'external_id': cr.external_id,
        'url': cr.image_url,
        'campaign': {'id': cr.campaign_id},
        'categories': [{'id': x.id, 'code': x.code} for x in cr.categories],
    }
    print(f"Creative is created: {data}")
    return data, 201


if __name__ == '__main__':
    from app.creative import create_default_categories
    with app.app_context():
        db.create_all()
        create_default_categories()

    app.run(host='0.0.0.0', port=8000)
