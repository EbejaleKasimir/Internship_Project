import time
import json
import random
import html
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import traceback
import logging
import re  # Make sure to include this import
from word2number import w2n
from datetime import datetime
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def process_review_count(text):
    text = text.strip().replace(',', '')
    if 'K+' in text:
        return str(int(float(text.replace('(', '').replace(')', '').replace('K+', '').strip()) * 1000))
    return text

def setup_driver():
    options = webdriver.EdgeOptions()
    options.add_argument('--no-sandbox')
    try:
        driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
    except Exception as e:
        print(e)
        raise Exception("Failed to install Edge Chromium driver.")
    return driver



def scrape_extra_parameters(url: str, driver: webdriver.Edge) -> dict:
    try:
        driver.get(url)
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-hook='review']")))

        except TimeoutException:
            print(f"TimeoutException: Could not find reviews for {url}")
            return {}
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract the general reviews
        reviews_tags = soup.find_all('div', attrs={'data-hook': 'review'})

        result = {}
        for i, review_tag in enumerate(reviews_tags[:5]):
            result[f'Customer_{i + 1}_ID'] = review_tag.attrs.get('id', 'None')
            
            # Extract the Star Rating
            star_rating_tag = review_tag.select_one('i[data-hook="review-star-rating"] span.a-icon-alt')
            star_rating = float(star_rating_tag.text.split()[0]) if star_rating_tag else 0.0
            result[f'Customer_{i+1}_Star_Rating'] = star_rating
            
            # Extract the Comment Title
            comment_title_tag = review_tag.select_one('a[data-hook="review-title"]')
            # Inside the for loop, after extracting the comment title:
            if comment_title_tag:
                actual_comment_title = comment_title_tag.text.strip()
            else:
                # Handle alternate structure
                comment_title_tag = review_tag.select_one('span.cr-original-review-content')
                actual_comment_title = comment_title_tag.text.strip() if comment_title_tag else 'NaN'

            # Remove the pattern "k out of 5 stars\n" from the comment
            actual_comment_title = re.sub(r'\d+(\.\d+)? out of 5 stars\n', '', actual_comment_title)

            result[f'Customer_{i+1}_Comment'] = actual_comment_title

            # Extract the Number of people who found the review helpful
            helpful_vote_tag = review_tag.select_one('span[data-hook="helpful-vote-statement"]')
            helpful_count = w2n.word_to_num(helpful_vote_tag.text.split()[0]) if helpful_vote_tag else 0
            result[f'Customer_{i+1}_buying_influence'] = helpful_count
        

        # Extract Top Positive and Critical Reviews (Moved outside of the above loop)
        Parent_review_tags = soup.select('div[id^="viewpoint-"]')
        if len(Parent_review_tags) > 0: 
            ts = 'positive-review'
            result.update(extract_specific_review(Parent_review_tags[0], 'Top_Positive', ts, soup, url))

        else:
            result.update(set_default_values('Top_Positive'))
            
        if len(Parent_review_tags) > 1: 
            ts = 'critical-review.a-span-last'
            result.update(extract_specific_review(Parent_review_tags[1], 'Critical', ts, soup, url))

        else:
            result.update(set_default_values('Critical'))
            
        return result
    except Exception as e:
        print(f"Error scraping extra parameters: {e}")
        traceback.print_exc()
        return {}

