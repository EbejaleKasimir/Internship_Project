
# E-Commerce Sentiment Analysis for Customer Reviews

This project focuses on analyzing sentiment trends across different product categories on e-commerce platforms and developing a sentiment analysis model to classify reviews.

## Project Objective:
- Analyze sentiment trends across different product categories.
- Develop a sentiment analysis model to classify reviews as positive, negative, and neutral.

## Tasks Covered:
1. Import of Python Libraries
2. Import of Amazon.com data
3. Assessment of data
4. Cleaning of data
5. Exploratory Data Analysis (EDA)
6. Natural Language Processing (NLP) and Sentiment Analysis
7. Sentiment Classification Model Building and Evaluation

## Setup and Usage:
Ensure you have the necessary Python libraries installed as mentioned in the notebook. Run the notebook (`Internship_Project.ipynb`) to execute the project. The dataset was scraped from Amazon.com, and associated scripts (`scraper_script.py` and `data_processing_script.py`) are provided for additional functionalities.

# Amazon Scraper and Data Processing

This project consists of two main Python scripts that scrape product data from Amazon and then process and store the retrieved data in a PostgreSQL database.

## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Description

1. **Scraping Script**: This script utilizes Selenium and BeautifulSoup to scrape product information from Amazon for predefined categories such as Smartphones, Laptops, Video Games, Dresses, Shoes, and Accessories. The scraped data includes:

   **Data Dictionary**

      - **Product_ID:** The unique identifier for the product.
      - **product:** The name and description of the product.
      - **price in dollars:** The price of the product.
      - **star ratings:** The average star rating of the product.
      - **Total Ratings:** The total number of reviews for the product.
      - **url:** The URL of the product’s review page.
      - **category:** The category to which the product belongs.
      - **Customer_i_ID:** The unique identifier for the customer.
      - **Customer_i_Star_Rating:** The star rating given by the customer.
      - **Customer_i_Comment:** The review comment made by the customer.
      - **Customer_i_buying_influence:** A measure of how influential this customer’s review is in terms of influencing other customers’ buying decisions.
      - **For both top positive and critical reviews:**
          - **Review_Cust_ID:** The unique identifier for the customer who wrote the review.
          - **Review_Cust_Name:** The name of the customer who wrote the review.
          - **Review_Cust_Influenced:** A measure of how influential this review is in terms of influencing other customers’ buying decisions.
          - **Review_Cust_Comment:** The content of the review.
          - **Review_Cust_Comment_Title:** The title of the review.
          - **Review_Cust_Date:** The date when the review was posted.
          - **Review_Cust_Star_Rating:** The star rating given by this reviewer.
          - **Top_Positive_Review_Cust_ID:** The unique identifier for the customer who wrote the top positive review.
          - **Top_Positive_Review_Cust_Name:** The name of the customer who wrote the top positive review.
          - **Top_Positive_Review_Cust_Influenced:** A measure of how influential this top positive review is in terms of influencing other customers' buying decisions.
          - **Top_Positive_Review_Cust_Comment:** The content of the top positive review.
          - **Top_Positive_Review_Cust_Comment_Title:** The title of the top positive review.
          - **Top_Positive_Review_Cust_Date:** The date when the top positive review was posted.
          - **Top_Positive_Review_Cust_Star_Rating:** The star rating given by the customer who wrote the top positive review.

2. **Data Processing Script**: This script loads the scraped JSON data into a Pandas DataFrame, cleans, and formats it, ensuring that any missing values are handled appropriately. The processed data is then inserted into a PostgreSQL table, and any inconsistencies in the URLs are resolved. Additionally, the DataFrame is saved to a CSV file for further use.

## Installation

### Prerequisites
- Python 3.x
- PostgreSQL
- Selenium WebDriver
- BeautifulSoup

### Installing Dependencies
```sh
pip install selenium beautifulsoup4 pandas psycopg2-binary word2number webdriver-manager
```

### Database Setup
- Ensure that PostgreSQL is installed and running.
- Create a database and user, and grant the necessary permissions.
- Update the database connection parameters in the script.

### Selenium WebDriver
- The script uses the Edge WebDriver, ensure that it is installed and available in the system PATH.

## Usage

1. **Running the Scraping Script**: 
   ```sh
   python scraper_script.py
   ```
   The script will scrape product data for the predefined categories and save the results in a JSON file named `amazon_data_ext.json`.

2. **Running the Data Processing Script**: 
   ```sh
   python data_processing_script.py
   ```
   This script will read the `amazon_data_ext.json`, process the data, insert it into the PostgreSQL table, and save it to a CSV file named `amazon_data_ext.csv`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is open-source. Feel free to use, modify, and distribute the code as you see fit.

## Collaborators and Contribution:
Feel free to fork this repository and submit pull requests for any enhancements or fixes. All contributions are welcome.

For any issues or queries, raise an issue or contact the repository owner.
