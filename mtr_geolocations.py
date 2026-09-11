import pandas as pd
import googlemaps
from dotenv import load_dotenv
import os

# Load env variables
load_dotenv()
API_KEY = os.getenv("MAPS_API")

# Import and clean CSV
df = pd.read_csv("mtr.csv")

df = df.drop_duplicates(
    subset=["English Name"],
    ignore_index=True
    )
df = df.dropna()

gmaps = googlemaps.Client(key=API_KEY)

mtr_stations = []

# API request loop
for index, station in enumerate(df["English Name"]):
    print(f"Getting location for station {index}...")
    
    address = f"{station} MTR Station, Hong Kong"
    geocode_result = gmaps.geocode(address)

    if geocode_result:
        print(f"Address found for station {index}")
        location = geocode_result[0]["geometry"]["location"]
        lat = location["lat"]
        lon = location["lng"]

        mtr_stations.append({
            "Name": station,
            "coords": (lat, lon)
        })
    else:
        print(f"Invalid address for station {index}...")

mtr_df = pd.DataFrame(mtr_stations)
mtr_df.to_csv("mtr_geolocations.csv", index=False)
