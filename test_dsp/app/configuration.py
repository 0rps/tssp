from sqlalchemy.sql import update

from .app import ConfigurationModel, Creative, Campaign
from .app import db


def get_current_configuration():
    cfg = db.session.query(ConfigurationModel).where(ConfigurationModel.actual == True).first()
    return cfg


def get_configuration_data():
    cfg = db.session.query(ConfigurationModel).where(ConfigurationModel.actual == True).first()
    if cfg is None:
        return {}
    return {
        'id': cfg.id,
        'budget': cfg.budget,
        'impressions_total': cfg.impressions_total,
    }


def handle_configuration_request(configuration_data):
    db.session.execute(
            update(ConfigurationModel).
            where(ConfigurationModel.actual == True).
            values(actual=False)
        )

    configuration = ConfigurationModel()
    configuration.budget = configuration_data['budget']
    configuration.actual = True
    configuration.impressions_total = configuration_data['impressions_total']
    configuration.auction_type = configuration_data['auction_type']
    configuration.game_goal = configuration_data['game_goal']
    configuration.mode = configuration_data['mode']
    configuration.impression_revenue = configuration_data['impression_revenue']
    configuration.click_revenue = configuration_data['click_revenue']
    configuration.conversion_revenue = configuration_data['conversion_revenue']
    configuration.frequency_capping = configuration_data['frequency_capping']
    configuration.current_impression = 0

    db.session.add(configuration)

    db.session.query(Creative).delete()
    db.session.query(Campaign).delete()

    if configuration.mode == 'free':
        from .campaign import create_default_campaign
        create_default_campaign(configuration)

    return configuration

