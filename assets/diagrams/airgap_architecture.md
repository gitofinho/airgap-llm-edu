# LLM 서비스 참조 아키텍처 (OpenRouter 경유 OpenAI)

## 1. 구성 계층

```mermaid
flowchart LR
    subgraph CLIENT["👥 사용자"]
        U[내부 사용자]
    end

    subgraph APP["💠 애플리케이션"]
        GW[게이트웨이\n(Guardrails + 감사)]
        RAG[RAG 서비스\nChroma/FAISS]
        KG[Neo4j\nGraphRAG]
    end

    subgraph CLOUD["☁️ OpenAI / OpenRouter"]
        LLM[ChatOpenAI\nopenai/gpt-4o-mini]
        EMB[Embeddings\ntext-embedding-3-small]
    end

    U --> GW
    GW --> RAG
    RAG --> LLM
    RAG --> KG
    RAG --> EMB
    GW --> LLM
```

## 2. 데이터 흐름 (질의 → 응답)

```mermaid
sequenceDiagram
    participant U as 사용자
    participant G as 게이트웨이\n(Guardrails)
    participant R as RAG 리트리버
    participant V as 벡터/그래프 DB
    participant L as LLM (OpenAI / OpenRouter)
    participant A as 감사로그

    U->>G: 질문 (PII 포함 가능)
    G->>G: PII 탐지·마스킹 (Presidio)
    G->>G: 프롬프트 인젝션 필터 (NeMo)
    G->>R: 정화된 질문
    R->>V: 유사도·Cypher 검색
    V-->>R: 근거 문서/노드
    R->>L: context + 질문
    L-->>R: 답변
    R->>G: 답변 + citations
    G->>G: 출력 정책 검증
    G-->>U: 최종 응답
    G->>A: {질문, 근거, 응답, PII 플래그}
```

## 3. 환경변수 연결

| 변수 | 용도 |
|---|---|
| `OPENAI_API_KEY` | OpenAI 또는 OpenRouter API 키 |
| `OPENAI_API_BASE` | OpenRouter 사용 시 `https://openrouter.ai/api/v1` |
| `OPENAI_MODEL` | `openai/gpt-4o-mini` 같은 모델 경로 |
| `OPENAI_EMBEDDING_MODEL` | `openai/text-embedding-3-small` |
