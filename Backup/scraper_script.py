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

from selenium.common.exceptions import TimeoutException
from word2number import w2n
import traceback

def scrape_extra_parameters(url: str, driver: webdriver.Edge) -> dict:
    try:
        driver.get(url)
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-hook='review']")))
        except TimeoutException:
            print(f"TimeoutException: Could not find reviews for {url}")
            return {}
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        reviews_tags = soup.find_all('div', attrs={'data-hook': 'review'})

        result = {}
        for i, review_tag in enumerate(reviews_tags[:5]):
            result[f'Customer_{i + 1}_ID'] = review_tag.attrs.get('id', 'NaN')
            
            # Extract the Star Rating
            star_rating_tag = review_tag.select_one('i[data-hook="review-star-rating"] span.a-icon-alt')
            star_rating = float(star_rating_tag.text.split()[0]) if star_rating_tag else 0.0
            result[f'Customer_{i+1}_Star_Rating'] = star_rating
            
            # Extract the Comment Title
            comment_title_tag = review_tag.select_one('a[data-hook="review-title"]')
            if comment_title_tag:
                actual_comment_title = comment_title_tag.text.strip()
            else:
                # Handle alternate structure
                comment_title_tag = review_tag.select_one('span.cr-original-review-content')
                actual_comment_title = comment_title_tag.text.strip() if comment_title_tag else 'NaN'
            
            result[f'Customer_{i+1}_Comment'] = actual_comment_title

            # Extract the Number of people who found the review helpful
            helpful_vote_tag = review_tag.select_one('span[data-hook="helpful-vote-statement"]')
            helpful_count = w2n.word_to_num(helpful_vote_tag.text.split()[0]) if helpful_vote_tag else 0
            result[f'Customer_{i+1}_buying_influence'] = helpful_count

        return result
    except Exception as e:
        print(f"Error scraping extra parameters for {url}: {e}")
        traceback.print_exc()
    return {}


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
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-asin]")))
            except TimeoutException:
                print(f"Timed out waiting for elements on page {page} of category {category}.")
                continue

            time.sleep(random.uniform(3.0, 6.0))
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            for product in soup.find_all('div', attrs={"data-asin": True}):
                product_dict = {}

                product_dict['Product_ID'] = product.attrs.get('data-asin', None)

                item_name = product.find('span', class_='a-text-normal')
                if item_name:
                    product_dict['product'] = item_name.text.strip()

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
                    reviews_text = item_reviews.text.strip()
                    reviews_count = process_review_count(reviews_text)
                    product_dict['reviews'] = reviews_count


                # Extract ASIN
                product_dict['Product_ID'] = product.attrs.get('data-asin', None)

                # Construct the review URL using ASIN
                if product_dict['Product_ID']:
                    asin = product_dict['Product_ID']
                    product_dict['url'] = f"https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_dp_d_show_all_top?ie=UTF8&reviewerType=all_reviews"
                    
                else:
                    product_dict['url'] = None


                product_dict['category'] = category

                if 'Product_ID' in product_dict and product_dict['Product_ID']:
                # Create a unique identifier for the product
                    identifier = product_dict['Product_ID']

                    if identifier not in seen_products:
                        seen_products.add(identifier) #
                        if product_dict.get('url'):
                            extra_params = scrape_extra_parameters(product_dict['url'], driver)
                            product_dict.update(extra_params)
                        products.append(product_dict) #
            all_products.extend(products)
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
