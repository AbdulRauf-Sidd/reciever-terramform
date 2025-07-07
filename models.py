from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, UTC

db = SQLAlchemy()

class WeatherAlert(db.Model):
    __tablename__ = 'weather_alerts'

    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(128))
    region = db.Column(db.String(128))
    country = db.Column(db.String(128))
    alert_time = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    temp_c = db.Column(db.Float)
    condition = db.Column(db.String(128))
    wind_kph = db.Column(db.Float)

    def __init__(self, location_name, region, country, alert_time, temp_c, condition, wind_kph):
        self.location_name = location_name
        self.region = region
        self.country = country
        self.alert_time = alert_time
        self.temp_c = temp_c
        self.condition = condition
        self.wind_kph = wind_kph