def extract_specific_review(review_tag, review_type, ts, soup, url):
    specific_result = {}
    
    # Extracting ID
    review_id = review_tag.get('id', 'None').replace('viewpoint-', '')
    specific_result[f'{review_type}_Review_Cust_ID'] = review_id

    # # Extract Customer Name and Influenced
 
     # Corrected Extraction for Customer Name
    customer_name_selector = 'div.a-profile-content span.a-profile-name'
    specific_result[f'{review_type}_Review_Cust_Name'] = review_tag.select_one(customer_name_selector).text if review_tag.select_one(customer_name_selector) else 'None'

    # Corrected Selector
    influenced_selector = f'div.a-column.a-span6.view-point-review.{ts} div.a-row.a-spacing-top-small span.a-size-small.a-color-tertiary span.review-votes'
    influenced_element = soup.select_one(influenced_selector)

    if influenced_element:
        # Directly extract the text from the found element
        helpful_text = influenced_element.text.strip()
        print("Helpful Text:", helpful_text)  # Debugging line
        
        # Check if the text starts with a digit and extract the first contiguous digit sequence
        match = re.match(r'\d+', helpful_text)
        if match:
            helpful_count = int(match.group())
        else:
            # If the text doesn't start with a digit, try converting the first word to a number
            helpful_count = w2n.word_to_num(helpful_text.split()[0])
    else:
        print(f"Tag not found in {url}")  # Debugging line
        helpful_count = 0

    specific_result[f'{review_type}_Review_Cust_Influenced'] = helpful_count

    
 
  # # customer_name_tags = review_tag.select('span.a-profile-name')
    # customer_name_tags = review_tag.select('div.a-expander-content.a-expander-partial-collapse-content div.a-profile-content')
    # specific_result[f'{review_type}_Review_Cust_Name'] = customer_name_tags[1].text if len(customer_name_tags) > 1 else 'None'
    
    # Extract Customer Review Comment
    review_comment_tag = review_tag.find('div', class_='a-row a-spacing-top-mini')
    specific_result[f'{review_type}_Review_Cust_Comment'] = review_comment_tag.text.strip() if review_comment_tag else 'None'
    
    # Extract Customer Review Title
    review_title_tag = review_tag.select_one('span[data-hook="review-title"]')
    specific_result[f'{review_type}_Review_Cust_Comment_Title'] = review_title_tag.text if review_title_tag else 'None'
    
    # Extract the post time
    review_tags_date = review_tag.select('div.a-expander-content.a-expander-partial-collapse-content span.a-size-base.a-color-secondary.review-date')
    if review_tags_date:
        post_time_text = review_tags_date[0].text.strip()
        match = re.search(r'on (.+)$', post_time_text)
        if match:
            date_string = match.group(1)
            try:
                post_date = datetime.strptime(date_string, '%B %d, %Y')
                specific_result[f'{review_type}_Review_Cust_Date'] = post_date.isoformat()                            
            except ValueError as ve:
                print(f"Error parsing date string {date_string}: {ve}")
                specific_result[f'{review_type}_Review_Cust_Date'] = '-'
        else:
            print("Date not found in text:", post_time_text)
            specific_result[f'{review_type}_Review_Cust_Date'] = '-'
    else:
        print("Date tag not found")
        specific_result[f'{review_type}_Review_Cust_Date'] = None
    
    
    # Extract the Star Rating
    review_star_rating_tag = review_tag.select_one('i[data-hook="review-star-rating-view-point"] span.a-icon-alt')
    star_rating = float(review_star_rating_tag.text.split()[0]) if review_star_rating_tag else 0.0
    specific_result[f'{review_type}_Review_Cust_Star_Rating'] = star_rating
    
    return specific_result

def set_default_values(review_type):
    default_values = {
        f'{review_type}_Review_Cust_ID': 'None',
        f'{review_type}_Review_Cust_Name': 'None',
        f'{review_type}_Review_Cust_Comment': 'None',
        f'{review_type}_Review_Cust_Comment_Title': 'None',
        f'{review_type}_Review_Cust_Influenced': 0,
        f'{review_type}_Review_Cust_Star_Rating': 0.0,
        f'{review_type}_Review_Cust_Date': None,
    }
    return default_values

    #     return result
    # except Exception as e:
    #     print(f"Error scraping extra parameters for {url}: {e}")
    #     traceback.print_exc()
    # return {}

