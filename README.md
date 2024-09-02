# Sneaker Resale Predictor

## Overview
This program consists of two main components: a sneaker pricing web scraper (`NikeParser.py`/`GoatParser.py`) and a machine 
learning model to predict sneaker resale (`NikeGoatML.py`/`PredictResale.py`). The web scraper collects sneaker pricing information 
from the Nike website and compares it with prices on the GOAT sneaker reselling website. The ML portion uses the resulting data 
and the scikit-learn library to predict the resale price of a shoe based on its name, release year, and retail price. This is done using
the Random Forest algorithm.

**The most practically useful part of this project is the ability to filter sneakers by profitability.
Any shoe that has a resale price greater than its retail minus the cost of selling fees on GOAT will be deemed profitable.
If you choose to filter by this metric, you can easily find shoes that can be resold for profit.**


## Requirements
- Python 3.7+

- pip 

- ChromeDriver (for Selenium)
## Installation
1. Clone the repository or download the source code files.
2. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure you have a compatible WebDriver for Selenium. Make sure it matches the version of your Chrome browser.

## Usage

### Running the Web Scraper (DEMO)
![](DemoGIFS/ScrapingDemo.gif)
The web scraper (`NikeParser.py`) takes a Nike or GOAT product page URL as an argument, scrapes the page for sneaker details, and stores info on the sneaker and resale price based on the GOAT website. The results are saved to a CSV file.

### Running the GUI
The GUI (`SneakerGUI.py`) allows users to input a URL, run the scraper, and view the results.

#### Command Line
```bash
python SneakerGUI.py
```

### Using the GUI
1. Enter a Nike or GOAT URL in the text box.
2. Check boxes if you want to filter the results to be only profitable to resell, or if you want to overwrite the current CSV file results. 
3. Click "Run Parser" to execute the scraper with the provided URL.
4. Click on column headers to sort the data.
5. Click on any cell to copy its content to the clipboard.

### Sample Input
The Nike Best Selling Shoes page: https://www.nike.com/w/best-shoes-76m50zy7ok

Or the GOAT Nike brand page: https://www.goat.com/brand/nike?web_groups=sneakers


## CSV Output
The results are saved in `NikeParserResults.csv` with the following columns:

SKU, Profit ($), Profit (%), Retail Price ($), Resale Price ($), Nike Link, Goat Link


## Training/Using Machine Learning Model (DEMO)
![](DemoGIFS/MLDemo.gif)

### GUI Instructions
1. Switch to the ML model tab
2. Browse the project directory for a csv file to train the model on
**Included files: NikeParserResults.csv will have any data you scraped, MLTrainingData.csv is a dataset with around 2,000 entries I made that produces a relatively low MSE (~28).
3. Once a file is selected, click train model and you will see the accuracy statistics displayed. 
4. To make predictions for a sneaker's resale value, simply enter its name/retail price/year and click the button to get an estimation of its resale.




## Code Structure

### NikeParser.py
1. **URL Input**: Reads the URL from command-line arguments.
2. **Web Scraping**:
   - Uses `selenium` to open the Nike URL and scroll through the page to load all products.
   - Parses the page content with `BeautifulSoup` to extract product links.
   - Visits each product page to get price and SKU information.
3. **Price Comparison**:
   - Searches for each SKU on the GOAT website.
   - Compares retail and resale prices to calculate potential profit.
4. **CSV Output**: Writes the results to a CSV file.

### GoatParser.py
Same general steps as Nike parser, but it takes results from GOAT product page rather than Nike to start. 

### NikeGoatML.py
1. **Features/Data**: Takes in CSV file and extracts name, retail price, and year from each row as features to predict resale. Data is cleaned by removing duplicates and handling missing/incorrect values
2. **Model**: Data is split into 80% training data, 20% test data, and the random forest algorithm is used to create the model, which is saved to the project directory. Random Forest was used due to improved results over linear regression, as the features did not have a very linear correlation to the resale price. 
3. **Output**: MAE, MSE, RMSE, and R-squared are all calculated and displayed.
4. **Predictions:**: File makes call to PredictResale.py, which uses the given information and the model to create and return a prediction for a shoe's resale price. 


## Notes
- Ensure the Nike URL provided points to a valid product listing page with sneaker tiles.
- The scraper relies on the structure of the Nike and GOAT websites; changes to these websites may require updates to the scraper.
- Machine learning predictions are not always very practically useful (lol)
