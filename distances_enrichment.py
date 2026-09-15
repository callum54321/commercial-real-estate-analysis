import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree

# Initialize dataframes (listings and mtr geolocation data)
listings_df = pd.read_csv("enriched_listings.csv")
mtr_df = pd.read_csv("mtr_geolocations.csv")

# Drop NaN lat and lon
listings_df.dropna(subset=["latitude", "longitude"], inplace=True)
mtr_df.dropna(subset=["coords"], inplace=True)

# Separate lat, lon for mtr df
mtr_df[["latitude", "longitude"]] = mtr_df["coords"].str.strip("() ").str.split(",", expand=True).astype(float)

# Convert coords to radians (BallTree required)
mtr_coords = np.radians(mtr_df[["latitude", "longitude"]].values)
listings_coords = np.radians(listings_df[["latitude", "longitude"]].values)

# Build haversine tree
tree = BallTree(mtr_coords, metric="haversine")
distances, indices = tree.query(listings_coords, k=1)

# Get nearest mtr distances in km
distances_m = distances.flatten() * 6371 * 1000

# Add nearest mtr distance results
listings_df["nearest_mtr_distance_m"] = distances_m
listings_df["nearest_mtr_name"] = mtr_df.iloc[indices.flatten()]["Name"].values

# Get stations within radius 1km
radius_m = 1000
radius_rad = radius_m / 6371000

indices_within_radius = tree.query_radius(listings_coords, r=radius_rad)

# Count stations within radius and add to df
listings_df["stations_within_1km"] = [len(index) for index in indices_within_radius]

listings_df.to_csv("final_dataset.csv")