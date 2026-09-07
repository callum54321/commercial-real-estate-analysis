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

    # Remove leading text from address string
    df["address_text"] = df["address_text"].str.replace("Office Space in ", "")

    # Format price data
    df["price"] = df["price"].apply(parse_price)

    # Create dummy tags
    tags_exploded = df["tags"].explode().str.lower()
    tags_dummies = pd.get_dummies(tags_exploded).groupby(level=0).max()
    df = df.join(tags_dummies)

    # Drop missing values
    df.dropna(subset=["address_text", "price"], inplace=True)

    # Reset df index
    df.reset_index(drop=True, inplace=True)

    print(df)
    df.to_csv('data.csv', index=False)