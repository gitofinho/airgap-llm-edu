# Day 2 — 폐쇄망 LLM 심화 과정

## 노트북 구성

| # | 파일 | 내용 |
|---|------|------|
| 01 | [`01_hybrid_ensemble.ipynb`](01_hybrid_ensemble.ipynb) | BM25 + Dense hybrid · RRF (recall 확보) |
| 02 | [`02_reranking.ipynb`](02_reranking.ipynb) | Cross-encoder · BGE Reranker (precision 확보) |
| 03 | [`03_langgraph_basic.ipynb`](03_langgraph_basic.ipynb) | LangGraph 기초 — State · Node · Edge · 조건부 엣지 |
| 04 | [`04_naive_rag_relevance.ipynb`](04_naive_rag_relevance.ipynb) | LangGraph로 Naive RAG 조립 + 관련성 체크 (무한 루프 시연) |
| 05 | [`05_self_rag_langgraph.ipynb`](05_self_rag_langgraph.ipynb) | Self-RAG — `grade → rewrite` 로 자가교정 루프 구현 |
| 06 | [`06_adaptive_rag.ipynb`](06_adaptive_rag.ipynb) | Adaptive RAG — 쿼리 복잡도 라우터로 경로 분기 |

## 학습 흐름

```
01·02 (검색 품질)        03 (워크플로 문법)        04·05·06 (RAG 그래프)
Hybrid → Rerank    →    State/Node/Edge     →    Naive → Self-RAG → Adaptive
recall + precision       LangGraph 기초           자가교정·라우팅
```

- **01·02** : 2-stage retrieval 로 "정답이 후보에 들어오게(recall) + 꼭대기에 올라오게(precision)" 만든다.
- **03** : 04·05·06의 공통 뼈대인 LangGraph 문법(State·Node·Edge·조건부 엣지·ToolNode)만 순수하게 학습.
- **04** : 03을 실제 RAG에 적용해 "retrieve → 관련성 체크 → 답변" 그래프를 만들고, **일부러 무한 루프**를 재현해 왜 05가 필요한지 체감한다.
- **05** : `rewrite_query` 노드 하나로 04의 루프를 깬다 — 검색 *후* 재시도 패턴(Self-RAG).
- **06** : 시점을 앞당겨 검색 *전* 에 경로를 분류한다(Adaptive RAG). 단일 경로 안에서는 05 의 `grade → rewrite` 를 그대로 재활용한다.

모든 노트북은 **단독 실행 가능**하다. 필요한 인덱스·벡터스토어는 각자 노트북 내부에서 `data/corpus_ko.txt` 를 로드해 즉석 구축하므로, 선행 노트북을 먼저 돌릴 필요가 없다.

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

### 2. 벡터스토어 기본 (Chroma · FAISS · MMR) — 5분

본 과정의 Day 2 노트북들은 FAISS(01·02·03·04·05) 또는 Chroma(06)에 한국어 코퍼스를 색인해 쓴다.

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

### 3. LangGraph · 구조화 출력 — 5분

03~06 에서 전면적으로 사용.

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    question: str
    answer: str

def node(state: State) -> dict:
    return {"answer": llm.invoke(state["question"])}

g = StateGraph(State)
g.add_node("answer", node)
g.add_edge(START, "answer")
g.add_edge("answer", END)
app = g.compile()
```

핵심:
- **State · Node · Edge** — 03에서 본격적으로 다룬다.
- **조건부 엣지 (`add_conditional_edges`)** — 라우터 함수가 반환하는 라벨로 다음 노드를 선택. 04·05·06 전부의 심장.
- **구조화 출력 (`llm.with_structured_output(Pydantic)`)** — 06 쿼리 라우터에서 사용.

### 4. 한국어 토큰화 특성 — 3분

한국어는 영어보다 1.3~2.5배 더 많은 토큰을 소비한다 (OpenAI 토크나이저 기준). 비용·레이턴시 논의의 전제.

- 짧은 청크(300~500 토큰)는 한국어에서 의미 단위가 깨지기 쉬우므로, **Reranker / Query Transform**이 중요해진다.
- `common/ko_tokenizer.py`에 한국어 친화 `tokenize_ko` 헬퍼(kiwi 기반)가 준비되어 있다 — 01의 BM25에서 바로 사용.

### 5. 도메인 맥락 — 전자금융 표준약관 — 2분

본 과정의 모든 RAG 예제는 **전자금융 표준약관 / 감독규정**을 타겟으로 한다.

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
2. **공용 자산 확인** (모두 레포에 포함되어 있음):
   - `common/` — LLM/임베딩 provider 추상화 (`get_chat_model`, `get_embeddings`)
   - `data/corpus_ko.txt` — 전자금융 표준약관 코퍼스
3. **Jupyter 기동**:
   ```bash
   uv run jupyter lab
   ```

모든 Day 2 노트북은 `common/` + `data/` 만 사용하며 노트북 내부에서 필요한 데이터·벡터스토어를 즉석 구축하므로, 별도 선행 실행 없이 단독으로 돌아간다.

## 참고

- 환경·오프라인 반입 절차: [`SETUP.md`](../SETUP.md)
- 루트 가이드: [`../README.md`](../README.md)
