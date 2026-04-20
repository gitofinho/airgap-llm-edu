# Day 2 — 폐쇄망 LLM 심화 과정

## 세션 구성

```
session3_advanced_graphrag/   고급 RAG 패턴
├── 01_hybrid_ensemble.ipynb           BM25 + Dense hybrid · RRF (1단계: recall)
├── 02_reranking.ipynb                 Cross-Encoder · BGE Reranker (2단계: precision)
├── 03_query_transform.ipynb           Multi-Query · HyDE · Step-back
├── 04_contextual_compression.ipynb    LLM 기반 컨텍스트 압축
├── 05_self_crag_langgraph.ipynb       Self-RAG / CRAG (LangGraph 상태 머신)
├── 07_agentic_rag.ipynb               Agentic RAG (도구 호출 + 라우팅)
└── 08_adaptive_rag.ipynb              Adaptive RAG (질의 유형별 전략)

session4_security_webservice/  보안 · 웹서비스 배포
├── 01_regulations_architecture.ipynb  망분리 · 전자금융감독규정 배포 아키텍처
├── 02_pii_and_guardrails.ipynb        Presidio PII 마스킹 · 가드레일
└── 04_custom_service_fastapi_gradio.ipynb  FastAPI + Gradio 서비스화
```

---

## 30분 사전 지식 요약

본 과정은 아래 개념들을 전제로 진행합니다. 각 항목은 **Day 2 수강에 필요한 최소한**만 요약했습니다.

### 1. LCEL (LangChain Expression Language) — 5분

LangChain 체인을 파이프 연산자로 조립하는 표준 문법.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

prompt = ChatPromptTemplate.from_template("질문: {q}\n컨텍스트: {ctx}")
chain = (
    RunnableParallel(q=RunnablePassthrough(), ctx=retriever)   # 병렬 입력 구성
    | prompt                                                   # 프롬프트 포맷
    | llm                                                      # LLM 호출
    | StrOutputParser()                                        # 문자열로 파싱
)
chain.invoke("전자금융사고 발생 시 보고 기한은?")
```

핵심 3가지:
- **`|` (파이프)**: 앞 단계 출력이 뒷 단계 입력이 된다.
- **`RunnableParallel`**: 여러 입력 필드를 동시에 준비한다 (ex. 원 질문 + 검색된 컨텍스트).
- **`.assign()`**: 기존 dict에 키를 누적한다 (ex. `RunnablePassthrough.assign(ctx=retriever)`).

### 2. 벡터스토어 기본 (Chroma · MMR) — 5분

본 과정의 Day 2 노트북들은 대부분 Chroma에 한국어 코퍼스를 색인해 MMR 검색을 쓴다.

```python
from langchain_chroma import Chroma
from common import get_embeddings

vs = Chroma.from_documents(docs, embedding=get_embeddings(), persist_directory="./_store/x")
retriever = vs.as_retriever(search_type="mmr", search_kwargs={"k": 4, "fetch_k": 20})
```

핵심 개념:
- **persist_directory**: 벡터 인덱스를 디스크에 저장 → 재실행 시 재색인 불필요.
- **MMR (Maximum Marginal Relevance)**: 유사도만 보지 않고 **다양성**도 확보해 중복 청크를 줄인다.
- **메타데이터 필터링**: `vs.similarity_search(q, filter={"article": "제21조"})` 처럼 조항 단위 제약 가능.

### 3. ReAct Agent + MemorySaver — 5분

S3-7(Agentic RAG), S3-8(Adaptive RAG), S4-4(서비스화)에서 사용.

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_react_agent(llm, tools=[search_tool, calc_tool], checkpointer=MemorySaver())
agent.invoke(
    {"messages": [("user", "전자금융사고 보고 기한 알려줘")]},
    config={"configurable": {"thread_id": "user-42"}},
)
```

핵심:
- **ReAct 루프**: LLM이 "생각(Reason) → 도구 호출(Act) → 관찰(Observe)"을 반복하다 최종 답을 낸다.
- **MemorySaver**: `thread_id`별로 대화 상태를 보관 → 멀티턴 대화 복원 가능.
- 본 과정에서는 이 구조 위에 **질의 라우팅·self-reflection·조건 분기**를 얹는다.

### 4. 한국어 토큰화 특성 — 3분

한국어는 영어보다 1.3~2.5배 더 많은 토큰을 소비한다 (OpenAI 토크나이저 기준). 비용·레이턴시 논의의 전제.

- 짧은 청크(300~500 토큰)는 한국어에서 의미 단위가 깨지기 쉬우므로, **Reranker / Query Transform**이 중요해진다.
- `common/ko_tokenizer.py`에 한국어 친화 tokenize 헬퍼가 준비되어 있다.

### 5. 도메인 맥락 — 전자금융감독규정 · 표준약관 — 2분

본 과정의 모든 RAG 예제는 **전자금융감독규정**(또는 전자금융 표준약관)을 타겟으로 한다.

- 해당 규정은 조(條) 단위 구조가 뚜렷해 조항별 청킹이 자연스럽다.
- **인용(citation) 필수**: 금융 도메인 특성상 LLM 답변은 `[근거: 제○조]` 형태로 출처를 붙이는 패턴을 사용한다.
- 코퍼스 파일: `data/corpus_ko.txt` (공유 자산).

---

## 실행 체크리스트

1. **환경**:
   ```bash
   uv sync            # Python 3.11 + 모든 의존성
   cp .env.example .env
   # .env 에 OPENAI_API_KEY 입력
   ```
2. **Neo4j** (S4-1 에서 아키텍처 참고 수준으로만 사용):
   ```bash
   docker-compose up -d neo4j   # 필요시
   ```
3. **공용 자산 확인** (모두 레포에 포함되어 있음):
   - `common/` — LLM/임베딩 provider 추상화 (`get_chat_model`, `get_embeddings`)
   - `data/corpus_ko.txt` — 전자금융 표준약관 코퍼스
   - `data/pii_samples.jsonl` — S4-2 PII 테스트셋
4. **Jupyter 기동**:
   ```bash
   uv run jupyter lab
   ```

모든 Day 2 노트북은 `common/` + `data/` 만 사용하며 노트북 내부에서 필요한 데이터·벡터스토어를 즉석 구축하므로, 별도 선행 실행 없이 단독으로 돌아간다.

## 참고

- 환경·오프라인 반입 절차: [`SETUP.md`](../SETUP.md)
- 루트 가이드: [`../README.md`](../README.md)
