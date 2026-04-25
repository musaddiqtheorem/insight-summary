import requests
import csv
import time
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("KLAVIYO_API_KEY")

BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": "2023-10-15"
}

OUTPUT_FILE = "data/raw/events.csv"

# 🔥 TEST CONFIG
DAYS_BACK = 1
LIMIT_PER_EVENT = 10

start_date = (datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)).strftime("%Y-%m-%dT%H:%M:%SZ")

# 🔥 HARDCODED METRIC IDS (from your account)
TARGET_METRICS = {
    "XfQVkd": "view_product",   # Viewed Product
    "VapDiV": "add_to_cart",    # Added to Cart
    "XX5eZB": "purchase",        # Placed Order
    # Add later if needed:
    # "metric_id_here": "purchase"
}


# ✅ Safe request
def safe_request(url, params=None):
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if response.status_code == 200:
            return response
        else:
            print("API error:", response.text)
    except Exception as e:
        print("Request failed:", e)

    return None


# ✅ Fetch events
def fetch_events(metric_id, event_name):
    url = f"{BASE_URL}/events/"
    all_rows = []

    params = {
        "filter": f"equals(metric_id,'{metric_id}')",
        "page[size]": 50
    }

    print(f"\n🔄 Fetching {event_name}...")

    while True:
        response = safe_request(url, params)

        if not response:
            break

        data = response.json()
        events = data.get("data", [])

        for event in events:
            attr = event.get("attributes", {})

            # ✅ Correct profile extraction
            try:
                profile_id = event["relationships"]["profile"]["data"]["id"]
            except:
                continue

            timestamp = attr.get("datetime")

            if profile_id and timestamp:
                all_rows.append({
                    "user_id": profile_id,
                    "timestamp": timestamp
                })

                # Progress log
                if len(all_rows) % 5 == 0:
                    print(f"{event_name}: {len(all_rows)} records")

                # Limit for testing
                if len(all_rows) >= LIMIT_PER_EVENT:
                    print(f"✅ Done {event_name}")
                    return all_rows

        next_link = data.get("links", {}).get("next")

        if not next_link:
            break

        url = next_link
        params = None

        time.sleep(0.2)

    return all_rows


def main():
    print("\n🚀 Starting event extraction...\n")

    all_events = []

    for metric_id, event_type in TARGET_METRICS.items():
        events = fetch_events(metric_id, event_type)

        for e in events:
            e["event_type"] = event_type

        all_events.extend(events)

    # Ensure folder exists
    os.makedirs("data/raw", exist_ok=True)

    print(f"\n💾 Saving {len(all_events)} events...")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["user_id", "event_type", "timestamp"])
        writer.writeheader()
        writer.writerows(all_events)

    print("✅ events.csv ready!")


if __name__ == "__main__":
    main()