"""
구글 시트 업로드 모듈
날짜 컬럼을 포함한 단일 시트에 뉴스 데이터를 누적 업로드합니다.
"""
import json
import logging
from datetime import datetime, timezone, timedelta

import gspread
from google.oauth2.service_account import Credentials

from config import GOOGLE_CREDENTIALS_JSON, SPREADSHEET_ID, SHEET_NAME

logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))

# 시트 헤더 정의
HEADERS = ["날짜", "카테고리", "주제안", "핵심요약", "키워드", "중요도", "원문 출처", "URL"]

# 중요도별 색상 (RGB 비율, 0~1)
IMPORTANCE_COLORS = {
    "상": {"red": 1.0,  "green": 0.85, "blue": 0.85},
    "중": {"red": 1.0,  "green": 1.0,  "blue": 0.85},
    "하": {"red": 0.95, "green": 0.95, "blue": 0.95},
}


def _get_client() -> gspread.Client:
    """Google Sheets 클라이언트를 초기화합니다."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)


def _ensure_header(sheet: gspread.Worksheet):
    """헤더 행이 없으면 추가합니다."""
    first_row = sheet.row_values(1)
    if first_row != HEADERS:
        sheet.insert_row(HEADERS, index=1)
        # 헤더 서식 — 굵게 + 배경색(진한 파랑)
        sheet.format("A1:H1", {
            "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.8},
            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
            "horizontalAlignment": "CENTER",
        })
        logger.info("헤더 행 추가 완료")


def _apply_row_color(sheet: gspread.Worksheet, row_index: int, importance: str):
    """중요도에 따라 행 배경색을 적용합니다."""
    color = IMPORTANCE_COLORS.get(importance, IMPORTANCE_COLORS["하"])
    range_notation = f"A{row_index}:H{row_index}"
    sheet.format(range_notation, {"backgroundColor": color})


def upload_to_sheets(summarized_articles: list[dict]) -> int:
    """요약된 기사 목록을 구글 시트에 업로드합니다.

    Returns:
        업로드된 행 수
    """
    if not summarized_articles:
        logger.warning("업로드할 기사가 없습니다.")
        return 0

    client = _get_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    # 시트 탭 가져오기 (없으면 생성)
    try:
        sheet = spreadsheet.worksheet(SHEET_NAME)
    except gspread.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=10000, cols=len(HEADERS))
        logger.info(f"새 시트 탭 생성: {SHEET_NAME}")

    _ensure_header(sheet)

    today_str = datetime.now(KST).strftime("%Y-%m-%d")

    # 오늘 날짜 데이터 중복 방지: 기존 날짜 컬럼 확인
    existing_dates = sheet.col_values(1)
    if today_str in existing_dates:
        logger.warning(f"{today_str} 데이터가 이미 존재합니다. 건너뜁니다.")
        return 0

    # 행 데이터 구성
    rows_to_insert = []
    for article in summarized_articles:
        row = [
            today_str,
            article.get("category", ""),
            article.get("주제안", ""),
            article.get("핵심요약", ""),
            article.get("키워드", ""),
            article.get("중요도", "중"),
            article.get("source", ""),
            article.get("url", ""),
        ]
        rows_to_insert.append(row)

    # 헤더 바로 아래(2번째 행)에 삽입하여 최신 데이터가 위에 오도록
    insert_start = 2
    sheet.insert_rows(rows_to_insert, row=insert_start)

    # 중요도별 색상 적용
    for i, article in enumerate(summarized_articles):
        row_index = insert_start + i
        _apply_row_color(sheet, row_index, article.get("중요도", "중"))

    # 열 너비 자동 조정 (Batch update)
    col_widths = [120, 100, 250, 420, 150, 60, 120, 200]
    requests_body = []
    for col_idx, width in enumerate(col_widths):
        requests_body.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet.id,
                    "dimension": "COLUMNS",
                    "startIndex": col_idx,
                    "endIndex": col_idx + 1,
                },
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })
    if requests_body:
        spreadsheet.batch_update({"requests": requests_body})

    logger.info(f"{len(rows_to_insert)}행 업로드 완료 → 시트: {SHEET_NAME}")
    return len(rows_to_insert)
