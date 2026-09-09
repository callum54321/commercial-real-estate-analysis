from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import math
import pandas as pd

url = "https://hongkongoffices.com/en/commercial-property/for-rent?order=prd"

# Set options
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(3)

listings = []

while True:
    print("Starting data scrape...")

    # Results container
    container = driver.find_element(
        By.CSS_SELECTOR, "div[class*='search-result-container']"
    )

    # Property cards
    cards = container.find_elements(
        By.CSS_SELECTOR, "div[class*='property-item']"
    )

    # Data wrangling loop
    for index, card in enumerate(cards):
        print(f"Gather data from listing {index + 1}/{len(cards)}")

        # Scroll for lazy load
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
        time.sleep(0.4)

        # Building name element
        building_name = card.find_element(By.CSS_SELECTOR, "h3[class*='card-title']").text

        # District element
        p_tag = card.find_element(By.CSS_SELECTOR, "p[class*='card-text']")
        district = p_tag.find_element(By.CSS_SELECTOR, "span[class*='district']").text

        # Square feet element
        sq_ft = card.find_element(By.XPATH, ".//*[contains(., 'Size:')]").text

        # Price element
        price = card.find_element(By.CSS_SELECTOR, "span[class*='price-in-hkd']").text

        listings.append({
            "bldg_name" : building_name,
            "district": district,
            "sq_ft": sq_ft,
            "price": price,
        })

    try:
        print("Attempting to click next button...")
        pagination = driver.find_element(By.CSS_SELECTOR, "ul[class*='pagination']")

        next_button = WebDriverWait(pagination, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '›')]"))
        )

        if "disabled" in next_button.get_attribute("class"):
            print("Next button disabled, reached the last page...")
            driver.quit()
            break

        next_button.click()
        print("Navigating to next page...")

    except Exception:
        print("Next button unavailable")
        break

df = pd.DataFrame(listings)
df.to_csv("listings.csv", index=False)