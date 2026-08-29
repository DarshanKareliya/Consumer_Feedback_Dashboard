import requests
from amzpy import AmazonScraper

url = "https://api.apify.com/v2/actors/R8WeJwLuzLZ6g4Bkk/run-sync-get-dataset-items"

headers = {
    "content-type": "application/json",
    "accept": "application/json",
    "authorization": "Bearer env.cresds"
}


def get_amazon_reviews_from_urls(urls):
    # print(f"URLSSSSS:\n {urls}")
    payload = {
        "deduplicateRedirectedAsins": True,
        "filterByRatings": ["allStars"],
        "includeGdprSe100tive": False,
        "maxReviews": 10,
        "productUrls": [{"url": url} for url in urls],
        "reviewsAlwaysSaveCategoryData": False,
        "reviewsUseProductVariantFilter": False,
        "scrapeProductDetails": False,
        "sort": "recent"
    }
    reviews = requests.request("post", url, json=payload, headers=headers).json()
    print(reviews)
    
    return [review["reviewDescription"] for review in reviews]


def get_amazon_urls_from_product_name(product_name):
    print(f"--- Fetching Amazon Product urls for {product_name} ---")
    try:
        search_scraper = AmazonScraper(country_code="com")
        products = search_scraper.search_products(
            query=product_name, max_pages=2)
        print(
            f"Found {len(products)} products for '{product_name}' on Amazon.")
        # print(f"Products: {products}")

        if not products:
            return "No products found."
        return [product["url"] for product in products]
    except Exception as e:
        return f"Amazon Scraper Error: Could not find product urls for product: {product_name}. Message: {e}"


def get_amazon_reviews(product_name):
    print(f"--- Fetching Amazon Reviews for {product_name} ---")
    try:
        urls = get_amazon_urls_from_product_name(product_name)
        if not urls:
            return "No urls found."
        product_reviews = get_amazon_reviews_from_urls(urls)
        if not product_reviews:
            return "No Product Reviews found."
        return product_reviews
    except Exception as e:
        return f"Amazon Scraper Error: {e}"


# print(get_amazon_reviews("Macbook air m5"))
