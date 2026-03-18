
import geohash2
import random
import string

def decode_parkopedia_location(location):
    """
    Extract and decode the embedded geohash from a Parkopedia location token.
    """
    if len(location) < 18:
        raise ValueError("Location token too short to be valid")

    # Extract according to JS logic
    geohash_part = location[4:15]  # chars 4 → 14 (11 chars total)

    lat, lon = geohash2.decode(geohash_part)

    return {
        "original": location,
        "geohash": geohash_part,
        "latitude": lat,
        "longitude": lon
    }



# Parkopedia uses base-20 chars: 0–9 + a–j
BASE20_CHARS = string.digits + string.ascii_lowercase[:10]

def random_base20(length):
    return ''.join(random.choice(BASE20_CHARS) for _ in range(length))

def encode_parkopedia_location(lat, lon):
    """
    Encode latitude/longitude into a Parkopedia-compatible location token.

    JS equivalent:
      hash = ngeohash.encode(lat, lng, 11)
      hash = random(4) + hash + random(3)
    """
    
    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid lat/lon values: lat={lat}, lon={lon}")
    geohash_part = geohash2.encode(lat, lon, precision=11)
    prefix = random_base20(4)
    suffix = random_base20(3)

    # return f"{prefix}{geohash_part}{suffix}"

    return {
        "full": f"{prefix}{geohash_part}{suffix}",
        "prefix": prefix,
        "geohash": geohash_part,
        "suffix": suffix,
        "latitude": lat,
        "longitude": lon
    }


#  VALIDATION
# token = "b6e4u151e1dvskech0"

# decoded = decode_parkopedia_location(token)

# print(f"Decoded Parkopedia location {token}")
# print("---------------------------")
# print(f"Original token : {decoded['original']}")
# print(f"Geohash        : {decoded['geohash']}")
# print(f"Latitude       : {decoded['latitude']}")
# print(f"Longitude      : {decoded['longitude']}")



# lat = decoded['latitude']
# lon = decoded['longitude']

# location = encode_parkopedia_location(lat, lon)
# print(f"Encoded location: {location}")


# decoded = decode_parkopedia_location(location["full"])

# print(f"Decoded Parkopedia location {location}")
# print("---------------------------")
# print(f"Original token : {decoded['original']}")
# print(f"Geohash        : {decoded['geohash']}")
# print(f"Latitude       : {decoded['latitude']}")
# print(f"Longitude      : {decoded['longitude']}")


