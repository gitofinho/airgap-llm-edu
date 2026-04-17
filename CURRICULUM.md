# 상세 커리큘럼

각 노트북 상단에는 ⏱ 소요시간이 명시되어 있으며, 일부 셀은 `<!-- optional -->` 마커로 생략 가능합니다.

---

## Day 1 — 기초 과정 (5h)

### Session 1 · LLM 기초 (2.5h)

#### 1-1. Transformer와 Attention (60m)
- **학습목표**: Self-Attention의 Q/K/V 계산을 스크래치로 구현하고, MHA/MQA/GQA·Positional Encoding·KV Cache의 동기를 설명할 수 있다.
- **핵심 키워드**: Scaled Dot-Product Attention, Causal Mask, Multi-Head, MQA/GQA, Sinusoidal/RoPE/ALiBi, KV Cache
- **실습**: NumPy로 단일 head attention → multi-head 확장 → HuggingFace `bert-base-multilingual-cased` attention 행렬 시각화

#### 1-2. 토큰화 심화 (45m)
- **학습목표**: BPE/WordPiece/SentencePiece 원리를 이해하고, 모델별 한국어 토큰 효율을 측정할 수 있다.
- **핵심 키워드**: BPE, WordPiece, SentencePiece, 어휘 크기, OOV, subword
- **실습**: `tiktoken`으로 영/한 토큰 수 비교, Llama3/Qwen2.5/Ko-BPE 벤치마크

#### 1-3. 임베딩 심화 (30m)
- **학습목표**: Static→Contextual→Sentence 임베딩의 진화와 유사도 계산 차이를 설명할 수 있다.
- **핵심 키워드**: word2vec, BERT CLS, SBERT, SimCSE, MTEB-ko, cosine/dot/L2
- **실습**: `sentence-transformers`로 `bge-m3`·`ko-sroberta`·`multilingual-e5` 비교

#### 1-4. LLM API와 추론 (15m)
- **학습목표**: LangChain `ChatOpenAI` 기본 사용과 샘플링 파라미터·비용 계산을 할 수 있다.
- **핵심 키워드**: temperature, top_p, streaming, function calling, context window
- **실습**: OpenAI + LangChain 스트리밍, 토큰 비용 계산

### Session 2 · RAG 기본 (2.5h)

#### 2-1. 문서 로더와 청킹 (45m)
- PDF/DOCX/HWP 로더 비교, Recursive·Semantic·Markdown-aware·Token 분할 비교, 한국어 문장 분할기 `kss`/`kiwi`

#### 2-2. 벡터스토어 비교 (30m)
- Chroma·FAISS·Qdrant(self-host) 🔒 비교, HNSW 파라미터 튜닝

#### 2-3. 리트리버 패턴 (30m)
- similarity·MMR·threshold, 메타데이터 필터링, 멀티테넌트 격리

#### 2-4. LCEL RAG 파이프라인 (30m)
- 엔드투엔드 체인, citations, 전자금융 표준약관 Q&A (캡스톤 시드)

#### 2-5. RAGAS 평가 (15m)
- faithfulness, answer relevancy, context precision/recall, LangSmith/LangFuse 로깅

#### 2-6. LLM-as-a-Judge 심화 (30m) 🧩 심화/선택
- Single-answer / Pairwise / Reference-based(G-Eval) 세 가지 판사 패턴
- Position·verbosity 편향과 완화 기법 (순서 교차, 앙상블)
- RAGAS 고급 지표 (AnswerCorrectness, ContextEntityRecall, NoiseSensitivity)
- 폐쇄망 환경에서 local judge 사용 시 주의사항

---

## Day 2 — 심화 과정 (5h)

### Session 3 · Advanced RAG + GraphRAG (2.5h)

#### 3-1. 재순위화 (25m)
- Cross-encoder 원리, BGE-reranker-v2-m3(🔒) vs Cohere(☁️), 2-stage 검색

#### 3-2. 하이브리드·앙상블 검색 (25m)
- BM25+Dense RRF, Ensemble Retriever, 한국어 BM25(kiwi)

#### 3-3. 쿼리 변환 (30m)
- HyDE, Multi-Query, Step-Back, RAG-Fusion, Query Decomposition

#### 3-4. 컨텍스트 압축 (15m)
- LLMChainExtractor, Parent-Child, Small-to-Big, Contextual Retrieval

#### 3-5. Self-RAG / CRAG (30m)
- LangGraph 상태 기계로 자가교정 RAG 구현

#### 3-6. GraphRAG (45m)
- Neo4j + LLMGraphTransformer, Microsoft GraphRAG의 community detection·local vs global, Vector RAG와 비교

#### 3-7. Agentic RAG (35m) 🧩 심화/선택
- LLM이 도구를 호출하며 검색 여부·횟수를 스스로 결정
- LangGraph ReAct 패턴, tool-calling 에이전트 구현
- 검색 폭주 방지(max_iterations)와 감사 관점의 trace 기록

#### 3-8. Adaptive RAG (30m) 🧩 심화/선택
- 쿼리 복잡도 분류기로 `no_retrieval / single / multi-hop` 경로 분기
- LangGraph conditional_edges로 상태 기계 구현
- Agentic vs Adaptive 비교, "언제 어느 기법" 의사결정 트리

### Session 4 · 보안·규제 + 웹서비스 + Airgap (2.5h)

#### 4-1. 규제와 망분리 아키텍처 (30m)
- 개보법·신용정보법·전자금융감독규정, 금감원 AI 가이드라인, Mermaid 아키텍처

#### 4-2. PII 마스킹 & Guardrails (30m)
- Presidio + 한국어 커스텀 인식기, OWASP LLM Top10, NeMo Guardrails/Llama Guard, 감사로그

#### 4-3. OpenWebUI + Ollama (45m)
- Docker Compose, RBAC, 내장 RAG, 폐쇄망 반입 절차

#### 4-4. 커스텀 서비스 (FastAPI + Gradio) (30m)
- SSE 스트리밍, OpenAI 호환 프록시, 인증 미들웨어

#### 4-5. Airgap 전환 (15m)
- `.env` 스위칭으로 2-4·3-5 로컬 재실행, vLLM 소개
