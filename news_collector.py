"""
뉴스 수집 모듈
RSS 피드와 네이버 뉴스 API를 사용해 뉴스를 수집합니다.
"""
import feedparser
import requests
import logging
from datetime import datetime, timezone, timedelta
from config import NEWS_CATEGORIES, MAX_ARTICLES_PER_CATEGORY, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))


def fetch_rss_articles(rss_url: str, category_name: str, max_count: int) -> list[dict]:
    """RSS 피드에서 최신 기사를 가져옵니다."""
    articles = []
    try:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:max_count]:
            title = entry.get("title", "").strip()
            summary = entry.get("summary", entry.get("description", "")).strip()
            link = entry.get("link", "")
            pub_date = entry.get("published", "")

            if not title or not link:
                continue

            # HTML 태그 간단히 제거
            import re
            summary = re.sub(r"<[^>]+>", "", summary)
            summary = summary[:500].strip()

            articles.append({
                "category": category_name,
                "title": title,
                "summary": summary,
                "url": link,
                "source": feed.feed.get("title", rss_url),
                "pub_date": pub_date,
            })
        logger.info(f"[RSS] {category_name}: {len(articles)}건 수집")
    except Exception as e:
        logger.warning(f"[RSS] {category_name} 수집 실패: {e}")
    return articles


def fetch_naver_articles(query: str, category_name: str, max_count: int) -> list[dict]:
    """네이버 뉴스 검색 API로 기사를 가져옵니다."""
    if not query or not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return []

    articles = []
    try:
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
        }
        params = {
            "query": query,
            "display": max_count,
            "sort": "date",
        }
        resp = requests.get(
            "https://openapi.naver.com/v1/search/news.json",
            headers=headers,
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])

        import re
        for item in items:
            title = re.sub(r"<[^>]+>", "", item.get("title", "")).strip()
            description = re.sub(r"<[^>]+>", "", item.get("description", "")).strip()
            link = item.get("originallink") or item.get("link", "")

            if not title:
                continue

            articles.append({
                "category": category_name,
                "title": title,
                "summary": description[:500],
                "url": link,
                "source": "네이버 뉴스",
                "pub_date": item.get("pubDate", ""),
            })
        logger.info(f"[Naver] {category_name}: {len(articles)}건 수집")
    except Exception as e:
        logger.warning(f"[Naver] {category_name} 수집 실패: {e}")
    return articles


def collect_all_news() -> list[dict]:
    """모든 카테고리의 뉴스를 수집하여 반환합니다."""
    all_articles = []
    seen_titles = set()

    for cat in NEWS_CATEGORIES:
        name = cat["name"]
        rss = cat.get("rss", "")
        naver_query = cat.get("naver_query", "")

        # RSS 우선 시도
        articles = []
        if rss:
            articles = fetch_rss_articles(rss, name, MAX_ARTICLES_PER_CATEGORY)

        # RSS 결과가 부족하면 네이버 API 보완
        if len(articles) < MAX_ARTICLES_PER_CATEGORY and naver_query:
            naver_articles = fetch_naver_articles(
                naver_query, name, MAX_ARTICLES_PER_CATEGORY - len(articles)
            )
            articles.extend(naver_articles)

        # 중복 제거
        for article in articles:
            title_key = article["title"][:30]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                all_articles.append(article)

    logger.info(f"총 {len(all_articles)}건 기사 수집 완료")
    return all_articles
