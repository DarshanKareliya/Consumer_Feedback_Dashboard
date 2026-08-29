from youtube_search import YoutubeSearch

from itertools import islice
from youtube_comment_downloader import *


def get_youtube_comments_from_urls(urls):
    comments = []

    for url in urls:

        downloader = YoutubeCommentDownloader()
        comments_list = downloader.get_comments_from_url(
            f'https://www.youtube.com{url}', sort_by=SORT_BY_POPULAR)

        count = 0
        for comment in comments_list:
            comments.append(comment)
            count += 1

        print(f"Fetched {count} comments.")

    print(f"Fetched {len(comments)} comments from youtube.")
    
    return [comment["text"] for comment in comments]


def get_youtube_urls_from_product_name(product_name):
    print(f"--- Fetching Youtube Video urls for {product_name} ---")
    try:
        search_results = YoutubeSearch(product_name, max_results=3)
        print(
            f"Found {len(search_results.videos)} vidoes for '{product_name}' on Youtube.")

        if not search_results:
            return "No Videos Found."

        return [video["url_suffix"] for video in search_results.videos]

    except Exception as e:
        return f"Youtube Scraper Error: Could not find video urls for product: {product_name}. Message: {e}"


def get_youtube_comments(product_name):
    print(f"--- Fetching Youtube Reviews for {product_name} ---")
    try:
        urls = get_youtube_urls_from_product_name(
            product_name)
        print("URLSSSSSSSS")
        print(urls)
        comments = get_youtube_comments_from_urls(urls)
        return comments
    except Exception as e:
        return f"Youtube Scraper Error: {e}"


# print(get_youtube_comments("Macbook air m5"))
