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

# 수집 카테고리 (정치 제외, 경제·사회·IT·국제·문화 등 균형 있게)
NEWS_CATEGORIES = [
    # 국내
    {"name": "국내 경제·산업",  "rss": "https://www.hankyung.com/feed/economy",              "naver_query": "경제 산업 기업"},
    {"name": "국내 사회·문화",  "rss": "https://www.yonhapnews.co.kr/rss/society.xml",       "naver_query": "사회 문화 교육 환경"},
    {"name": "국내 과학·기술",  "rss": "https://rss.etnews.com/Section901.xml",              "naver_query": "과학 기술 혁신"},
    # 해외
    {"name": "해외 경제·비즈니스", "rss": "https://feeds.bbci.co.uk/news/business/rss.xml",  "naver_query": ""},
    {"name": "해외 사회·환경",  "rss": "https://feeds.bbci.co.uk/news/world/rss.xml",        "naver_query": ""},
    {"name": "해외 테크·혁신",  "rss": "https://techcrunch.com/feed/",                       "naver_query": ""},
]

# 카테고리당 최대 기사 수
MAX_ARTICLES_PER_CATEGORY = 5

# Gemini 모델 우선순위
GEMINI_MODEL_PRIORITY = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]
