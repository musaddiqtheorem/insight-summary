import requests
import time
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("KLAVIYO_API_KEY")

BASE_URL = "https://a.klaviyo.com/api"
HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": "2023-10-15"
}

TARGET_METRICS = [
    "Viewed Product",
    "Added to Cart"
]


def safe_request(url, params=None):
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        print(f"\n🌐 Request URL: {response.url}")
        print(f"Status Code: {response.status_code}")

        if response.status_code != 200:
            print("❌ API Error:", response.text)
            return None

        return response

    except Exception as e:
        print("❌ Request failed:", e)
        return None


def get_metric_ids():
    print("\n🔍 Fetching metric IDs...\n")

    url = f"{BASE_URL}/metrics/"
    response = safe_request(url)

    if not response:
        return {}

    data = response.json().get("data", [])

    metric_map = {}

    for metric in data:
        name = metric["attributes"]["name"]
        metric_id = metric["id"]

        print(f"Found metric: {name}")

        if name in TARGET_METRICS:
            metric_map[name] = metric_id
            print(f"✅ Matched target metric: {name}")

    print("\n📌 Final metric mapping:", metric_map)
    return metric_map


def debug_events(metric_id, event_name):
    print(f"\n🚀 DEBUGGING EVENTS: {event_name}")

    url = f"{BASE_URL}/events/"

    params = {
        # 🔥 NO DATE FILTER (important for debugging)
        "filter": f"equals(metric_id,'{metric_id}')",
        "page[size]": 10
    }

    response = safe_request(url, params)

    if not response:
        return

    data = response.json()

    print("\n🔍 FULL RESPONSE STRUCTURE:")
    print(data)

    events = data.get("data", [])

    print(f"\n📊 Events returned: {len(events)}")

    if not events:
        print("⚠️ No events found for this metric")
        return

    print("\n🧪 SAMPLE EVENT:")
    print(events[0])

    attr = events[0].get("attributes", {})

    print("\n🔍 ATTRIBUTE KEYS:")
    print(attr.keys())

    print("\n🔍 PROFILE ID:")
    print(attr.get("profile_id"))

    print("\n🔍 DATETIME:")
    print(attr.get("datetime"))


def main():
    print("\n==============================")
    print("🔥 KLAVIYO EVENT DEBUG MODE")
    print("==============================\n")

    metric_ids = get_metric_ids()

    if not metric_ids:
        print("❌ No metrics found. Check API key or account.")
        return

    for name in TARGET_METRICS:
        metric_id = metric_ids.get(name)

        if not metric_id:
            print(f"\n⚠️ Metric NOT FOUND: {name}")
            continue

        debug_events(metric_id, name)

        # Only debug first working metric
        break


if __name__ == "__main__":
    main()