import os
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import csv
import sys

# File uses BeautifulSoup and selenium to obtain and compare
# sneaker pricing data from Nike and GOAT.

# Link to target Nike page
# Example input: https://www.nike.com/w/best-shoes-76m50zy7ok (Trending shoes page)
nike_url = ""
filter_profit = False
overwrite_csv = False

# Getting URL from arguments
if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith("http"):
                nike_url = arg
            elif arg == "--filter-profit":
                filter_profit = True
            elif arg == "--overwrite-csv":
                overwrite_csv = True
    else:
        print("Please provide a URL")

headers = {  # Header used for requests
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.google.com/',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Initialize the webdriver
driver = webdriver.Chrome()

# Open the Nike URL
driver.get(nike_url)

# Scroll down the page to load more products
scroll_pause_time = 1
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Wait to load the page
    time.sleep(scroll_pause_time)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Once the scrolling is done, parse the page content with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Extract product links
product_links = soup.select('a.product-card__link-overlay')
links = [l.get("href") for l in product_links]

# driver.quit()

# Visit each product page to get its price + SKU
product_prices = []

for link in links:
    # Construct the full URL
    full_link = link

    # Send a GET request to the product page
    response = requests.get(full_link, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the price and SKU
        price_element = soup.select_one('.product-price')
        sku_element = soup.select_one('.description-preview__style-color')
        if price_element and sku_element:
            price = price_element.get_text()
            sku = sku_element.get_text()
            product_prices.append((full_link, price[1:], sku[7:]))  # Add them to list
        else:
            product_prices.append((full_link, "ERROR", "ERROR"))
    else:
        product_prices.append((full_link, "ERROR", "ERROR"))

profitable = []  # List containing information of all profitable shoes
print(len(product_prices))
for product in product_prices:
    goat_url = f'https://www.goat.com/search?query={product[2]}'  # visit their GOAT page
    goat_response = requests.get(goat_url, headers=headers)
    driver.get(goat_url)

    # goat_soup = BeautifulSoup(goat_response.text, 'html.parser')
    goat_soup= BeautifulSoup(driver.page_source, 'html.parser')
    try:
        # Retrieve first products link
        resultOne = goat_soup.find_all('a', class_='GridCellLink__Link-sc-2zm517-0 VoJbO')[0]
        endLink = resultOne.get('href')
        # Retrieve first products price
        priceEl = goat_soup.find_all('span', class_='LocalizedCurrency__Amount-sc-yoa0om-0 jDDuev')[0]
        priceProcessed = priceEl.get_text()[1:]
        # Get sneaker name
        snkrNamePre = goat_soup.find_all('div', class_='GridCellProductInfo__Name-sc-17lfnu8-3 iPovsV')[0]
        snkrName = snkrNamePre.get_text()
        # Get sneaker release year
        snkrYearPre = goat_soup.find_all('div', class_='GridCellProductInfo__Year-sc-17lfnu8-2 hyAqZs')[0]
        snkrYear = snkrYearPre.get_text()
        if len(snkrYear) > 4:
            snkrYear = "2024"

        print(priceProcessed)
        print(endLink)
        if filter_profit and float(priceProcessed) * 0.905 <= float(product[1]):
            continue
        else:
            finalProfit = (round(float(priceProcessed) * 0.905 - float(product[1]), 2))
            profitPercent = round(float(finalProfit / float(product[1])), 2) * 100
            profitPercent = round(profitPercent, 2)
            finalProfit = format(finalProfit, '.2f')
            print(
                "SKU: " + product[2] + "\n Name: "  + snkrName + "\nProfit: $" + str(finalProfit) + "\nProfit " + str(profitPercent) + "%" +
                "\nRetail: $" + product[1] + "\nResale: $" + priceProcessed + "\n Year: " + snkrYear + "\nNike Link: " + product[0] +
                "\nGOAT Link: " + goat_url + "\n")
            profitable.append(
                (product[2], snkrName, float(finalProfit), profitPercent, product[1], priceProcessed, str(snkrYear), product[0],
                 goat_url))
            # Added information to list of profitable shoes

    except Exception as e:
        print(e)


profitable = sorted(profitable, key=lambda x: x[2], reverse=True)
print(len(profitable))
# Sort information based on second column ($ amount of profit)
# Insert header for CSV file
profitable.insert(0,
                  ("SKU", "Name", "Profit ($)", "Profit (%)", "Retail Price ($)", "Resale Price ($)", "Year",
                   "Nike Link", "Goat Link"))

# Write list to CSV file and save
file_exists = os.path.isfile('NikeParserResults.csv')

if overwrite_csv or not file_exists:
    with open('NikeParserResults.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(profitable)
else:
    with open('NikeParserResults.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if file_exists and os.path.getsize('NikeParserResults.csv') == 0:
            writer.writerows(profitable)
