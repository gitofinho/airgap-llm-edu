# RAG 파이프라인 비교 (기본 → Advanced → GraphRAG)

## 1. 기본 RAG (Day 1 S2)

```mermaid
flowchart LR
    Q[질문] --> E[임베딩]
    E --> V[(벡터스토어)]
    V -->|top-k| C[컨텍스트]
    C --> P[프롬프트]
    Q --> P
    P --> L[LLM]
    L --> A[답변]
```

## 2. Advanced RAG (Day 2 S3) — Hybrid + Rerank + Query Transform

```mermaid
flowchart LR
    Q[질문] --> QT[쿼리 변환\nHyDE/Multi-Query]
    QT --> BM[BM25 검색]
    QT --> DENSE[Dense 검색]
    BM --> RRF[RRF 결합]
    DENSE --> RRF
    RRF -->|top-100| RR[Reranker\nBGE-v2-m3]
    RR -->|top-10| P[프롬프트]
    Q --> P
    P --> L[LLM]
    L --> A[답변]
```

## 3. Self-RAG / CRAG (LangGraph 상태기계)

```mermaid
stateDiagram-v2
    [*] --> retrieve
    retrieve --> grade_docs
    grade_docs --> relevant: 관련성 OK
    grade_docs --> rewrite: 관련성 부족
    rewrite --> retrieve
    relevant --> generate
    generate --> verify
    verify --> [*]: 충실성 OK
    verify --> rewrite: 환각 탐지
```

## 4. GraphRAG (Day 2 S3-6)

```mermaid
flowchart LR
    DOC[원문] --> LGT[LLMGraphTransformer]
    LGT --> KG[(Neo4j 지식그래프)]
    Q[자연어 질문] --> CQG[Cypher 생성기\nLLM]
    CQG --> KG
    KG -->|노드+관계| CTX[컨텍스트]
    CTX --> P[프롬프트]
    Q --> P
    P --> L[LLM]
    L --> A[답변]
```
