import pandas as pd
import re

# CSV to dataframe
df = pd.read_csv("../data/scraped_listings.csv")

# Drop missing values
df.dropna(inplace=True)

# Sq ft value extraction
df["sq_ft"] = df["all_info"].str.extract(r"\bSize:\s+([\d,]+)\s+s.f\b")
df["sq_ft"] = df["sq_ft"].str.replace(",", "")
df["sq_ft"] = df["sq_ft"].astype(int)

# Total price value extraction
df["price"] = df["price"].str.replace(",", "")
df["price_total"] = df["price"].astype(int)

# Price per sq ft
df["price_sq_ft"] = df["price_total"] / df["sq_ft"]
df["price_sq_ft"] = df["price_sq_ft"].astype(int)

# Drop all_info, price columns
df = df.drop(columns=["all_info", "price"])
