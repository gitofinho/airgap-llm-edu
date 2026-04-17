# 강사용 가이드

## 전체 페이스

| 세션 | 목표 페이스 | 버퍼 |
|------|-------------|------|
| S1 (LLM 기초) | 1-1 Attention에 60분, 남은 90분에 토큰화·임베딩·API | 1-1이 60분 초과하지 않도록 시각화 셀 생략 가능 |
| S2 (RAG 기본) | 2-1~2-5 각 셀 순차 | 2-5 RAGAS는 `<!-- optional -->`로 생략 가능 |
| S3 (Advanced/GraphRAG) | 3-1~3-5에 105분, 3-6 GraphRAG에 45분 | 3-4 Contextual Compression 생략 가능 |
| S4 (보안/웹/Airgap) | 4-1·4-2에 60분, 4-3 OpenWebUI 45분, 4-4·4-5 45분 | 4-4 Gradio 데모는 스크린샷 공유로 대체 가능 |

## 자주 나오는 질문 & 답변

### S1
- **Q: RoPE가 왜 절대 위치보다 좋은가?**
  - A: 상대 위치 정보를 쿼리·키 내적에 직접 인코딩하여 긴 컨텍스트 외삽이 쉬움. Llama 계열이 채택.
- **Q: 한국어가 영어보다 토큰을 많이 쓰는 이유?**
  - A: 다국어 BPE가 한글을 바이트/자소 단위로 쪼개는 경우가 많음. Ko-BPE·Qwen2.5는 한국어 어휘를 더 많이 포함.

### S2
- **Q: Chroma vs FAISS, 어느 쪽을 추천?**
  - A: 영구 저장·메타데이터 필터가 필요하면 Chroma. 단순 속도·대용량·오프라인이면 FAISS. 운영급은 Qdrant self-host.
- **Q: 청크 크기 어떻게 정하나?**
  - A: 임베딩 모델 학습 길이(대개 512 토큰 내외)를 넘지 않도록. 한국어는 문자가 아니라 토큰 기준으로 측정.

### S3
- **Q: GraphRAG는 Vector RAG를 대체하나?**
  - A: 아님. 개체 간 관계·다단계 추론·요약 질문에 유리. 사실조회형은 Vector RAG가 더 싸고 빠름. **하이브리드** 구성이 실제 현장에 많음.
- **Q: Self-RAG 구현에 LangGraph가 필수인가?**
  - A: 아니지만 상태·반복·분기를 표현하기에 가장 적합. RunnableGraph로도 가능.

### S4
- **Q: 폐쇄망에서 모델 업데이트는?**
  - A: 허가된 반입 절차(외부망 다운로드 → 승인 → DMZ 경유 → 내부망 복사). 모델 무결성(SHA256) 검증 필수.
- **Q: OpenWebUI는 감사 요구사항을 만족하나?**
  - A: 기본 로그 + pipelines 훅으로 요청/응답 감사 가능. 별도 SIEM 연동은 reverse proxy(nginx) 레벨에서 구성 권장.

## 디버깅 팁

- `OPENAI_API_KEY`가 로드되지 않으면 노트북 최상단에 `from dotenv import load_dotenv; load_dotenv()` 실행 확인.
- Neo4j 연결 실패 → `docker logs airgap-neo4j`로 초기화 완료(약 30초) 대기 확인.
- Ollama 모델 pull이 느리면 미리 `ollama pull qwen2.5:7b-instruct` 실행 후 시연.
- 윈도우에서 `faiss-cpu` 설치 실패 시 Chroma 경로만 진행 (노트북에 분기 처리).

## 리허설 체크리스트

- [ ] 전체 노트북 `jupyter nbconvert --execute` 회귀 완료
- [ ] OpenWebUI Docker 기동 + PDF 업로드 시연 확인
- [ ] `.env` 한 줄 변경으로 2-4·3-5 Airgap 재실행 확인
- [ ] 각 세션 2.5h ± 15분 수렴 타이밍 측정
