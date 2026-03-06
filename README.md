# 📰 매일 아침 뉴스 자동화 시스템

> 매일 오전 7시, 주요 시사 뉴스를 AI로 수집·요약하여 구글 시트에 자동 업로드합니다.

## 📁 파일 구조

```
├── main.py               # 메인 실행 (전체 파이프라인)
├── config.py             # 설정값 (환경변수 읽기)
├── news_collector.py     # 뉴스 수집 (RSS + 네이버 API)
├── ai_summarizer.py      # AI 요약 + 주제안 생성 (Gemini)
├── sheets_uploader.py    # 구글 시트 업로드
├── test_run.py           # 로컬 테스트용 스크립트
├── requirements.txt      # Python 패키지
└── .github/workflows/
    └── daily_news.yml    # GitHub Actions (매일 07:00 KST 자동 실행)
```

---

## 🚀 시작하기 (최초 1회 설정)

### 1단계: Gemini API 키 발급
1. [Google AI Studio](https://aistudio.google.com) 접속
2. **Get API Key** → API 키 복사

---

### 2단계: Google Sheets API 설정

1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성
3. **Google Sheets API** + **Google Drive API** 활성화
4. **서비스 계정(Service Account)** 생성 → JSON 키 파일 다운로드
5. **구글 시트** 하나 생성 → 서비스 계정 이메일을 **편집자**로 공유
6. 구글 시트 URL에서 ID 복사:
   `https://docs.google.com/spreadsheets/d/` **`[여기가 SPREADSHEET_ID]`** `/edit`

---

### 3단계: 네이버 뉴스 API 등록 (선택)
1. [네이버 개발자 센터](https://developers.naver.com) → 애플리케이션 등록
2. **검색** API 사용 체크 → Client ID, Client Secret 발급

---

### 4단계: GitHub에 Secret 등록

GitHub Repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret 이름 | 값 |
|---|---|
| `GEMINI_API_KEY` | Gemini API 키 |
| `GOOGLE_CREDENTIALS_JSON` | 서비스 계정 JSON 파일 **전체 내용** (텍스트로 붙여넣기) |
| `SPREADSHEET_ID` | 구글 시트 ID |
| `SHEET_NAME` | 시트 탭 이름 (기본값: `뉴스_자동정리`) |
| `NAVER_CLIENT_ID` | 네이버 Client ID (선택) |
| `NAVER_CLIENT_SECRET` | 네이버 Client Secret (선택) |

---

### 5단계: GitHub에 코드 Push

```bash
git init
git add .
git commit -m "초기 뉴스 자동화 시스템"
git remote add origin https://github.com/YOUR_ID/YOUR_REPO.git
git push -u origin main
```

→ GitHub Actions 탭에서 **"Daily News Aggregator"** 워크플로우 확인

---

## 🧪 로컬 테스트

```bash
# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정 (Windows PowerShell)
$env:GEMINI_API_KEY="your_key"
$env:GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
$env:SPREADSHEET_ID="your_sheet_id"

# 뉴스 수집만 테스트 (AI 제외)
python test_run.py --skip-ai

# AI 요약까지 테스트
python test_run.py

# 전체 실행
python main.py
```

---

## 📊 구글 시트 구조

| 날짜 | 카테고리 | 주제안 | 핵심요약 | 키워드 | 중요도 | 원문 출처 | URL |
|---|---|---|---|---|---|---|---|
| 2026-03-06 | 국내 IT·AI | AI 반도체 수출 제한 강화 | • ... | AI, 반도체 | 상 | 연합뉴스 | https://... |

- 새 데이터는 항상 **맨 위에** 삽입 (최신 데이터가 상단)
- 중요도 **상**(빨간색), **중**(노란색), **하**(회색) 로 자동 색상 표시
- 같은 날짜 데이터 **중복 삽입 방지** 내장

---

## ⏰ 자동 실행 스케줄

| 항목 | 내용 |
|---|---|
| 실행 시간 | 매일 오전 **7:00 KST** |
| 수동 실행 | GitHub Actions 탭 → **"Run workflow"** 버튼 |
| 무료 한도 | GitHub Actions 월 2,000분 (하루 약 5분 사용) |

---

## 💰 비용

모든 API를 무료 티어로 운영 가능합니다.

| 항목 | 비용 |
|---|---|
| Gemini API (Flash 모델) | 무료 |
| 네이버 뉴스 API | 무료 |
| Google Sheets API | 무료 |
| GitHub Actions | 무료 (월 2,000분) |
