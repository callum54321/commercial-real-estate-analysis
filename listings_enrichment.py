import pandas as pd
import googlemaps
from dotenv import load_dotenv
import os
from data_cleaning import df

# Load env variables
load_dotenv()
API_KEY = os.getenv("MAPS_API")

gmaps = googlemaps.Client(key=API_KEY)

latitudes = []
longitudes = []

# Geolocation request loop
for index, listing in df.iterrows():
    address = f"{listing["bldg_name"]}, {listing["district"]}"

    result = gmaps.geocode(address)

    if result:
        print(f"Address found for: {index + 1}/{len(df)}")

        location = result[0]["geometry"]["location"]
        latitudes.append(location["lat"])
        longitudes.append(location["lng"])
    else:
        print(f"Invalid address for listing: {index + 1}/{len(df)}")
        latitudes.append(None)
        longitudes.append(None)

df["latitude"] = latitudes
df["longitude"] = longitudes

df.to_csv("enriched_listings.csv", index=False)
