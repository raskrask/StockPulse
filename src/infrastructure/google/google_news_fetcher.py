import feedparser
import urllib.parse
from datetime import datetime
import time

def fetch_google_news_rss(query: str, max_results: int = 6):
    """
    Fetches news from Google News RSS for a specific query.
    
    Args:
        query (str): The search query (e.g., stock name or code).
        max_results (int): Maximum number of news items to return.
        
    Returns:
        list[dict]: A list of news items, each containing title, link, published, summary, source.
    """
    # URL encode the query
    encoded_query = urllib.parse.quote(query)
    # Google News RSS URL for Japan (hl=ja&gl=JP&ceid=JP:ja)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
    
    feed = feedparser.parse(rss_url)
    
    news_list = []
    
    for entry in feed.entries[:max_results]:
        # Parse published date if possible, else keep raw
        published = entry.published
        
        # Clean summary (sometimes contains HTML)
        summary = entry.summary if 'summary' in entry else ""
        
        news_item = {
            "title": entry.title,
            "link": entry.link,
            "published": published,
            "summary": summary,
            "source": entry.source.title if 'source' in entry else "Google News"
        }
        news_list.append(news_item)
        
    return news_list

if __name__ == "__main__":
    # Test
    res = fetch_google_news_rss("トヨタ自動車")
    for item in res:
        print(item)
