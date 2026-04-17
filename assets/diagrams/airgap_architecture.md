# 폐쇄망 LLM 서비스 참조 아키텍처

## 1. 망분리 기반 3계층 구조

```mermaid
flowchart LR
    subgraph INTERNET["🌐 인터넷망"]
        U[외부 사용자/연구자]
        CHAT[Claude / GPT\nSaaS]
        HF[HuggingFace\n모델 다운로드]
    end

    subgraph DMZ["🔸 DMZ (자료전송 구간)"]
        PROXY[보안 프록시\n정보통신망 이용촉진법]
        SCAN[악성코드 스캔]
        APPROVAL[반입 승인\n전자결재]
    end

    subgraph INTRANET["🔒 내부망 (폐쇄망)"]
        EMP[내부 임직원]
        WEBUI[OpenWebUI\nRBAC + 감사로그]
        VLLM[vLLM / Ollama\nqwen2.5:7b]
        RAG[RAG 서비스\nChroma/FAISS]
        KG[Neo4j\nGraphRAG]
        AUDIT[SIEM / 감사로그]
    end

    HF -.반입.-> SCAN
    CHAT -.대조 실험만.-> APPROVAL
    SCAN --> APPROVAL
    APPROVAL -.승인 후.-> VLLM

    EMP --> WEBUI
    WEBUI --> VLLM
    WEBUI --> RAG
    RAG --> VLLM
    RAG --> KG
    WEBUI --> AUDIT
    VLLM --> AUDIT
```

## 2. 데이터 흐름 (학습/운영 분리)

```mermaid
sequenceDiagram
    participant U as 사용자
    participant G as 게이트웨이\n(Guardrails)
    participant R as RAG 리트리버
    participant V as 벡터/그래프 DB
    participant L as LLM (Ollama/vLLM)
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

## 3. 모델/패키지 반입 절차

```mermaid
flowchart TD
    A[외부망\nollama pull] --> B[GGUF 파일\nSHA256 계산]
    B --> C[승인 신청\n(모델명, 용도, 책임자)]
    C --> D{승인}
    D -->|거절| X[반입 중단]
    D -->|승인| E[USB/전송매체]
    E --> F[DMZ 스캐너\n악성코드 검사]
    F --> G[내부망 Ollama 서버\nSHA256 재검증]
    G --> H[Modelfile 등록]
    H --> I[운영 배포]
```
