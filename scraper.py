from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import math

# Calculate total pages
def calc_total_pages(driver):
    element = driver.find_element(
        By.XPATH, "//*[contains(text(), 'results')]"
    )
    element_text = element.text
    results_count = element_text.split()[0]
    results_int = int(results_count)
    total_pages = math.ceil(results_int / 20)

    return total_pages


def run_scraper(url):
    # Set options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
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

            for page in range(1, total_pages + 1):
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

                for card in cards:
                    # Scroll into card (lazy load workaround)
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(0.4)

                    # Address element
                    address = card.find_element(
                        By.XPATH, ".//*[@data-name='listings-page-centre-name']"
                    ).text

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
                        "address": address,
                        "price": price,
                        "tags": tags,
                    })
                    
                print(f"Found {len(results) / page} results on page {page}")

            print(f"Results: {results}")

            return results

    except Exception as e:
        print(f"Error while attempting to connect: {e}")

    finally:
        driver.quit()
