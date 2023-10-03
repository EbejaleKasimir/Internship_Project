import pandas as pd
import psycopg2
import numpy as np
import re

# Load the JSON data into a pandas DataFrame
df = pd.read_json('amazon_data_ext.json')

# Ensure the columns for the additional information from the five customers exist
for i in range(1, 6):
    df[f'Customer_{i}_ID'] = df[f'Customer_{i}_ID'].fillna('NaN')
    df[f'Customer_{i}_Star_Rating'] = df[f'Customer_{i}_Star_Rating'].fillna(0)
    df[f'Customer_{i}_Comment'] = df[f'Customer_{i}_Comment'].fillna('NaN')
    df[f'Customer_{i}_buying_influence'] = df[f'Customer_{i}_buying_influence'].fillna(0)

# Handle other columns similarly
df['price'].fillna(0, inplace=True)
df['ratings'].fillna(0, inplace=True)
df['reviews'] = df['reviews'].str.replace('(', '').str.replace(')', '')
df['reviews'].fillna(0, inplace=True)

# Check the data type of the reviews column
if pd.api.types.is_string_dtype(df['reviews']):
    df['reviews'] = df['reviews'].str.replace('(', '').str.replace(')', '')

# Convert reviews to integer
try:
    df['reviews'] = df['reviews'].astype(int)
except ValueError:
    df['reviews'] = 0

df['url'].fillna('Unknown', inplace=True)
df['category'].fillna('', inplace=True)
df['product'].fillna('', inplace=True)
df['monthly_sales'] = df.get('monthly_sales', 0)  # Adding handling for 'monthly_sales'

# Set negative reviews to 0
df.loc[df['reviews'] < 0, 'reviews'] = 0

# Function to extract the second occurrence of the URL
def extract_second_url(url):
    prefix = "https://www.amazon.comhttps://"
    if url.startswith(prefix):
        matches = re.findall(r'https://www\.amazon\.com/', url[len(prefix):])
        if len(matches) >= 1:
            second_occurrence_index = url.rfind(matches[0])
            return url[second_occurrence_index:]
    return url

# Apply the function to the 'url' column
df['url'] = df['url'].apply(extract_second_url)

# Remove any duplicates that may have been created due to URL changes
df = df.drop_duplicates(subset=['product', 'price', 'ratings', 'reviews', 'category'], keep='first')

# Replace empty product names with NaN and drop those rows
df['product'].replace('', pd.NA, inplace=True)
df.dropna(subset=['product'], inplace=True)

# Drop the 'review_responders' column if it exists
if 'review_responders' in df.columns:
    df.drop('review_responders', axis=1, inplace=True)
print(len(df))
# Drop all items with review having zero values
df.drop(df.index[df['reviews'] == 0], inplace=True)
print(len(df))

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="demopass",
    client_encoding='utf8'
)

cur = conn.cursor()

# Create a table in the PostgreSQL database with additional columns for the five customers
create_table_query = """
DROP TABLE IF EXISTS amazon_data_ext;
CREATE TABLE IF NOT EXISTS amazon_data_ext (
    product_id TEXT NOT NULL,
    product TEXT NOT NULL,
    price_dollars NUMERIC NOT NULL,
    -- monthly_sales NUMERIC,
    ratings NUMERIC NOT NULL,
    reviews_qty INTEGER NOT NULL,
    category TEXT NOT NULL,
    url TEXT NOT NULL,
    """ + ",\n    ".join([f"Customer_{i}_ID TEXT, Customer_{i}_Star_Rating INTEGER, Customer_{i}_Comment TEXT, Customer_{i}_buying_influence INTEGER" for i in range(1, 6)]) + """
)
"""
cur.execute(create_table_query)
conn.commit()

def clean_format_data(row):
    # Convert the ratings value to a float
    ratings = float(row['ratings'])
    
    # Convert the product name, reviews, and category to strings and then adapt for SQL insertion
    product = psycopg2.extensions.adapt(str(row['product']).encode('utf-8', 'replace')).getquoted().decode('utf-8')[1:-1]
    category = psycopg2.extensions.adapt(row['category'].encode('utf-8', 'replace')).getquoted().decode('utf-8')[1:-1]
    
    # Convert price to float, if not possible set to 0
    try:
        price = float(row['price'])
    except ValueError:
        price = 0

    url = row['url']
    product_id = row['Product_ID']
    reviews = row['reviews']  # Already cleaned and converted to int
    monthly_sales = float(row['monthly_sales'])  # Handling for 'monthly_sales'

    
    # Handle additional customer information
    customer_data = []
    for i in range(1, 6):
        customer_id = row[f'Customer_{i}_ID']
        star_rating = row[f'Customer_{i}_Star_Rating']
        comment = psycopg2.extensions.adapt(str(row[f'Customer_{i}_Comment']).encode('utf-8', 'replace')).getquoted().decode('utf-8')[1:-1]
        buying_influence = row[f'Customer_{i}_buying_influence']
        customer_data.extend([customer_id, star_rating, comment, buying_influence])
    
    return product_id, product, price, ratings, reviews, category, url,*customer_data

# Modify the INSERT query to include additional columns for the five customers
insert_query = """
INSERT INTO amazon_data_ext (
    product_id, product, price_dollars, ratings, reviews_qty, category, url,
    """ + ", ".join([f"Customer_{i}_ID, Customer_{i}_Star_Rating, Customer_{i}_Comment, Customer_{i}_buying_influence" for i in range(1, 6)]) + """
) VALUES (%s, %s, %s, %s, %s, %s, %s, """ + ", ".join(["%s"] * 20) + ")"

# Insert the data from the pandas DataFrame into the PostgreSQL table
for index, row in df.iterrows():
    try:
        product_id, product, price,ratings, reviews, category, url, *customer_data = clean_format_data(row)
        cur.execute(insert_query, (product_id, product, price,ratings, reviews, category, url, *customer_data))
    except Exception as e:
        print(f"Error inserting row: {e}")

conn.commit()
cur.close()
conn.close()

# Save the DataFrame to a CSV file
df.to_csv('amazon_data_ext.csv', index=False)
