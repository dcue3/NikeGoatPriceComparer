import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import sys

def scrape_sneaker_prices(goat_url, filter_profit, overwrite_csv):
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(goat_url)
    except Exception as e:
        print(f"Failed to load URL {goat_url}: {e}")
        driver.quit()
        return

    scroll_pause_time = 2
    # last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(50):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        # new_height = driver.execute_script("return document.body.scrollHeight")
        # if new_height == last_height:
        #     break
        # last_height = new_height

    goat_soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = goat_soup.find_all('a', class_='GridCellLink__Link-sc-2zm517-0 VoJbO')
    profitable = []

    base_url = "https://www.goat.com"

    try:
        for resultOne in results:
            endLink = resultOne.get('href')
            if endLink is None:
                continue

            full_link = base_url + endLink
            driver.get(full_link)

            try:
                # Wait for the price element to be present
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-qa='buy_bar_price_size_9']")))
                goatpage_soup = BeautifulSoup(driver.page_source, 'html.parser')

                price_element = goatpage_soup.find('span', {'data-qa': 'buy_bar_price_size_9'})
                if price_element:
                    priceProcessed2 = price_element.get_text()[1:]
                else:
                    priceProcessed2 = "Price not found"
                priceProcessed = int(priceProcessed2.replace(',', ''))
                snkrName = goatpage_soup.find('h1', class_='ProductInfo__Name-sc-yvcr9v-2 bMmuxU').get_text()

                snkrYearPre = goatpage_soup.find('div', class_='ProductInfo__Container-sc-yvcr9v-1 irvBLb')
                if snkrYearPre:
                    snkrYear = snkrYearPre.find('span').get_text()
                    if len(snkrYear) != 4:
                        snkrYear = "2024"
                else:
                    snkrYear = "Unknown"
                # could be exiting before this or something?
                if len(endLink) >= 10:
                    # Correct case: Extract the last 10 characters
                    sku = endLink[-10:].upper()
                else:
                    # Handle case where endLink is shorter than 10 characters
                    sku = endLink.upper()

                print(sku)
                profitable.append((sku, snkrName, 0, 0, 0, priceProcessed, str(snkrYear), "", full_link))
            except Exception as e:
                print(f"Failed to retrieve data for {full_link}: {e}")
                continue

    except Exception as e:
        print(e)

    profitable = sorted(profitable, key=lambda x: x[2], reverse=True)
    header = ("SKU", "Name", "Profit ($)", "Profit (%)", "Retail Price ($)", "Resale Price ($)", "Year", "Nike Link", "Goat Link")

    file_exists = os.path.isfile('NikeParserResults.csv')
    mode = 'w' if overwrite_csv or not file_exists else 'a'

    with open('NikeParserResults.csv', mode, newline='') as file:
        writer = csv.writer(file)
        if mode == 'w' or os.path.getsize('NikeParserResults.csv') == 0:
            writer.writerow(header)
        writer.writerows(profitable)

    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        goat_url = ""
        filter_profit = False
        overwrite_csv = False

        for arg in sys.argv[1:]:
            if arg.startswith("http"):
                goat_url = arg
            elif arg == "--filter-profit":
                filter_profit = True
            elif arg == "--overwrite-csv":
                overwrite_csv = True

        if goat_url:
            scrape_sneaker_prices(goat_url, filter_profit, overwrite_csv)
        else:
            print("Please provide a valid URL.")
    else:
        print("Please provide a URL.")
