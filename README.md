# 폐쇄망 LLM 실무 2일 집중 과정

국내 금융·공공 폐쇄망(airgap) 환경에서 LLM을 도입·운영하려는 **수준 높은 실무 개발자** 대상 교안입니다.
[langchain-kr](https://github.com/teddylee777/langchain-kr) 스타일을 참고하되, Advanced RAG·GraphRAG·보안·OpenWebUI·Airgap 전환은 직접 작성했습니다.

## 일정표 (총 10시간)

| Day | 세션 | 시간 | 주제 |
|-----|------|------|------|
| Day 1 | Session 1 (기초) | 2.5h | LLM 기초 — Transformer·Attention·토큰화·임베딩·Agent |
| Day 1 | Session 2 (심화) | 2.5h | RAG 기본 — 로더·분할·벡터스토어·검색·LCEL·RAGAS |
| Day 2 | Session 3 (기초) | 2.5h | Advanced RAG + GraphRAG |
| Day 2 | Session 4 (심화) | 2.5h | 보안·규제 + 웹서비스(OpenWebUI) + Airgap 전환 |

## 수강 전 준비

1. **환경 구축** — [SETUP.md](SETUP.md)의 Python 3.11, Docker Desktop, (선택) Ollama 설치
2. **계정** — `OPENAI_API_KEY` (Day 1~Day 2 전반), LangSmith 계정(무료, 선택)
3. **하드웨어** — Day 2 Ollama 시연 시 최소 16GB RAM 권장 (양자화 모델 기준)

## 사용 방법 (uv 기반 — 3줄)

```bash
# 0. uv 설치 (30초, 최초 1회)
# Windows:  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS:    curl -LsSf https://astral.sh/uv/install.sh | sh

# 1. 의존성 동기화 (Python 3.11 자동 설치 + 전 패키지 설치)
uv sync

# 2. 환경변수
cp .env.example .env   # Windows: copy .env.example .env
# .env에 OPENAI_API_KEY 입력

# 3. Jupyter 실행
uv run jupyter lab
```

자세한 셋업·트러블슈팅은 [SETUP.md](SETUP.md). 폐쇄망 오프라인 반입 절차 포함.

## 디렉터리

```
common/       provider 추상화·한국어 로더·토크나이저
day1/         Day 1 기초 과정 노트북 (10개, 🧩 심화 1개 포함)
day2/         Day 2 심화 과정 노트북 (13개, 🧩 심화 2개 포함)
data/         샘플 PDF·코퍼스·KG·PII 테스트셋
assets/       다이어그램·시각화 이미지
```

> 🧩 **심화/선택** 마커가 붙은 노트북(LLM-as-judge, Agentic RAG, Adaptive RAG)은 시간 여유나 과제용으로 활용합니다.

## 캡스톤: 전자금융 표준약관 챗봇

S1(토큰 분석) → S2(기본 RAG) → S3(고급 검색 + GraphRAG 비교) → S4(OpenWebUI 배포 + Airgap 전환)로 **한 가지 주제를 누적 고도화**하며 배웁니다.

## 참고 자료

- [langchain-kr](https://github.com/teddylee777/langchain-kr)
- [LangChain 공식 문서](https://python.langchain.com/)
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- 금감원 ["금융분야 AI 활용 안내서"](https://www.fss.or.kr/)
- 개인정보보호위원회 ["AI 개인정보보호 자율점검표"](https://www.pipc.go.kr/)
