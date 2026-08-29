from apify_client import ApifyClient
import json

# Initialize the ApifyClient with your API token
# Replace 'YOUR_APIFY_API_TOKEN' with your actual token
client = ApifyClient("creds")

def get_reddit_reviews(product_name):
    print(f"Searching Reddit for reviews of: {product_name}...")

    # Prepare the Actor input
    # Depending on the exact scraper version, search queries are usually passed 
    # under "searches" or "searchQuery".
    run_input = {
        "searches": [product_name],     # The product name you are searching for
        "scrapeType": "posts",          # Extract posts matching the product name
        "sort": "relevance",            # Sort by relevance to find the best reviews
        "time": "all",                  # Search across all time
        "maxItems": 50,                 # Limit the number of results to fetch
        "includeComments": True         # (Optional) Fetch comments for deeper sentiment
    }

    # Run the Actor (openclawai/reddit-scraper) and wait for it to finish
    run = client.actor("openclawai/reddit-scraper").call(run_input=run_input)

    print("Scraping completed! Fetching data...")

    # Fetch Actor results from the run's default dataset
    dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    # Save the results to a JSON file
    filename = f"{product_name.replace(' ', '_')}_reddit_reviews.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(dataset_items, f, ensure_ascii=False, indent=4)
        
    print(f"Saved {len(dataset_items)} results to {filename}")

    # Print a quick preview of the top 3 results
    print("\n--- Top 3 Results Preview ---")
    for item in dataset_items[:3]:
        title = item.get("itemTitle") or item.get("title", "No Title")
        url = item.get("url", "")
        print(f"Title: {title}")
        print(f"URL: {url}\n")

if __name__ == "__main__":
    # Just enter the name of the product here
    # product_input = input("Enter the name of the product: ")
    get_reddit_reviews("macbook air m5")