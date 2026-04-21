# 환경 구축 가이드 (uv 기반)

## 1. 필수 소프트웨어

| 항목 | 버전 | 용도 |
|------|------|------|
| [uv](https://docs.astral.sh/uv/) | 최신 | Python·의존성 일괄 관리 (권장 경로) |
| Python | 3.11 | uv가 자동 설치하므로 별도 설치 불필요 |
| Docker Desktop | 최신 | Neo4j(S3-6) |
| Git | 2.40+ | 교안 clone |

### uv 설치 (30초)
```bash
# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```
설치 후 새 터미널에서 `uv --version` 확인.

### 시스템 패키지 (Unstructured PDF 파서용)
`uv sync`로는 해결되지 않는 OS 레벨 의존성입니다. Day 1 S2-1 노트북의 `UnstructuredPDFLoader`에서 사용.

```bash
# Ubuntu / WSL
sudo apt install -y poppler-utils libmagic1

# macOS
brew install poppler libmagic

# Windows
# https://github.com/oschwartz10612/poppler-windows 릴리스 zip을 받아 bin/을 PATH에 추가
```

OCR(스캔 PDF)까지 실습할 경우 선택적으로 `tesseract-ocr`도 설치:
`sudo apt install tesseract-ocr` / `brew install tesseract` / Windows는 UB Mannheim 빌드 사용.

### Docker Desktop
- Windows: WSL2 백엔드 권장
- macOS: 공식 설치 프로그램

---

## 2. 프로젝트 셋업 (한 줄)

```bash
git clone <repo-url> airgap-llm-edu
cd airgap-llm-edu
uv sync              # Python 3.11 자동 설치 + 모든 의존성 설치 (수 분)
```

`uv sync`가 `.venv/`를 만들고 `uv.lock`에 핀된 버전으로 전체 패키지를 설치합니다.

### 가상환경 활성화 (선택)
`uv run` 명령 앞에 붙이면 자동 활성화되므로 명시적 activate가 필요 없지만, 전통적으로 하려면:
```bash
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

---

## 3. 환경변수

```bash
# Windows
copy .env.example .env
# macOS/Linux
cp .env.example .env
```

`.env` 수정 (인라인 주석 금지 — `python-dotenv`가 값에 포함해 버립니다):
```bash
OPENAI_API_KEY=sk-or-v1-...
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini
OPENAI_EMBEDDING_MODEL=openai/text-embedding-3-small

LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

OpenRouter가 아닌 OpenAI 본가를 쓰려면 `OPENAI_API_BASE`를 비우거나 지우고 `OPENAI_MODEL=gpt-4o-mini`로 두면 됩니다.

---

## 4. Docker 서비스 — OpenWebUI + Pipelines + Langfuse 스택

강의 시연용 3-tier 스택. `.env`의 `OPENAI_API_KEY`(OpenRouter)만 채워두면 기타 값은 기본값으로 동작한다.

```bash
docker compose up -d
docker compose ps          # 8개 서비스 모두 healthy/running
```

접속:

| 용도 | URL | 로그인 |
|------|-----|--------|
| OpenWebUI (chat) | http://localhost:3000 | 첫 가입자가 관리자 |
| Langfuse (관측성) | http://localhost:3001 | `.env`의 `LANGFUSE_INIT_USER_EMAIL` / `_PASSWORD` (기본 `admin@airgap.local` / `admin1234`) |
| MinIO 콘솔 (선택) | http://localhost:9091 | `minio` / `miniosecret` |

**Langfuse 필터 연결 (최초 1회)** — OpenWebUI Admin Panel → Settings → Pipelines 에서 `Langfuse Filter Pipeline`의 valves를 연다:

- `secret_key` = `.env`의 `LANGFUSE_INIT_PROJECT_SECRET_KEY`
- `public_key` = `.env`의 `LANGFUSE_INIT_PROJECT_PUBLIC_KEY`
- `host` = `http://langfuse-web:3000`

저장 후 OpenWebUI에서 OpenRouter 모델(예: `openai/gpt-4o-mini`)로 대화 한 번 → Langfuse *Traces* 탭에 prompt·completion·usage·latency가 나타난다.

### 종료
```bash
docker compose down         # 볼륨 보존
docker compose down -v      # 데이터 완전 초기화
```

---

## 5. Jupyter 실행

```bash
uv run jupyter lab
```
브라우저에서 `http://localhost:8888` 열림. `day1/session1_llm_basics/01_transformer_attention.ipynb`부터 순서대로 실행.

---

## 6. 폐쇄망 반입 절차 (오프라인 환경)

외부망에서 한 번 수행한 뒤 내부망으로 복사합니다.

```bash
# 외부망
uv pip compile pyproject.toml -o requirements.txt
uv pip download -r requirements.txt -d offline_wheels/ --python-version 3.11

# 내부망 (동일 OS·아키텍처)
uv venv --python 3.11
uv pip install --no-index --find-links ./offline_wheels -r requirements.txt

# NLTK 데이터도 함께 반입 (Unstructured 로더가 런타임에 요구)
# 외부망에서 아래 실행 후 생성된 ~/.cache/nltk_data 디렉터리를 내부망 동일 경로로 복사
uv run python -c "import nltk; nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger_eng')"
```

---

## 7. 문제 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| `uv: command not found` | PATH 미반영 | 새 터미널 열기, 또는 `~/.local/bin`을 PATH에 추가 |
| `uv sync` 느림 | 초회 다운로드 | 두 번째부터는 캐시 사용, 수 초 이내 |
| OpenAI 401 | `.env` 미로드 / 키 오타 | 노트북 커널 재시작 후 첫 셀 실행 (common/llm.py가 `load_dotenv()`) |
| `Unknown LLM_PROVIDER: 'openai   # ...'` | `.env`에 인라인 주석 | 주석을 별도 라인으로 이동 |
| Neo4j 연결 실패 | 컨테이너 미기동 | `docker ps`, `docker compose up -d neo4j` |
| faiss-cpu 설치 실패 (Windows) | wheel 없음 | `uv add faiss-cpu --python-downloads never` 후 재시도 또는 Chroma만 사용 |
| 한글 폰트 깨짐 (matplotlib) | 한글 폰트 없음 | 노트북 1-1 첫 셀 참고 (Malgun Gothic / AppleGothic) |
| `UnstructuredPDFLoader` 로드 실패 (`pdfminer.six`/`pdf2image` ImportError, `poppler not installed`, `Resource punkt_tab not found`) | `[pdf]` extras 또는 시스템 패키지 또는 NLTK 데이터 누락 | §1 **시스템 패키지** 박스 설치 → `uv sync` 재실행 → 커널 재시작. 폐쇄망이면 §6의 NLTK 반입까지 완료 |
