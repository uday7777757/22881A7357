from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class ShortURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    shortcode = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expiry = db.Column(db.DateTime, nullable=False)
    clicks = db.relationship('ClickLog', backref='shorturl', lazy=True)

class ClickLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shorturl_id = db.Column(db.Integer, db.ForeignKey('short_url.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    referrer = db.Column(db.String(255))
    location = db.Column(db.String(100))