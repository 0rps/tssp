from .app import Campaign, ConfigurationModel, db


def select_campaigns():
    res = []
    for cmp in db.session.query(Campaign):
        res.append({
            'id': cmp.id,
            'name': cmp.name,
            'budget': cmp.budget,
        })
    return res


def create_campaign(campaign_data):
    conf = db.session.query(ConfigurationModel).first()

    instance = Campaign()
    instance.budget = campaign_data['budget']
    instance.name = campaign_data['name']
    instance.balance = float(campaign_data['budget'])
    instance.freq_cap = conf.frequency_capping

    db.session.add(instance)
    return instance


def create_default_campaign(cfg):
    from .creative import create_default_creative

    instance = Campaign()
    instance.budget = cfg.budget
    instance.name = "test campaign"
    instance.balance = float(cfg.budget)
    instance.freq_cap = cfg.frequency_capping

    db.session.add(instance)
    db.session.commit()

    create_default_creative(instance)

    return instance
