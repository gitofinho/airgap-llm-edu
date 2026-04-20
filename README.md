## 수강 전 준비

1. **환경 구축** — [SETUP.md](SETUP.md)의 Python 3.11, Docker Desktop 설치
2. **계정** — `OPENAI_API_KEY` (OpenRouter 권장, Day 1~Day 2 전반), LangSmith 계정(무료, 선택)

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
day2/         Day 2 심화 과정 노트북 (13개, 🧩 심화 2개 포함) — 단독 수강 가능, [day2/README.md](day2/README.md) 참조
data/         샘플 PDF·코퍼스·KG·PII 테스트셋
assets/       다이어그램·시각화 이미지
```

> **Day 2만 수강하는 분**은 [`day2/README.md`](day2/README.md)의 "30분 사전 지식 요약" 섹션부터 시작하세요. Day 1 없이도 세션 3~4가 독립적으로 돌아가도록 구성되어 있습니다.