"""
설정값 관리 모듈
환경변수(GitHub Secrets) 또는 로컬 .env 파일에서 API 키를 읽어옵니다.
"""
import os

# ── Gemini API ──────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ── Google Sheets ───────────────────────────────────────────
# GitHub Actions에서는 GOOGLE_CREDENTIALS_JSON Secret을 사용합니다.
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "")  # 구글 시트 ID
SHEET_NAME = os.environ.get("SHEET_NAME", "뉴스_자동정리")  # 시트 탭 이름

# ── 뉴스 수집 설정 ───────────────────────────────────────────
NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET", "")

# 수집 카테고리 (정치 제외, 일반시사·IT·경제 등)
NEWS_CATEGORIES = [
    {"name": "국내 일반",   "rss": "https://feeds.feedburner.com/yonhapnews/society",  "naver_query": "사회 이슈"},
    {"name": "국내 경제",   "rss": "https://feeds.feedburner.com/yonhapnews/economy", "naver_query": "경제 금융"},
    {"name": "국내 IT·AI", "rss": "https://rss.etnews.com/Section901.xml",            "naver_query": "AI 인공지능 기술"},
    {"name": "해외 시사",   "rss": "https://feeds.bbci.co.uk/news/world/rss.xml",     "naver_query": ""},
    {"name": "해외 테크",   "rss": "https://techcrunch.com/feed/",                    "naver_query": ""},
]

# 카테고리당 최대 기사 수
MAX_ARTICLES_PER_CATEGORY = 5

# Gemini 모델 우선순위
GEMINI_MODEL_PRIORITY = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]
