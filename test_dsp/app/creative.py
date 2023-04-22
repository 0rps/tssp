from .app import db, Creative, Category


def generate_creative_url(creative, w, h):
    return creative.image_url


def select_creatives():
    res = []
    for creative in db.session.query(Creative):
        res.append({
            'id': creative.id,
            'name': creative.name,
            'external_id': creative.external_id,
            'image_url': creative.image_url,
            'campaign': {'id': creative.campaign_id},
            'categories': [{'id': x.id, 'code': x.code} for x in creative.categories],
        })
    return res


def create_default_categories():
    count = db.session.query(Category.id).count()
    if count > 0:
        return

    for i in range(1, 26):
        category_code = f"IAB{i}"
        for j in range(0, 25):
            if j > 0:
                category_code = f"IAB{i}-{j}"
            cat = Category()
            cat.name = category_code
            cat.code = category_code
            db.session.add(cat)
    db.session.commit()


def create_creative(creative_data):
    creative = Creative()

    creative.name = creative_data['name']
    creative.campaign_id = creative_data['campaign']['id']
    creative.external_id = creative_data['external_id']
    creative.image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR74m2G-qXqwQ2B_mnAh-xOuv1zT-WVyOhqqGjvDfymKg&s'

    categories = [Category.query.filter_by(code=x['code']).first() for x in creative_data['categories']]
    for cat in categories:
        creative.categories.append(cat)

    db.session.add(creative)

    return creative


def create_default_creative(campaign):
    creative = Creative()

    creative.name = "free mode creative"
    creative.campaign_id = campaign.id
    creative.external_id = f"free_mode_creative_{campaign.id}"
    creative.image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR74m2G-qXqwQ2B_mnAh-xOuv1zT-WVyOhqqGjvDfymKg&s'

    db.session.add(creative)
    return creative
