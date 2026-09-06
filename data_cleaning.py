from scraper import run_scraper
from dotenv import load_dotenv
import os
import pandas as pd
import re

# Load env variables
load_dotenv()
url = os.getenv("URL")

# Price parsing function
def parse_price(price_str: str) -> str:
    if not price_str or price_str.strip() == "":
        return None
    # Extract the number element
    price = re.sub(r"\D", "", price_str)

    return price

if __name__ == "__main__":
    raw_data = run_scraper(url)

    # Initialize dataframe
    df = pd.DataFrame(raw_data)

    # Remove trailing/leading whitespaces from address
    df["address"] = df["address"].str.strip()

    # Format price data
    df["price"] = df["price"].apply(parse_price)

    # Create dummy tags
    tags_exploded = df["tags"].explode().str.strip().str.lower()
    tags_dummies = pd.get_dummies(tags_exploded).groupby(level=0).max()
    df = df.join(tags_dummies)

    # Drop missing values
    df.dropna(subset=["address", "price"], inplace=True)

    # Reset index
    df.reset_index(drop=True, inplace=True)

    print(df)