def scrape_amazon(categories):
 
    driver = setup_driver()
    all_products = []
    seen_products = set()

    for category, base_url in categories.items():
        products = []

        for page in range(1, 2):
            url = f"{base_url}&page={page}"

            try:
                driver.get(url)
                WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#search > div.s-desktop-width-max.s-desktop-content.s-wide-grid-style-t1.s-opposite-dir.s-wide-grid-style.sg-row > div.sg-col-20-of-24.s-matching-dir.sg-col-16-of-20.sg-col.sg-col-8-of-12.sg-col-12-of-16 > div > span.rush-component.s-latency-cf-section > div.s-main-slot.s-result-list.s-search-results.sg-row > div:nth-child(1)")))
            except TimeoutException:
                print(f"Timed out waiting for elements on page {page} of category {category}.")
                continue

            time.sleep(random.uniform(3.0, 6.0))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find all products using the given CSS selector
            products_tags = soup.select("#search > div.s-desktop-width-max.s-desktop-content.s-wide-grid-style-t1.s-opposite-dir.s-wide-grid-style.sg-row > div.sg-col-20-of-24.s-matching-dir.sg-col-16-of-20.sg-col.sg-col-8-of-12.sg-col-12-of-16 > div > span.rush-component.s-latency-cf-section > div.s-main-slot.s-result-list.s-search-results.sg-row > div")

            products_list = []  # Use a different name for the list of product_dict dictionaries

            for product in products_tags:
                product_dict = {}
                product_dict['Product_ID'] = product.attrs.get('data-asin', None)

                # Try to find item_name with the general class
                item_name = product.find('span', class_='a-text-normal')

                # If not found, try the first specific class
                if item_name is None:
                    item_name = product.find('span', class_='a-size-base-plus a-color-base a-text-normal')

                # If still not found, try the second specific class
                if item_name is None:
                    item_name = product.find('span', class_='a-size-medium a-color-base a-text-normal')

                # If item_name is found with any class, extract the text
                if item_name:
                    product_dict['product'] = item_name.text.strip()
                else:
                    print(f"Failed to scrape item name in {url}")
                    product_dict['product'] = "Unknown"
                product_price = product.find('span', class_='a-offscreen')
                if product_price:
                    product_price = product_price.text.strip().replace("$", "").replace(",", "").strip()
                    product_dict['price'] = product_price

                rating_spans = product.find_all('span', attrs={"aria-label": True})
                for rating_span in rating_spans:
                    aria_label_value = rating_span.attrs["aria-label"]
                    if "stars" in aria_label_value:
                        product_dict['ratings'] = aria_label_value.split(" ")[0]
                    else:
                        if 'K+' in aria_label_value:
                            product_dict['review_responders'] = aria_label_value
                        else:
                            try:
                                int_value = int(aria_label_value)
                                product_dict['review_responders'] = aria_label_value
                            except ValueError:
                                pass

                item_reviews = product.find('span', class_='a-size-base s-underline-text')
                if item_reviews:
                    try:
                        reviews_text = item_reviews.text.strip()
                        reviews_count = process_review_count(reviews_text)
                        product_dict['reviews'] = reviews_count
                        logging.info(f"Successfully scraped total {product_dict['reviews']} rating for product {product_dict.get('Product_ID', 'Unknown ID')}")
                    except Exception as e:
                        logging.error(f"Error processing review count for product {product_dict.get('Product_ID', 'Unknown ID')}: {e}")
                else:
                    logging.warning(f"Failed to scrape total rating for product {product_dict.get('Product_ID', 'Unknown ID')}")

            

                # Extract ASIN
                product_dict['Product_ID'] = product.attrs.get('data-asin', None)

                # Construct the review URL using ASIN
                if product_dict['Product_ID']:
                    asin = product_dict['Product_ID']
                    product_dict['url'] = f"https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_dp_d_show_all_top?ie=UTF8&reviewerType=all_reviews"
                    
                else:
                    product_dict['url'] = "None"


                product_dict['category'] = category

                if 'Product_ID' in product_dict and product_dict['Product_ID']:
                # Create a unique identifier for the product
                    identifier = product_dict['Product_ID']

                    if identifier not in seen_products:
                        seen_products.add(identifier) #
                        if product_dict.get('url'):
                            extra_params = scrape_extra_parameters(product_dict['url'], driver)
                            product_dict.update(extra_params)
                            products_list.append(product_dict)

                        all_products.extend(products_list)
    driver.quit()
    return json.dumps(all_products)


if __name__ == '__main__':
    categories = {
        'Smartphones': 'https://www.amazon.com/s?k=smartphone&ref=nb_sb_noss',
        'Laptops': 'https://www.amazon.com/s?k=Laptops&ref=nb_sb_noss',
        'video_games': 'https://www.amazon.com/s?k=video_games&ref=nb_sb_noss',
        'Dresses':'https://www.amazon.com/s?k=Dresses&ref=nb_sb_noss',
        'Shoes':'https://www.amazon.com/s?k=Shoes&ref=nb_sb_noss',
        'Accessories':'https://www.amazon.com/s?k=accessories+for+clothes&ref=nb_sb_noss',
    }

    all_products = []
    try:
        all_products = json.loads(scrape_amazon(categories))
    except Exception as e:
        print(f"Error occurred during scraping: {e}")
    finally:
        with open('amazon_data_ext.json', 'w') as file:
            json.dump(all_products, file)
