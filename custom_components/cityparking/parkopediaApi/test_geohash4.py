import geohash2
import random
import string
import requests

BASE20_CHARS = string.digits + string.ascii_lowercase[:10]  # 0-9 + a-j

def random_base20(n):
    return ''.join(random.choice(BASE20_CHARS) for _ in range(n))

def encode_parkopedia_location(lat, lon):
    gh = geohash2.encode(lat, lon, precision=11)
    return f"{random_base20(4)}{gh}{random_base20(3)}"

def get_locations_by_latlon(lat, lon, dates):
    location = encode_parkopedia_location(lat, lon)

    url = "https://www.parkopedia.fr/api/locations/"
    params = {
        "location": location,
        "dates": dates,
        "apiver": 40,
        "cid": "avalon_iu4ryufghgjrf"
    }

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    return r.json()

data = get_locations_by_latlon(
    50.8503,
    4.3517,
    "202602101800-202602102000"
)

print(data.keys())
