# Restaurant Review 프로젝트 폴더 구조 설명

이 프로젝트는 FastAPI 백엔드와 바닐라 JS 기반의 프론트엔드(View)를 사용하는 식당 리뷰 서비스입니다. 아래는 폴더 및 파일 구조와 각 역할에 대한 설명입니다.

```
restaurant_review/
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
  - **images/**: 이미지 파일이 위치합니다.

- **tests/**: 테스트 코드가 위치합니다.

- **.env**: 환경 변수 파일입니다. (DB, API 키 등 민감 정보 관리)

- **.gitignore**: Git에서 제외할 파일/폴더 목록입니다.

- **requirements.txt**: Python 의존성 패키지 목록입니다.

- **README.md**: 프로젝트 설명 및 폴더 구조 안내 파일입니다.

---

이 구조는 백엔드와 프론트엔드, 데이터 크롤링 및 처리, 정적 파일 관리까지 명확하게 분리하여 유지보수와 확장성을 높이기 위해 설계되었습니다.
