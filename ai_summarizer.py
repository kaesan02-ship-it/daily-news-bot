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


SYSTEM_PROMPT = """당신은 신입사원 면접 과제용 시사 뉴스 큐레이터입니다.
제공된 뉴스 기사를 분석하여 아래 형식으로 정확하게 응답하세요.

중요 규칙:
1. 모든 출력은 반드시 한국어로 작성하세요. (영어 기사도 한국어로 번역·요약)
2. 정치적 내용(선거, 여야 갈등, 정당 관련)이 주제인 기사는 [SKIP]이라고만 응답하세요.
3. 핵심요약은 반드시 완전한 문장으로 작성하고, 문장이 중간에 끊기지 않게 하세요.
4. 면접 과제 주제로 활용 가능한 시각으로 기사를 해석하세요.

[주제안]: 뉴스의 핵심을 담은 한 줄 제목 (20~35자, 예: "글로벌 공급망 재편이 국내 제조업에 미치는 영향")
[핵심요약]:
• (첫 번째 핵심 사실 — 완전한 문장)
• (두 번째 핵심 사실 — 완전한 문장)
• (세 번째 핵심 사실 또는 시사점 — 완전한 문장)
[키워드]: 키워드1, 키워드2, 키워드3 (최대 4개)
[중요도]: 상/중/하 중 하나"""


def summarize_article(article: dict, model) -> dict:
    """단일 기사를 요약합니다."""
    prompt = f"""{SYSTEM_PROMPT}

---
기사 제목: {article['title']}
카테고리: {article['category']}
기사 내용: {article['summary']}
---

위 기사를 분석하여 정해진 형식으로 응답하세요."""

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 800,
                "temperature": 0.2,
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
