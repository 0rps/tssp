from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

app = Flask("rtb")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rtb.sqlite3'

db = SQLAlchemy(app)


class ConfigurationModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actual = db.Column(db.Boolean)
    impressions_total = db.Column(db.Integer)
    auction_type = db.Column(db.String(16), nullable=False)
    game_goal = db.Column(db.String(16),  nullable=False)
    mode = db.Column(db.String(16),  nullable=False)
    budget = db.Column(db.Integer)
    impression_revenue = db.Column(db.Integer)
    click_revenue = db.Column(db.Integer)
    conversion_revenue = db.Column(db.Integer)
    frequency_capping = db.Column(db.Integer)
    current_impression = db.Column(db.Integer)


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    budget = db.Column(db.Integer)
    balance = db.Column(db.Float)
    creatives = db.relationship('Creative', backref='campaign')


creative_category = db.Table('creative_category',
                             db.Column('category_id', db.Integer, db.ForeignKey('category.id')),
                             db.Column('creative_id', db.Integer, db.ForeignKey('creative.id')),
                             )


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    code = db.Column(db.String(16))


class Creative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    external_id = db.Column(db.String(128), unique=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey(Campaign.id))
    categories = db.relationship('Category', secondary=creative_category, backref='creatives')
    image_url = db.Column(db.String(512))

    def is_allowed(self, blocked_categories):
        cats = [x.code for x in self.categories]
        for blocked in blocked_categories:
            if blocked in cats:
                return False

            for cat in cats:
                if cat.startswith(blocked):
                    return False

        return True


class BidObject(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    impression_index = db.Column(db.Integer)
    bid = db.Column(db.Float)
    status = db.Column(db.String(16))
    configuration_id = db.Column(db.Integer)
    creative_id = db.Column(db.Integer)
    real_revenue = db.Column(db.Integer)


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64))
    campaign_id = db.Column(db.Integer)
