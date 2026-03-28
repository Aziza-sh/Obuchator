from prometheus_client import Counter

# Created
NEWS_CREATED = Counter("news_created_total", "Total created news")

# Deleted
NEWS_DELETED = Counter("news_deleted_total", "Total deleted news")

# Requests
NEWS_FETCHED = Counter("news_fetched_total", "Total news fetch requests")
