from flask import Flask, jsonify, request, render_template
from models import db, WeatherAlert
from config import Config
# from pubsub_subscriber import start_subscriber
import threading
import base64

from google.cloud import pubsub_v1
import os
import json


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/alerts', methods=['GET'])
def get_alerts():
    alerts = WeatherAlert.query.order_by(WeatherAlert.alert_time.desc()).limit(10).all()
    return render_template('alerts.html', alerts=alerts)

# # pubsub_subscriber.py

# GCP Project and Subscription ID
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'true-area-464010-j9')
SUBSCRIPTION_ID = os.getenv('SUBSCRIPTION_ID', 'iaac-topic-sub')

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(GCP_PROJECT_ID, SUBSCRIPTION_ID)

def start_subscriber(app):
    print(f"[Pub/Sub] Listening for messages on {subscription_path}...")
    def callback(message):
        try:
            # Decode and parse the message
            payload = message.data.decode('utf-8')
            data = json.loads(payload)

            print(f"[Pub/Sub] Received message: {data}")

            # Store in the database
            with app.app_context():
                alert = WeatherAlert(
                    location_name=data["location"].get("name", "Unknown"),
                    region=data["location"].get("region", ""),
                    country=data["location"].get("country", ""),
                    alert_time=data["current"].get("last_updated"),
                    temp_c=data["current"].get("temp_c"),
                    condition=data["current"]["condition"].get("text"),
                    wind_kph=data["current"].get("wind_kph")
                )
                db.session.add(alert)
                db.session.commit()
                print("[DB] Weather alert saved.")
            
            message.ack()
        except Exception as e:
            print(f"[Error] Failed to process message: {e}")
            message.nack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"[Pub/Sub] Listening for messages on {subscription_path}...")

    try:
        streaming_pull_future.result()
    except Exception as e:
        streaming_pull_future.cancel()
        print(f"[Pub/Sub] Stopped listening due to error: {e}")

from sqlalchemy.exc import SQLAlchemyError


try:
    with app.app_context():
        db.create_all()
        print("[DB] Successfully connected and created tables.")
except SQLAlchemyError as e:
    print(f"[DB Error] {e}")

def start_background_services():
    with app.app_context():
        print("Running background services...")
        db.create_all()
        threading.Thread(target=start_subscriber, args=(app,), daemon=True).start()

start_background_services()

if __name__ == '__main__':
    print("Starting subscriber")
    with app.app_context():
        threading.Thread(target=start_subscriber, args=(app,), daemon=True).start()
        db.create_all()
    app.run(host='0.0.0.0', port=5000) 