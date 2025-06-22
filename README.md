# Blog Review 프로젝트

이 프로젝트는 네이버 블로그 검색 API를 활용한 리뷰 분석 서비스입니다. FastAPI 백엔드와 바닐라 JS 기반의 프론트엔드를 사용하여 블로그 포스트를 검색하고 분석할 수 있습니다.

## 주요 기능

- **네이버 블로그 검색**: 네이버 Open API를 통한 블로그 포스트 검색
- **실시간 검색**: 키워드 기반 블로그 검색 및 결과 표시
- **구조화된 데이터**: 검색 결과를 정제하여 JSON 형태로 제공
- **헬스체크**: API 서버 상태 모니터링

## 프로젝트 구조

```
blog_review/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routers/
│   ├── core/
│   ├── models/
│   ├── services/
│   └── utils/
├── crawler/
├── data_processor/
├── static/
│   ├── js/
│   ├── css/
│   └── images/
├── tests/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## 폴더 및 파일 설명

- **app/**: FastAPI 백엔드의 핵심 코드가 위치합니다.
  - **__init__.py**: 패키지 초기화 파일입니다.
  - **main.py**: FastAPI 앱의 진입점(실행 파일)입니다.
  - **routers/**: API 라우터 파일들이 위치합니다. (엔드포인트별로 분리)
  - **core/**: 환경설정, 데이터베이스 연결 등 핵심 설정 파일이 위치합니다.
  - **models/**: SQLAlchemy 및 Pydantic 모델 정의 파일이 위치합니다.
  - **services/**: 비즈니스 로직(예: 네이버 API 연동, 식당 서비스 등)이 위치합니다.
  - **utils/**: 공통적으로 사용하는 유틸리티 함수들이 위치합니다.

- **crawler/**: Selenium, BeautifulSoup 등 크롤러 관련 코드가 위치합니다.

- **data_processor/**: 크롤링한 데이터의 정제, 전처리, 분석 코드가 위치합니다.

- **static/**: 정적 파일(프론트엔드 JS, CSS, 이미지 등)이 위치합니다.
  - **js/**: 바닐라 JS 파일이 위치합니다.
  - **css/**: CSS 파일이 위치합니다.
  - **index.html**: HTML 파일입니다.  

- **tests/**: 테스트 코드가 위치합니다.

- **.env**: 환경 변수 파일입니다. (DB, API 키 등 민감 정보 관리)

- **.gitignore**: Git에서 제외할 파일/폴더 목록입니다.

- **requirements.txt**: Python 의존성 패키지 목록입니다.

- **README.md**: 프로젝트 설명 및 폴더 구조 안내 파일입니다.

---

## 설치 및 실행

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 네이버 API 설정

`.env` 파일을 생성하고 네이버 Open API 정보를 입력합니다:

```env
NAVER_CLIENT_ID=your_client_id_here
NAVER_CLIENT_SECRET=your_client_secret_here
```

### 3. 서버 실행

```bash
# FastAPI 서버 실행
uvicorn app.main:app --reload

# 또는
python -m uvicorn app.main:app --reload
```

서버 실행 후 다음 주소에서 확인할 수 있습니다:
- API 문서: http://localhost:8000/docs
- 웹 인터페이스: http://localhost:8000

## API 사용법

### 블로그 검색

```bash
curl -X GET "http://localhost:8000/api/v1/blog/search?query=리뷰&display=10&start=1&sort=sim"
```

**파라미터:**
- `query`: 검색어 (필수)
- `display`: 표시할 결과 개수 (1~100, 기본값: 10)
- `start`: 검색 시작 위치 (1~1000, 기본값: 1)
- `sort`: 정렬 방식 (sim: 정확도순, date: 날짜순, 기본값: sim)

## 테스트

```bash
# API 테스트 스크립트 실행
python test_naver_api.py
```

## 네이버 API 설정 방법

1. [네이버 개발자 센터](https://developers.naver.com/)에서 애플리케이션 등록
2. 검색 API 사용 권한 설정
3. 발급받은 Client ID와 Client Secret을 `.env` 파일에 저장

이 구조는 백엔드와 프론트엔드, 데이터 크롤링 및 처리, 정적 파일 관리까지 명확하게 분리하여 유지보수와 확장성을 높이기 위해 설계되었습니다.
