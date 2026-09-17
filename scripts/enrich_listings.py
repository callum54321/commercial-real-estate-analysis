import googlemaps
from dotenv import load_dotenv
import os
from clean_scraped_listings import df

# Load env variables
load_dotenv(dotenv_path="../.env")
API_KEY = os.getenv("MAPS_API")

gmaps = googlemaps.Client(key=API_KEY)

# Empty arrays for lat and lon
latitudes = []
longitudes = []

# Place types list and storage
place_types = ["gym", "cafe", "restaurant"]
amenity_counts = {place: [] for place in place_types}

# Deduplicate building names 
unique_locations = df.drop_duplicates(ignore_index=True, subset=["bldg_name", "district"])[["bldg_name", "district"]].copy()

# Geolocation request loop
for index, listing in unique_locations.iterrows():
    print(f"Enriching {index + 1}/{len(unique_locations)} listings...")
    address = f"{listing['bldg_name']}, {listing['district']}"

    result = gmaps.geocode(address)

    if result:
        print(f"Address found for: {index + 1}/{len(unique_locations)}")

        location = result[0]["geometry"]["location"]
        latitudes.append(location["lat"])
        longitudes.append(location["lng"])

        # Nearby lifestyle amenities loop
        for place in place_types:
            try:
                nearby_result = gmaps.places_nearby(
                    location=(location["lat"], location["lng"]),
                    radius=100,
                    type=place
                )
                amenities = nearby_result.get("results", [])
                amenity_counts[place].append(len(amenities))
            except Exception as e:
                print(f"Error searching for {place}: {e}")
                amenity_counts[place].append(None)
    else:
        print(f"Invalid address for listing: {index + 1}/{len(unique_locations)}")
        latitudes.append(None)
        longitudes.append(None)
        for place in place_types:
            amenity_counts[place].append(None)

# Append coordinates to df
unique_locations["latitude"] = latitudes
unique_locations["longitude"] = longitudes

# Amenity counts loop - append to df
for place in place_types:
    unique_locations[f"num_{place}s_within_100m"] = amenity_counts[place]

enriched_listings = df.merge(unique_locations, on=["bldg_name", "district"], how="left")
enriched_listings.to_csv("../data/enriched_listings.csv", index=False)
