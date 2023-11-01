
# E-Commerce Sentiment Analysis for Customer Reviews

This project focuses on analyzing sentiment trends across different product categories on e-commerce platforms and developing a sentiment analysis model to classify reviews.

## Project Objective:
- Analyze sentiment trends across different product categories.
- Develop a sentiment analysis model to classify reviews as positive, negative, and neutral.

## Data Dictionary:

| Field Name                | Description |
|---------------------------|-------------|
| Product_ID                | The unique identifier for the product. |
| product                   | The name and description of the product. |
| price_dollars             | The price of the product in USD. |
| star_ratings              | The average star rating of the product. |
| total_ratings             | The total number of reviews for the product. |
| url                       | The URL link to the product page on Amazon. |
| Customer_i_ID             | The unique identifier for each customer review (where `i` ranges from 1 to 5 for the top 5 reviews). |
| Customer_i_Star_Rating    | The star rating given by the customer for the review. |
| Customer_i_Comment        | The comment or feedback provided by the customer. |
| Customer_i_buying_influence | The influence of the review on buying decisions. |
| Customer_i_Date           | The date the review was posted. |
| Customer_i_Unique_ID      | A unique identifier combining the `Product_ID` and `Customer_i_ID`. |

(Note: If there are more fields in the actual dataset, they should be added to the Data Dictionary accordingly.)

## Tasks Covered:
1. Import of Python Libraries
2. Import of Amazon.com data
3. Assessment of data
4. Cleaning of data
5. Exploratory Data Analysis (EDA)
6. Natural Language Processing (NLP) and Sentiment Analysis
7. Sentiment Classification Model Building and Evaluation

## Setup and Usage:
Ensure you have the necessary Python libraries installed as mentioned in the notebooks. Run the main notebook (`Internship_Project.ipynb`) to execute the project. Additionally, you can process the `amazon_data_ext.csv` file to format customer-related data using the `create_new_csv.ipynb` notebook. 

The dataset was scraped from Amazon.com. Associated scripts (`scraper_script.py` and `data_processing_script.py`) are provided for additional functionalities. 

## Contributing:

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License:

This project is open-source. Feel free to use, modify, and distribute the code as you see fit.

## Collaborators and Contribution:
Feel free to fork this repository and submit pull requests for any enhancements or fixes. All contributions are welcome.

For any issues or queries, raise an issue or contact the repository owner.
