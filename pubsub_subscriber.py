# pubsub_subscriber.py

from google.cloud import pubsub_v1
import os
import json
from models import db, WeatherAlert

# GCP Project and Subscription ID
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'true-area-464010-j9')
SUBSCRIPTION_ID = os.getenv('SUBSCRIPTION_ID', 'iaac-test-sub')

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(GCP_PROJECT_ID, SUBSCRIPTION_ID)

def start_subscriber(app):
    def callback(message):
        try:
            # Decode and parse the message
            payload = message.data.decode('utf-8')
            data = json.loads(payload)

            print(f"[Pub/Sub] Received message: {data}")

            # Store in the database
            with app.app_context():
                alert = WeatherAlert(
                    location_name=data.get("location_name", "Unknown"),
                    region=data.get("region", ""),
                    country=data.get("country", ""),
                    alert_time=data.get("alert_time"),  # ISO string expected
                    raw_data=json.dumps(data)
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
