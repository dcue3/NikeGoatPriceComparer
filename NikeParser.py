import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import csv
import sys # FN4216-001

def scrape_sneaker_prices(nike_url, filter_profit, overwrite_csv):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.google.com/',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)
    # driver = webdriver.Chrome()
    driver.get(nike_url)
    scroll_pause_time = 1
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_links = soup.select('a.product-card__link-overlay')
    links = [l.get("href") for l in product_links]
    product_prices = []

    for link in links:
        full_link = link
        response = requests.get(full_link, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            price_element = soup.select_one('.product-price')
            sku_element = soup.select_one('.description-preview__style-color')
            if price_element and sku_element:
                price = price_element.get_text() #delete this
                sku = sku_element.get_text()
                product_prices.append((full_link, price[1:], sku[7:]))
            else:
                product_prices.append((full_link, "ERROR", "ERROR"))
        else:
            product_prices.append((full_link, "ERROR", "ERROR"))

    profitable = []
    for product in product_prices:
        goat_url = f'https://www.goat.com/search?query={product[2]}'
        driver.get(goat_url)
        goat_soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            resultOne = goat_soup.find_all('a', class_='GridCellLink__Link-sc-2zm517-0 VoJbO')[0]
            endLink = resultOne.get('href')
            full_link = "https://www.goat.com" + endLink
            driver.get(full_link)
            try:
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
                if filter_profit and float(priceProcessed) * 0.905 <= float(product[1]):
                    continue
                else:
                    finalProfit = round(float(priceProcessed) * 0.905 - float(product[1]), 2)
                    profitPercent = round((finalProfit / float(product[1])) * 100, 2)
                    profitable.append((product[2], snkrName, finalProfit, profitPercent, product[1], priceProcessed, str(snkrYear), product[0], goat_url))
            except Exception as e:
                print(f"Failed to retrieve data for {full_link}: {e}")
                continue
        except Exception as e:
            print(e)

    profitable = sorted(profitable, key=lambda x: x[2], reverse=True)
    header = ("SKU", "Name", "Profit ($)", "Profit (%)", "Retail Price ($)", "Resale Price ($)", "Year", "Nike Link", "Goat Link")

    file_exists = os.path.isfile('NikeParserResults.csv')
    if overwrite_csv or not file_exists:
        with open('NikeParserResults.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(profitable)
    else:
        with open('NikeParserResults.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            if os.path.getsize('NikeParserResults.csv') == 0:
                writer.writerow(header)
            writer.writerows(profitable)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        nike_url = ""
        filter_profit = False
        overwrite_csv = False

        for arg in sys.argv[1:]:
            if arg.startswith("http"):
                nike_url = arg
            elif arg == "--filter-profit":
                filter_profit = True
            elif arg == "--overwrite-csv":
                overwrite_csv = True

        if nike_url:
            scrape_sneaker_prices(nike_url, filter_profit, overwrite_csv)
        else:
            print("Please provide a valid URL.")
    else:
        print("Please provide a URL.")
