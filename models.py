from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

db = SQLAlchemy()

class WeatherAlert(db.Model):
    __tablename__ = 'weather_alerts'
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(128))
    region = db.Column(db.String(128))
    country = db.Column(db.String(128))
    alert_time = db.Column(db.DateTime, default=datetime.utcnow)
    raw_data = db.Column(JSONB)

    def __init__(self, location_name, region, country, alert_time, raw_data):
        self.location_name = location_name
        self.region = region
        self.country = country
        self.alert_time = alert_time
        self.raw_data = raw_data 