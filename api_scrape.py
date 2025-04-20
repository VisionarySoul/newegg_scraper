import httpx
import json
import time
import random
import csv
from datetime import datetime
from fake_useragent import UserAgent
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
url = "https://www.newegg.com/store/api/PageDeals"

# Create output directories if they don't exist
local_output_dir = "scraped_data"  # Local directory
docker_output_dir = "/app/scraped_data"  # Docker directory

# Create both directories
os.makedirs(local_output_dir, exist_ok=True)
os.makedirs(docker_output_dir, exist_ok=True)
logger.info(f"Output directories created/verified: {local_output_dir} and {docker_output_dir}")

def get_random_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except:
        # Fallback user agents if fake_useragent fails
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15"
        ]
        return random.choice(user_agents)

def get_headers():
    return {
        "User-Agent": get_random_user_agent(),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.newegg.com/",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "DNT": "1",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Origin": "https://www.newegg.com",
        "Host": "www.newegg.com"
    }

def get_random_delay():
    # Increased base delay
    base_delay = random.uniform(5, 10)  # Increased from 2-5 to 5-10 seconds
    # Add occasional longer delays
    if random.random() < 0.2:  # 20% chance of longer delay
        base_delay += random.uniform(5, 10)
    return base_delay

def make_request(session, url, params, retry_count=0, max_retries=3):
    try:
        delay = get_random_delay()
        logger.info(f"Waiting {delay:.2f} seconds before next request...")
        time.sleep(delay)
        
        headers = get_headers()
        response = session.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response
        elif response.status_code == 403 and retry_count < max_retries:
            logger.warning(f"Got 403, retrying ({retry_count + 1}/{max_retries})...")
            time.sleep(random.uniform(10, 15))  # Increased delay on 403
            return make_request(session, url, params, retry_count + 1, max_retries)
        else:
            logger.error(f"Request failed with status code: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error during request: {e}")
        if retry_count < max_retries:
            logger.info(f"Retrying ({retry_count + 1}/{max_retries})...")
            time.sleep(random.uniform(10, 15))
            return make_request(session, url, params, retry_count + 1, max_retries)
        return None

def extract_product_info(item):
    """Get product information from API response"""
    item_cell = item.get("ItemCell", {})
    description_obj = item_cell.get("Description", {})
    review_obj = item_cell.get("Review", {})
    manufacturer_obj = item_cell.get("ItemManufactory", {})

    # Get bullet description and convert to single line if it exists
    bullet_desc = description_obj.get("BulletDescription", "")
    if bullet_desc:
        # Replace multiple spaces and newlines with a single space
        bullet_desc = ' '.join(bullet_desc.split())

    return {
        "title": description_obj.get("ProductName", "") or description_obj.get("ShortTitle", ""),
        "description": description_obj.get("Title", "") or description_obj.get("LineDescription", ""),
        "bullet_description": bullet_desc,
        "price": item_cell.get("FinalPrice", ""),
        "rating": str(review_obj.get("RatingOneDecimal", "") or review_obj.get("Rating", "")),
        "seller": manufacturer_obj.get("Manufactory", "") or "Newegg",
        "product_number": item.get("ProductNumber", "")
    }

# Initialize session with custom transport
transport = httpx.HTTPTransport(retries=3)
client = httpx.Client(transport=transport)

# Initialize counters and lists
products_list = []
item_counter = 0
max_pages = 50
min_products = 500

# Main scraping loop
for page in range(1, max_pages + 1):
    logger.info(f"Requesting page {page}...")
    
    params = {
        "originParams": '{"name":"Newegg-Deals","id":"9447"}',
        "originQuery": '{}',
        "from": "www.newegg.com",
        "index": page
    }
    
    response = make_request(client, url, params)
    if not response:
        break
        
    try:
        products_data = response.json()
        
        if not isinstance(products_data, list):
            logger.error("Invalid response format")
            break
        
        # Process products
        for item in products_data:
            product = extract_product_info(item)
            product["item_counter"] = item_counter + 1
            item_counter += 1
            products_list.append(product)
            
        logger.info(f"Total products scraped so far: {len(products_list)}")
        
        if len(products_list) >= min_products:
            logger.info(f"Reached {min_products} products. Stopping.")
            break
            
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        break

# Save results
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def save_to_file(filename, data, mode='w'):
    """Helper function to save data to both local and Docker directories"""
    try:
        # Save to local directory
        local_path = os.path.join(local_output_dir, os.path.basename(filename))
        with open(local_path, mode, encoding='utf-8') as f:
            if isinstance(data, list):
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                f.write(data)
        logger.info(f"Data saved to local file: {local_path}")
        
        # Save to Docker directory
        docker_path = os.path.join(docker_output_dir, os.path.basename(filename))
        with open(docker_path, mode, encoding='utf-8') as f:
            if isinstance(data, list):
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                f.write(data)
        logger.info(f"Data saved to Docker file: {docker_path}")
    except Exception as e:
        logger.error(f"Error saving file {filename}: {e}")

# Save to CSV
csv_filename = f"newegg_products_{timestamp}.csv"
fields = ["number", "title", "description", "bullet_description", "price", "rating", "seller", "product_number"]

# Prepare CSV data
csv_data = []
csv_data.append(','.join(fields))  # Header
for product in products_list:
    row = [
        f"{product['item_counter']}",
        product["title"],
        product["description"],
        product["bullet_description"],
        product["price"],
        product["rating"],
        product["seller"],
        product["product_number"]
    ]
    csv_data.append(','.join(str(x).replace(',', ';') for x in row))

# Save CSV
save_to_file(csv_filename, '\n'.join(csv_data))

# Save to JSON
json_filename = f"newegg_products_{timestamp}.json"
numbered_products = []
for product in products_list:
    numbered_product = {
        "number": f"{product['item_counter']}",
        "title": product["title"],
        "description": product["description"],
        "bullet_description": product["bullet_description"],
        "price": product["price"],
        "rating": product["rating"] or "N/A",
        "seller": product["seller"],
        "product_number": product["product_number"]
    }
    numbered_products.append(numbered_product)

# Save JSON
save_to_file(json_filename, numbered_products)

# Log summary
logger.info(f"\nScraping Summary:")
logger.info(f"Total products scraped: {len(products_list)}")
logger.info(f"Files generated in both local and Docker directories:")
logger.info(f"- CSV: {csv_filename}")
logger.info(f"- JSON: {json_filename}")