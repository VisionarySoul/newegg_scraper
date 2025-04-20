import httpx
import tls_client
from selectolax.parser import HTMLParser
from urllib.parse import urljoin
import time
import random

def web_scrape(url):
    print(f"\nTrying to scrape URL: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }

    try:
        # Add a small delay before request
        time.sleep(random.uniform(1, 2))

        session = tls_client.Session(
            client_identifier="chrome_120",  # Updated to chrome
            random_tls_extension_order=True
        )
        res = session.get(url, headers=headers)
        print(f"TLS Session Status Code: {res.status_code}")

        if res.status_code == 200:
            html = HTMLParser(res.text)
            return html
        else:
            print(f"Failed to get page. Status code: {res.status_code}")
            return None
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return None


def extract_text(html, selector):
    try:
        return html.css_first(selector).text()
    except AttributeError:
        return None

def parse_products(html):
    products = html.css("div.goods-container")
    item_counter = 0
    products_list = []
    print(f"\nFound {len(products)} products to parse")

    for product in products:
        if item_counter >= 3:  # Stop after 5 products
            break

        # Debug print
        print(f"\nProcessing product {item_counter + 1}")

        name = extract_text(product, "a.goods-title")
        price = extract_text(product, "span.goods-price-value")
        rating = extract_text(product, ".goods-rating")
        seller_name = extract_text(product, ".goods-brand")

        # Debug prints
        print("Found name:", name)
        print("Found price:", price)
        print("Found rating:", rating)
        print("Found seller name:", seller_name)

        product_data = {
            "name": name,
            "price": price,
            "rating": rating,
            "seller_name": seller_name,
            "item_counter": item_counter + 1,
        }
        item_counter += 1
        products_list.append(product_data)
        print("Product data:", product_data)
    return products_list

# def get_product_details(url):
#     html = web_scrape(url)
#     # Get the product title
#     title = html.css_first("h1.product-title")
#     if title:
#         print("\nProduct Name:")
#         print("-" * 50)
#         print(title.text().strip())
#         print("-" * 50)
#     else:
#         print("Could not find product name")

def link_product(html):
    item_counter = 0
    print("\nStarting to search for products...")

    products = html.css("div.goods-container")
    print(f"Found {len(products)} products")

    if len(products) == 0:
        # Try alternative selectors if the first one fails
        print("Trying alternative selectors...")
        products = html.css("div.item-container")
        print(f"Found {len(products)} products with item-container")
        if len(products) == 0:
            products = html.css("div.item-cell")
            print(f"Found {len(products)} products with item-cell")

    for product in products:
        item_counter += 1
        if item_counter >= 3:  # Stop after 2 products
            break
        time.sleep(random.uniform(1, 3))
        print(f"\n--- Product {item_counter} ---")

        # Try multiple selectors for links
        link = product.css_first("a.item-title")
        if not link:
            link = product.css_first("a.goods-title")
        if not link:
            link = product.css_first("a")

        print("Found link element:", link)
        if link:
            print("Link attributes:", link.attributes)
            href = link.attributes.get("href")
            if href:
                product_url = href
                print(f"Product URL: {product_url}")
            else:
                print("No href found in link")
        else:
            print("No link element found")

        # Print the raw HTML of the product container for debugging
        print("\nProduct container HTML:")
        print(product.html[:200] + "..." if len(product.html) > 200 else product.html)

def main():
    url_link = "https://www.newegg.com/Newegg-Deals/EventSaleStore/ID-9447"
    print(f"\nFetching main page: {url_link}")
    html = web_scrape(url_link)
    if html:
        # First get the products data
        products = parse_products(html)
        print("\nProduct parsing complete")

        # Then get the links
        link_product(html)
    else:
        print("Failed to get webpage content")

if __name__ == "__main__":
    main()
# for product in products:
#     for i in product.css_first(".goods-info"):
#         print(i)
#     # product_name =
#     # product_price =
#     # product_rating =