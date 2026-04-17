# 환경 구축 가이드 (uv 기반)

## 1. 필수 소프트웨어

| 항목 | 버전 | 용도 |
|------|------|------|
| [uv](https://docs.astral.sh/uv/) | 최신 | Python·의존성 일괄 관리 (권장 경로) |
| Python | 3.11 | uv가 자동 설치하므로 별도 설치 불필요 |
| Docker Desktop | 최신 | Neo4j(S3-6), OpenWebUI+Ollama(S4-3) |
| Git | 2.40+ | 교안 clone |
| (선택) Ollama | 최신 | S4-5 Airgap 전환 시연 — Docker 이미지로 대체 가능 |

### uv 설치 (30초)
```bash
# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```
설치 후 새 터미널에서 `uv --version` 확인.

### Docker Desktop
- Windows: WSL2 백엔드 권장
- macOS: 공식 설치 프로그램

### Ollama (S4 전용 — Docker 대체 가능)
- Windows/macOS: https://ollama.com/download
- 또는 `docker compose -f docker-compose.openwebui.yml up` 로 컨테이너 실행

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

`.env` 수정:
```bash
OPENAI_API_KEY=sk-...            # Day 1~Day 2 전반 필수
LLM_PROVIDER=openai              # Day 2 S4-5에서 ollama 로 변경
EMBEDDING_PROVIDER=openai        # S4-5에서 local 로 변경

LANGCHAIN_TRACING_V2=false       # LangSmith 사용 시 true
LANGCHAIN_API_KEY=

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct
```

---

## 4. Docker 서비스

### Day 2 S3-6 — Neo4j
```bash
docker compose up -d neo4j
# http://localhost:7474  (neo4j / password)
```

### Day 2 S4-3 — OpenWebUI + Ollama
```bash
docker compose -f docker-compose.openwebui.yml up -d
# http://localhost:3000
docker exec airgap-ollama ollama pull qwen2.5:7b-instruct
```

### 종료
```bash
docker compose down
docker compose -f docker-compose.openwebui.yml down
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
```

Ollama 모델은 `ollama pull` 후 `~/.ollama/models/` 전체를 복사하거나 GGUF 파일 + Modelfile로 반입합니다 (자세한 절차는 `day2/session4_security_webservice/03_openwebui_ollama.md` 참고).

---

## 7. 문제 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| `uv: command not found` | PATH 미반영 | 새 터미널 열기, 또는 `~/.local/bin`을 PATH에 추가 |
| `uv sync` 느림 | 초회 다운로드 | 두 번째부터는 캐시 사용, 수 초 이내 |
| OpenAI 401 | `.env` 미로드 | 노트북 커널 재시작 후 첫 셀 실행 (common/llm.py가 `load_dotenv()`) |
| Neo4j 연결 실패 | 컨테이너 미기동 | `docker ps`, `docker compose up -d neo4j` |
| Ollama `connection refused` | 서비스 미기동 | Windows: Ollama Desktop 실행, 또는 Docker Compose 사용 |
| faiss-cpu 설치 실패 (Windows) | wheel 없음 | `uv add faiss-cpu --python-downloads never` 후 재시도 또는 Chroma만 사용 |
| 한글 폰트 깨짐 (matplotlib) | 한글 폰트 없음 | 노트북 1-1 첫 셀 참고 (Malgun Gothic / AppleGothic) |
