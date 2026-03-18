import pygeohash as pgh

gh = "b6e4u151e1dvskech0"
print(pgh.decode(gh))


import pygeohash as pgh

gh = "b6e4u151e1dvskech0"

lat, lon, lat_err, lon_err = pgh.decode_exactly(gh)

print("Center:", lat, lon)
print("Lat range:", lat - lat_err, lat + lat_err)
print("Lon range:", lon - lon_err, lon + lon_err)