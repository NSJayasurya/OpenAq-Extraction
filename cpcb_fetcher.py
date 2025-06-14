import requests
import time
from datetime import datetime
import pytz

API_KEY = "14c2cde1d3c9d59447453abc64177323f6c1beee850d45e7770c471dc4df4628"
BASE_URL = "https://api.openaq.org/v3"
HEADERS = {"X-API-Key": API_KEY}

CITY_BBOX = {
    "chennai": (80.080170, 12.779249, 80.332855, 13.232850),
    "delhi": (76.8381, 28.4126, 77.3477, 28.8814),
    "gurugram": (76.9895, 28.3194, 77.1731, 28.5135)
}


def get_cpcb_location_ids(min_lon, min_lat, max_lon, max_lat):
    print("📍 Fetching CPCB location IDs...")
    location_ids = []
    page = 1

    while True:
        try:
            url = f"{BASE_URL}/locations"
            params = {
                "bbox": f"{min_lon},{min_lat},{max_lon},{max_lat}",
                "limit": 100,
                "page": page
            }
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
        except Exception as e:
            print(f"❌ Failed to fetch locations: {e}")
            break

        if not results:
            break

        for loc in results:
            provider = loc.get("provider", {})
            if provider.get("id") == 168 and provider.get("name") == "CPCB":
                location_ids.append(loc["id"])

        if len(results) < 100:
            break
        page += 1

    if not location_ids:
        print("⚠ No CPCB locations found for the given bounding box.")
    else:
        print(f"✔ Found {len(location_ids)} CPCB location IDs.")

    return location_ids


def get_latest_sensors(location_id):
    url = f"{BASE_URL}/locations/{location_id}/latest"
    try:
        response = requests.get(url, headers=HEADERS)
        time.sleep(1)
        if response.status_code == 200:
            data = response.json()
            return list(set(item.get("sensorsId") for item in data.get("results", []) if item.get("sensorsId")))
    except Exception as e:
        print(f"❌ Failed to fetch sensors for location {location_id}: {e}")
    return []


def parse_datetime(dt_str):
    """Parse ISO datetime string and return datetime object"""
    try:
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None


def get_all_measurements(sensor_id, location_id, frequency="hourly", from_date=None, to_date=None):
    all_data = []
    page = 1
    max_pages = 100  # safety limit to prevent infinite loop
    print(f"   🔎 Filtering data from {from_date} to {to_date}")

    # Parse input dates to datetime objects with timezone
    tz = pytz.timezone("Asia/Kolkata")
    from_dt = tz.localize(datetime.strptime(from_date, "%Y-%m-%d"))
    to_dt = tz.localize(datetime.strptime(to_date, "%Y-%m-%d"))

    while page <= max_pages:
        url = f"{BASE_URL}/sensors/{sensor_id}/measurements/{frequency}"
        params = {"page": page, "limit": 100}
        try:
            response = requests.get(url, headers=HEADERS, params=params)
            time.sleep(1)
            if response.status_code != 200:
                print(f"❌ Sensor {sensor_id} page {page} failed: {response.status_code}")
                break
            results = response.json().get("results", [])
        except Exception as e:
            print(f"❌ Error fetching data for sensor {sensor_id}: {e}")
            break

        if not results:
            break

        for entry in results:
            period = entry.get("period", {})
            period_from_str = period.get("datetimeFrom", {}).get("local")
            period_from = parse_datetime(period_from_str)
            if not period_from:
                continue

            # Only keep data within user-defined date range
            if not (from_dt <= period_from < to_dt):
                continue

            param = entry.get("parameter", {})
            summary = entry.get("summary", {})
            coverage = entry.get("coverage", {})

            record = {
                "location_id": location_id,
                "sensor_id": sensor_id,
                "value": entry.get("value"),
                "parameter_id": param.get("id"),
                "parameter_name": param.get("name"),
                "units": param.get("units"),

                "period_label": period.get("label"),
                "period_from_utc": period.get("datetimeFrom", {}).get("utc"),
                "period_to_utc": period.get("datetimeTo", {}).get("utc"),
                "period_from_local": period_from_str,
                "period_to_local": period.get("datetimeTo", {}).get("local"),

                "summary_avg": summary.get("avg"),
                "summary_min": summary.get("min"),
                "summary_max": summary.get("max"),
                "summary_median": summary.get("median"),
                "summary_sd": summary.get("sd"),

                "coverage_percent": coverage.get("percentCoverage"),
                "coverage_complete": coverage.get("percentComplete"),
                "coverage_expected_count": coverage.get("expectedCount"),
                "coverage_observed_count": coverage.get("observedCount"),
                "coverage_from_utc": coverage.get("datetimeFrom", {}).get("utc"),
                "coverage_to_utc": coverage.get("datetimeTo", {}).get("utc"),
                "coverage_from_local": coverage.get("datetimeFrom", {}).get("local"),
                "coverage_to_local": coverage.get("datetimeTo", {}).get("local"),
            }

            all_data.append(record)

        page += 1

    if not all_data:
        print(f"⚠ No data found for sensor {sensor_id} in the given range.")

    return all_data
