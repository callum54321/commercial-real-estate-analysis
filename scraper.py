from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import math

# Calculate total pages
def calc_total_pages(driver: object) -> int:
    element = driver.find_element(
        By.XPATH, "//*[contains(text(), 'results')]"
    )
    element_text = element.text
    results_count = element_text.split()[0]
    results_int = int(results_count)
    total_pages = math.ceil(results_int / 20)

    return total_pages

# Scraping pipeline
def run_scraper(url: str) -> list[dict]:
    # Set options
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    # Start webdriver
    driver = webdriver.Chrome(options=options)

    # Base URL
    base_url = url

    # Try...Except scraping block
    try:
            driver.get(base_url)
            print("Starting data scrape...")

            total_pages = calc_total_pages(driver)

            results = []

            # Pagination loop
            for page in range(1, 2):
                current_url = f"{base_url}?page={page}"

                driver.get(current_url)
                time.sleep(3)

                # Wait for cards to appear
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "li[class*='OfficeCard-module']")
                    )
                )

                cards = driver.find_elements(
                    By.CSS_SELECTOR, "li[class*='OfficeCard-module']"
                )

                # card (listings) loop
                for card in cards:
                    # Scroll into card (lazy load workaround)
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(0.4)

                    # Address href
                    address_element = card.find_element(
                        By.XPATH, ".//*[@data-name='listings-page-centre-name']"
                        )
                    address_href = address_element.get_attribute("href")

                    # Price element
                    price = card.find_element(
                        By.XPATH, ".//*[@data-name='listings-page-centre-price']"
                    ).text

                    # Tags elements
                    tags = []
                    li_elements = card.find_elements(
                        By.CSS_SELECTOR, "ul[class*='amenitiesItem'] li, li[class*='amenitiesItem']"
                    )
                    for li in li_elements:
                        tags.append(li.text)

                    results.append({
                        "address_href": address_href,
                        "price": price,
                        "tags": tags,
                    })
                print(f"Found {len(cards)} results on page {page}")

            # href loop (address gathering)
            for index, result in enumerate(results):
                driver.get(result["address_href"])
                time.sleep(2)

                print(f"Navigating to link {index}/{len(results)}...")

                address = driver.find_element(
                    By.CSS_SELECTOR, "h1[class*='text-base-content']"
                ).text
                result["address_text"] = address

            return results

    except Exception as e:
        print(f"Error while attempting to connect: {e}")

    finally:
        driver.quit()
