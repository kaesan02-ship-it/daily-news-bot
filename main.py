"""
메인 실행 파일
뉴스 수집 → AI 요약 → 구글 시트 업로드 파이프라인을 실행합니다.
"""
import logging
import sys
from datetime import datetime, timezone, timedelta

from news_collector import collect_all_news
from ai_summarizer import summarize_all
from sheets_uploader import upload_to_sheets

# ── 로깅 설정 ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))


def main():
    start_time = datetime.now(KST)
    logger.info("=" * 60)
    logger.info(f"📰 뉴스 자동화 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S KST')}")
    logger.info("=" * 60)

    # Step 1: 뉴스 수집
    logger.info("▶ Step 1: 뉴스 수집 중...")
    articles = collect_all_news()
    if not articles:
        logger.error("수집된 기사가 없습니다. 종료합니다.")
        sys.exit(1)
    logger.info(f"   → {len(articles)}건 수집 완료")

    # Step 2: AI 요약 및 주제안 생성
    logger.info("▶ Step 2: AI 요약 및 주제안 생성 중...")
    summarized = summarize_all(articles)
    if not summarized:
        logger.error("요약 결과가 없습니다. 종료합니다.")
        sys.exit(1)
    logger.info(f"   → {len(summarized)}건 요약 완료")

    # Step 3: 구글 시트 업로드
    logger.info("▶ Step 3: 구글 시트 업로드 중...")
    uploaded_count = upload_to_sheets(summarized)
    logger.info(f"   → {uploaded_count}행 업로드 완료")

    # 완료 요약
    elapsed = (datetime.now(KST) - start_time).total_seconds()
    logger.info("=" * 60)
    logger.info(f"✅ 완료! 총 {elapsed:.1f}초 소요 | 업로드: {uploaded_count}건")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
