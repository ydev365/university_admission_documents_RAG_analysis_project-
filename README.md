# 세부능력특기사항 RAG 서비스

학생들의 세부능력특기사항(세특) 작성을 도와주는 AI 기반 RAG 서비스입니다.
상명대학교 컴퓨터과학과 합격생들의 세특 데이터를 기반으로 맞춤형 조언을 제공합니다.

## 기술 스택

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Vector DB**: ChromaDB (세특 데이터 임베딩 저장)
- **Chat DB**: MySQL (대화 기록 저장)
- **AI**: OpenAI API (GPT-4o-mini, text-embedding-3-small)

## 빠른 시작 (이미 설정 완료된 경우)

### 1. Docker MySQL 시작
```bash
docker start mysql-setuek
```

### 2. 백엔드 실행 (터미널 1)
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 프론트엔드 실행 (터미널 2)
```bash
cd frontend
npm run dev
```

### 4. 접속
- Frontend: http://localhost:5173
- Backend API 문서: http://localhost:8000/docs

---

## 처음 설정하기

### 1. 사전 요구사항

- Python 3.10+
- Node.js 18+
- Docker Desktop
- OpenAI API Key

### 2. MySQL 데이터베이스 설정 (Docker)

```bash
# MySQL 이미지 다운로드
docker pull mysql:8.0

# MySQL 컨테이너 실행
docker run --name mysql-setuek ^
  -e MYSQL_ROOT_PASSWORD=1234 ^
  -e MYSQL_DATABASE=setuek_rag ^
  -p 3306:3306 ^
  -v mysql-setuek-data:/var/lib/mysql ^
  -d mysql:8.0

# 컨테이너 상태 확인
docker ps --filter "name=mysql-setuek"
```

**Docker MySQL 관리 명령어:**
```bash
docker stop mysql-setuek   # 컨테이너 중지
docker start mysql-setuek  # 컨테이너 시작
docker exec -it mysql-setuek mysql -uroot -p1234  # MySQL 쉘 접속
```

### 3. Backend 설정

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정
copy .env.example .env
# .env 파일을 열어 OPENAI_API_KEY 수정
```

### 4. ChromaDB 초기화 (데이터 임베딩)

```bash
cd backend
python scripts/init_vectordb.py
```

이 스크립트는:
- 세특 데이터 파일들을 파싱
- OpenAI API로 임베딩 생성
- ChromaDB에 저장

### 5. Frontend 설정

```bash
cd frontend
npm install
```

---

## 프로젝트 구조

```
세부능력특기사항_RAG_project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 앱
│   │   ├── config.py            # 설정
│   │   ├── database.py          # DB 연결
│   │   ├── models/              # SQLAlchemy 모델
│   │   ├── schemas/             # Pydantic 스키마
│   │   ├── routers/             # API 라우터
│   │   ├── services/            # 비즈니스 로직 (RAG)
│   │   └── utils/               # 유틸리티
│   ├── scripts/
│   │   └── init_vectordb.py     # ChromaDB 초기화
│   ├── chroma_db/               # ChromaDB 데이터 (임베딩)
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── ChatPage.tsx     # 메인 채팅 페이지
│   │   ├── services/
│   │   │   └── api.ts           # API 호출
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── tailwind.config.js
└── 상명대_컴퓨터과학과_합격생들_세부능력및특기사항_data_취합/
    └── *.txt                    # 세특 데이터 파일
```

## 주요 기능

1. **RAG 기반 질문/답변**: 과목 선택 후 세특 관련 질문
2. **대화 기록**: 왼쪽 사이드바에서 이전 대화 확인
3. **과목별 검색**: 50개 이상의 과목 지원

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | /api/chat/subjects | 과목 목록 조회 |
| POST | /api/chat | RAG 질문/답변 |
| GET | /api/history | 대화 기록 조회 |
| GET | /api/history/{id} | 특정 대화 조회 |

## 환경변수 (.env)

```env
# Database (Docker MySQL)
DATABASE_URL=mysql+pymysql://root:1234@localhost:3306/setuek_rag

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

## 문제 해결

### Docker MySQL 연결 실패
```bash
# Docker Desktop이 실행 중인지 확인
docker ps

# 컨테이너가 없으면 다시 생성
docker run --name mysql-setuek ...
```

### 패키지 설치 오류 (cryptography)
```bash
pip install --upgrade pip setuptools wheel
pip install cryptography --only-binary :all:
pip install -r requirements.txt
```

## 라이센스

MIT License
