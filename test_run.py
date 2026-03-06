"""
로컬 테스트 스크립트
실제 API 호출 없이 흐름을 검증하거나, 키 설정 후 단일 실행 테스트에 사용합니다.
"""
import os
import sys
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def check_env():
    """필요한 환경변수가 설정되어 있는지 확인합니다."""
    required = ["GEMINI_API_KEY", "GOOGLE_CREDENTIALS_JSON", "SPREADSHEET_ID"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        logger.error(f"❌ 다음 환경변수가 설정되어 있지 않습니다: {missing}")
        logger.info("   .env 파일을 만들거나, 아래처럼 터미널에서 설정하세요:")
        for k in missing:
            logger.info(f"   set {k}=your_value_here   (Windows)")
            logger.info(f"   export {k}=your_value_here (Mac/Linux)")
        return False
    logger.info("✅ 모든 필수 환경변수 설정 확인 완료")
    return True


def test_news_collection():
    """뉴스 수집 모듈만 단독 테스트합니다."""
    from news_collector import collect_all_news
    articles = collect_all_news()
    logger.info(f"수집된 기사 수: {len(articles)}")
    for a in articles[:3]:
        logger.info(f"  [{a['category']}] {a['title'][:60]}")
    return articles


def test_ai_summary(articles):
    """AI 요약 모듈을 테스트합니다 (최대 2건만)."""
    from ai_summarizer import summarize_all
    subset = articles[:2]
    results = summarize_all(subset)
    for r in results:
        logger.info(f"\n  카테고리: {r['category']}")
        logger.info(f"  주제안: {r.get('주제안', 'N/A')}")
        logger.info(f"  키워드: {r.get('키워드', 'N/A')}")
        logger.info(f"  중요도: {r.get('중요도', 'N/A')}")
    return results


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("🧪 로컬 테스트 시작")
    logger.info("=" * 50)

    if not check_env():
        sys.exit(1)

    logger.info("\n▶ 뉴스 수집 테스트...")
    articles = test_news_collection()

    if "--skip-ai" not in sys.argv:
        logger.info("\n▶ AI 요약 테스트 (2건)...")
        test_ai_summary(articles)
    else:
        logger.info("(--skip-ai 옵션으로 AI 요약 건너뜀)")

    logger.info("\n✅ 테스트 완료! 전체 실행은 main.py를 사용하세요.")
