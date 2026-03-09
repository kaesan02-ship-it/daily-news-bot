"""
AI 요약 모듈
Gemini API를 사용해 뉴스 기사를 요약하고 주제안을 생성합니다.
"""
import logging
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from config import GEMINI_API_KEY, GEMINI_MODEL_PRIORITY

logger = logging.getLogger(__name__)


def _get_model():
    """사용 가능한 Gemini 모델을 선택합니다 (테스트 호출 없이 바로 반환)."""
    genai.configure(api_key=GEMINI_API_KEY)
    model_name = GEMINI_MODEL_PRIORITY[0]
    logger.info(f"Gemini 모델 사용: {model_name}")
    return genai.GenerativeModel(model_name)


SYSTEM_PROMPT = """당신은 뉴스 콘텐츠 기획 전문가입니다.
제공된 뉴스 기사를 읽고 다음 형식으로 정확하게 응답하세요.

[주제안]: 해당 뉴스의 핵심을 담은 한 줄 제목 (15~30자, 예: "국내 AI 반도체 규제 강화 동향")
[핵심요약]: 3~5줄 핵심 내용 요약. 각 줄은 "• "으로 시작
[키워드]: 핵심 키워드 3~5개를 쉼표로 구분 (예: AI, 반도체, 수출규제)
[중요도]: 상/중/하 중 하나만 선택

절대 다른 내용이나 형식을 추가하지 마세요."""


def summarize_article(article: dict, model) -> dict:
    """단일 기사를 요약합니다."""
    prompt = f"""제목: {article['title']}
카테고리: {article['category']}
내용 미리 보기: {article['summary']}

위 뉴스를 분석하여 정해진 형식으로 응답하세요."""

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 500,
                "temperature": 0.3,
            },
        )
        text = response.text.strip()

        # 파싱
        result = {
            "주제안": _parse_field(text, "주제안"),
            "핵심요약": _parse_field(text, "핵심요약"),
            "키워드": _parse_field(text, "키워드"),
            "중요도": _parse_field(text, "중요도"),
        }

        # 파싱 실패 시 원본 제목 사용
        if not result["주제안"]:
            result["주제안"] = article["title"][:50]
        if not result["핵심요약"]:
            result["핵심요약"] = article["summary"][:200]

        return result

    except Exception as e:
        logger.warning(f"기사 요약 실패 ({article['title'][:30]}): {e}")
        return {
            "주제안": article["title"][:50],
            "핵심요약": article["summary"][:300],
            "키워드": "",
            "중요도": "중",
        }


def _parse_field(text: str, field_name: str) -> str:
    """응답 텍스트에서 특정 필드를 추출합니다."""
    import re
    pattern = rf"\[{field_name}\]\s*:?\s*(.+?)(?=\[|$)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def summarize_all(articles: list[dict]) -> list[dict]:
    """모든 기사를 요약하고 결과를 반환합니다."""
    if not articles:
        return []

    model = _get_model()
    results = []

    for i, article in enumerate(articles):
        logger.info(f"요약 중 ({i+1}/{len(articles)}): {article['title'][:40]}")
        summary = summarize_article(article, model)

        results.append({
            **article,
            **summary,
        })

    logger.info(f"총 {len(results)}건 요약 완료")
    return results
