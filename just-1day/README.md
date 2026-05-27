# Just 1-Day · 폐쇄망 LLM 강의 (1일 압축 트랙)

`day1` / `day2` 2일 커리큘럼을 **하루 안에 핵심만 짚고 캡스톤까지** 끝낼 수 있도록 재구성한 트랙입니다. 노트북은 위에서 아래로 한 줄로 따라가면 됩니다.

## 학습 순서

| # | 노트북 | 단계 | 핵심 |
|---|---|---|---|
| 01 | `01_loader_chunking.ipynb` | 데이터 준비 | PDF/DOCX/HWPX 로더 · 4가지 청킹 전략 |
| 02 | `02_langchain_prompt_basics.ipynb` | LangChain 기초 | Prompt · Few-shot · LCEL · Output Parser |
| 03 | `03_vectorstore_comparison.ipynb` | 벡터 검색 | Chroma / FAISS / Qdrant 비교 |
| 04 | `04_retriever_patterns.ipynb` | 벡터 검색 | similarity / MMR / threshold · 메타필터 · 멀티테넌트 |
| 05 | `05_hybrid_ensemble.ipynb` | 검색 고도화 | BM25 + Dense + RRF (2-stage retrieval 1단계) |
| 06 | `06_reranking.ipynb` | 검색 고도화 | Cross-encoder reranker (2-stage retrieval 2단계) |
| 07 | `07_rag_pipeline_lcel.ipynb` | 통합 | 전자금융감독규정 PDF 풀 RAG 체인 · 캡스톤 베이스라인 산출 |
| 08 | `08_eval_ragas.ipynb` | 평가 (옵션) | RAGAS 4지표로 베이스라인 진단 |
| 09 | `09_agent_and_langgraph.ipynb` | 에이전트 | ReAct · `create_react_agent` · `MemorySaver` |
| 10 | `10_streamlit_capstone.ipynb` | 캡스톤 | Streamlit + LangGraph Agent + RAG 도구 |

## 의존성 (산출물 흐름)

```
07_rag_pipeline_lcel
  ├─ _store/efinance_rag/              ← Chroma 인덱스
  │     └─ 09_agent_and_langgraph 가 도구로 재사용
  │     └─ 10_streamlit_capstone 이 앱에서 재사용
  └─ _capstone_baseline.json           ← 5개 질의의 답변·컨텍스트
        └─ 08_eval_ragas 가 RAGAS 평가 입력으로 로드
```

**최소 실행 경로**: 07 → 09 → 10 (RAG → Agent → 앱)
**평가 포함 경로**: 07 → 08 → 09 → 10

03·04·05는 각자 별도의 작은 `_store/` 인덱스를 만들어 쓰지만, 다른 노트북과 산출물을 공유하지 않는 독립 실습입니다.

## 입력 데이터

상위 `../data/` 폴더의 파일을 그대로 사용합니다.

- `../data/corpus_ko.txt` — 한국어 코퍼스 (03, 05, 06에서 사용)
- `../data/pdf/sample_compliance.docx` — DOCX 로더 데모용 (01)
- `../data/pdf/전자금융감독규정(금융위원회고시)(제2026-7호)(20260213).pdf` — 메인 도메인 문서 (07)
- `../data/pdf/전자금융거래법(법률)(제21205호)(20251216).hwpx` — HWPX 로더 데모용 (01)

## 노트북이 만들어내는 파일

모두 `.gitignore`로 제외되어 있습니다. 처음부터 다시 만들고 싶으면 폴더째 지우고 07부터 다시 실행하면 됩니다.

- `_store/` — Chroma / FAISS 인덱스 모음
- `_capstone_baseline.json` — 07이 산출, 08이 소비
- `app.py` — 10이 `%%writefile`로 생성하는 Streamlit 앱
