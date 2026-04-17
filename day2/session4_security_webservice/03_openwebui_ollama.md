# 4-3. OpenWebUI + Ollama 실습 가이드

⏱ **소요시간**: 45분
**모드**: 🔒 폐쇄망 On-prem (Ollama + OpenWebUI)

## 학습 목표

- Docker Compose로 🔒 **OpenWebUI + Ollama**를 기동하고 관리자 계정·RBAC을 구성한다.
- GGUF **양자화 수준**(Q4_K_M / Q5_K_M / Q8_0)의 메모리·품질 트레이드오프를 이해한다.
- OpenWebUI의 **워크스페이스·지식베이스(내장 RAG)·Pipelines** 기능을 실습한다.
- **폐쇄망 반입 절차**(외부망 다운로드 → 해시 검증 → 자료전송 → 내부망 로드)를 수행한다.
- Python 의존성을 **오프라인 wheel 번들**로 패키징해 내부망에서 설치한다.

## 핵심 키워드

`OpenWebUI` · `Ollama` · `GGUF` · `Q4_K_M` · `Modelfile` · `Knowledge Base` · `Pipelines` · `RBAC` · `sha256` · `자료전송시스템` · `pip download` · `--find-links`

---

## 1. Docker Compose로 기동

저장소 루트에 이미 `docker-compose.openwebui.yml`이 포함되어 있다.

```bash
# 저장소 루트에서
docker compose -f docker-compose.openwebui.yml up -d

# 상태 확인
docker compose -f docker-compose.openwebui.yml ps
docker logs airgap-ollama --tail 30
docker logs airgap-openwebui --tail 30
```

| 서비스 | 포트 | URL |
| --- | --- | --- |
| Ollama | 11434 | http://localhost:11434 |
| OpenWebUI | 3000 | http://localhost:3000 |

> 내부망 배포 시 `3000` 포트는 DMZ의 리버스 프록시(WAF/Nginx) 뒤에 두고 TLS 종단·MFA·SSO를 붙인다.

![openwebui 로그인](assets/images/openwebui_login.png)

## 2. 첫 관리자 계정 생성 & RBAC

1. 브라우저에서 `http://localhost:3000` 접속.
2. **첫 번째로 가입하는 계정이 자동으로 Admin 권한**을 받는다 → 리허설 전에 강사가 먼저 가입.
3. Admin Panel (`/admin`) → **Users** → 가입 대기 사용자 `pending` 상태를 `user` 또는 `admin`으로 승격.
4. `ENABLE_SIGNUP=false`, `DEFAULT_USER_ROLE=pending` (본 compose 기본값) → 승인 없는 가입 차단.

### 권장 역할 매트릭스

| 역할 | 권한 | 비고 |
| --- | --- | --- |
| `admin` | 전체 설정, 모델 등록, 사용자 관리 | 정보보호 담당 + 운영팀 2인 이상 |
| `user` | 모델 사용, 지식베이스 조회 | 일반 사용자 |
| `pending` | 승인 대기 | 가입 직후 기본값 |

SSO(SAML/OIDC) 연동은 `OAUTH_*` 환경변수로 구성 (Keycloak, Okta, Azure AD).

![admin users](assets/images/openwebui_admin_users.png)

## 3. 모델 다운로드 (외부망 or 사내 미러)

```bash
# Ollama 컨테이너 내부에서 pull
docker exec airgap-ollama ollama pull qwen2.5:7b-instruct
docker exec airgap-ollama ollama pull bge-m3   # 임베딩

# 리스트 확인
docker exec airgap-ollama ollama list
```

결과 예시:

```
NAME                     ID              SIZE      MODIFIED
qwen2.5:7b-instruct      abc123...       4.7 GB    2 minutes ago
bge-m3:latest            def456...       1.2 GB    1 minute ago
```

![model list](assets/images/openwebui_models.png)

## 4. GGUF 양자화 (Quantization) 이해

GGUF는 llama.cpp 계열의 단일 파일 포맷. 양자화는 모델 가중치를 정수로 압축해 메모리/속도를 얻고 약간의 품질을 잃는 기법.

| 양자화 | bit/weight | 7B 모델 크기 | 품질 손실 | 권장 용도 |
| --- | --- | --- | --- | --- |
| `F16` | 16 | ~14 GB | 없음 | 참조 성능 평가 |
| `Q8_0` | 8 | ~7.5 GB | 거의 없음 | 고품질 필요, 충분한 VRAM |
| `Q6_K` | ~6.6 | ~5.5 GB | 매우 낮음 | 균형 |
| **`Q5_K_M`** | ~5.7 | ~4.8 GB | 낮음 | 🎯 RAG/요약 등 일반 업무 |
| **`Q4_K_M`** | ~4.8 | ~4.0 GB | 보통 | 🎯 VRAM 제한 (8GB급) |
| `Q3_K_M` | ~3.9 | ~3.3 GB | 눈에 띔 | 엣지/CPU-only |
| `Q2_K` | ~3.0 | ~2.7 GB | 큼 | 시연/실험용 |

**실무 가이드**
- 금융 RAG 질의응답: **Q5_K_M** 기본, 장문 생성은 Q8_0 검토.
- VRAM 8GB 이하 랩탑 시연: **Q4_K_M**.
- 배치 작업/대량 처리: Q6_K 이상 + batching.
- 양자화 비교는 자체 벤치마크(내부 FAQ 100문항 정답률, latency p95) 필수.

Modelfile로 특정 양자화 지정:

```Dockerfile
# Modelfile
FROM qwen2.5:7b-instruct-q5_K_M
SYSTEM "당신은 폐쇄망 금융 상담 보조 LLM입니다. 개인정보를 묻지 말고, 일반 안내만 제공하세요."
PARAMETER temperature 0.2
PARAMETER num_ctx 8192
```

```bash
docker exec -i airgap-ollama ollama create kr-finance-assistant -f - < Modelfile
```

## 5. 워크스페이스 & 지식베이스(내장 RAG)

OpenWebUI는 **Knowledge**(지식베이스) 기능에 내장 RAG를 제공한다 (Chroma/pgvector 자동 구성).

1. 좌측 **Workspace** → **Knowledge** → `+ Create`.
2. 이름: `금융소비자보호법_FAQ`, 임베딩 모델: `bge-m3` (Ollama), chunk size: 500, overlap: 50.
3. PDF/MD/DOCX 업로드 → 자동 파싱 + 청킹 + 임베딩.
4. Chat에서 `#금융소비자보호법_FAQ` 로 멘션하면 해당 KB가 컨텍스트로 주입된다.

![knowledge base](assets/images/openwebui_knowledge.png)
![chat with kb](assets/images/openwebui_chat_kb.png)

### 문서 거버넌스 팁

- KB는 **부서/등급별로 분리** → RBAC에서 read permission 세분화.
- 원본 문서는 **별도 DMS/Confluence**에 두고 KB는 링크/스냅샷 메타데이터만 보유.
- 임베딩 모델은 내부 표준 1개로 고정 (차원·거리 방식 통일, 인덱스 호환).

## 6. 감사 로그 & Pipelines 훅

### 내장 로그 위치 (컨테이너 내부)

| 로그 | 경로 |
| --- | --- |
| 애플리케이션 로그 | `/app/backend/data/logs/` |
| 채팅 기록 DB | `/app/backend/data/webui.db` (SQLite 기본) |
| Ollama 로그 | `docker logs airgap-ollama` |

호스트에서 접근:

```bash
docker exec -it airgap-openwebui ls /app/backend/data/logs
docker cp airgap-openwebui:/app/backend/data/webui.db ./backup_webui.db
```

> 운영에서는 SQLite → **PostgreSQL**로 교체하고 (`DATABASE_URL` env), DB 접속 감사도 활성화한다.

### Pipelines 훅으로 외부 감사 시스템 연동

OpenWebUI Pipelines는 OpenAI 호환 프록시 형태의 플러그인 프레임워크이다. `inlet`/`outlet` 훅으로 모든 메시지를 가로채 외부 SIEM(Splunk, Elastic)으로 전송 가능.

```python
# pipelines/audit_forwarder.py (개념 예시)
import json, httpx, os
from datetime import datetime

class Pipeline:
    class Valves:
        SIEM_URL: str = os.getenv("SIEM_URL", "http://siem.internal/ingest")
        API_KEY: str = os.getenv("SIEM_API_KEY", "")

    def __init__(self):
        self.name = "Audit Forwarder"
        self.valves = self.Valves()

    async def inlet(self, body: dict, user: dict | None = None) -> dict:
        await self._send({"phase": "inlet", "user": user, "body": body})
        return body

    async def outlet(self, body: dict, user: dict | None = None) -> dict:
        await self._send({"phase": "outlet", "user": user, "body": body})
        return body

    async def _send(self, payload: dict):
        payload["timestamp"] = datetime.utcnow().isoformat()
        async with httpx.AsyncClient(timeout=3.0) as client:
            try:
                await client.post(
                    self.valves.SIEM_URL,
                    headers={"Authorization": f"Bearer {self.valves.API_KEY}"},
                    json=payload,
                )
            except Exception:
                pass  # 감사 실패가 서비스 장애로 번지지 않도록 best-effort, 별도 DLQ 권장
```

Admin → **Settings → Pipelines** → 해당 파이프라인 URL 등록.

---

## 7. 폐쇄망 반입 절차 (모델·데이터·패키지)

### 7.1 외부망에서 모델 다운로드

외부 인터넷망 VM에서:

```bash
# Ollama 설치 (리눅스 예)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b-instruct
ollama pull bge-m3

# 모델 파일 위치
ls -lh ~/.ollama/models/blobs/
ls ~/.ollama/models/manifests/registry.ollama.ai/library/qwen2.5/
```

Ollama 모델은 `~/.ollama/models/` 하위에 **blobs/**(실제 가중치 레이어)와 **manifests/**(매니페스트)로 저장된다. 통째로 tar 묶음 권장:

```bash
tar -C ~/.ollama -czf qwen2.5-7b-instruct.tar.gz models/
```

### 7.2 sha256 해시 계산

```bash
sha256sum qwen2.5-7b-instruct.tar.gz > qwen2.5-7b-instruct.sha256
cat qwen2.5-7b-instruct.sha256
# 예: 9f3a...d21c  qwen2.5-7b-instruct.tar.gz
```

- 해시값은 **별도 채널**(내부 티켓, 서명된 문서)로 전달 → 파일 자체와 분리.
- 가능하면 `cosign` 등으로 서명 (`cosign sign-blob`).

### 7.3 DMZ 자료전송시스템 경유

1. 외부망 VM → **자료전송 포털**에 업로드 (결재/반입 사유 기재).
2. 시스템에서 **악성코드 스캔**(AV, YARA) + 파일 크기/유형 정책 검사.
3. 승인 → 내부망 수신 폴더로 일방향 전달.
4. 내부망에서 해시 재계산 → 원본 해시와 비교. 불일치 시 폐기.

```bash
# 내부망 수신 확인
sha256sum /mnt/inbox/qwen2.5-7b-instruct.tar.gz
diff <(cut -d' ' -f1 qwen2.5-7b-instruct.sha256) \
     <(sha256sum /mnt/inbox/qwen2.5-7b-instruct.tar.gz | cut -d' ' -f1)
```

### 7.4 내부 Ollama에 로드

방법 A: 통째로 덮어쓰기 (blob 동일 경로)

```bash
tar -C ~/.ollama -xzf /mnt/inbox/qwen2.5-7b-instruct.tar.gz
docker restart airgap-ollama
docker exec airgap-ollama ollama list
```

방법 B: GGUF 파일 + Modelfile (`ollama create`)

```Dockerfile
# Modelfile
FROM /models/qwen2.5-7b-instruct-q5_k_m.gguf
TEMPLATE """{{ .System }}

{{ .Prompt }}"""
PARAMETER temperature 0.2
```

```bash
docker cp qwen2.5-7b-instruct-q5_k_m.gguf airgap-ollama:/models/
docker exec -i airgap-ollama ollama create qwen2.5:7b-instruct -f - < Modelfile
```

방법 C: 이미 다른 내부 노드에 있다면 복제

```bash
docker exec airgap-ollama ollama cp qwen2.5:7b-instruct qwen2.5-backup
```

---

## 8. Python 의존성 오프라인 번들

### 외부망 (인터넷 가능)

```bash
# 1) requirements 고정
pip freeze > requirements.txt   # 또는 requirements-local.txt 재사용

# 2) wheel만 다운로드 (소스 빌드 회피)
python -m pip download \
    -r requirements.txt \
    -d ./offline_wheels \
    --platform manylinux2014_x86_64 \
    --python-version 311 \
    --only-binary=:all:

# 3) 아카이빙 + 해시
tar czf offline_wheels.tar.gz offline_wheels requirements.txt
sha256sum offline_wheels.tar.gz > offline_wheels.sha256
```

`--platform` / `--python-version` / `--implementation` / `--abi` 옵션으로 **내부망 OS/파이썬과 동일한 바이너리**를 확보. 일부 패키지(`torch`, `faiss-gpu`)는 --extra-index-url로 공식 인덱스 지정.

### 내부망 (오프라인)

```bash
# 반입 파일 검증
sha256sum -c offline_wheels.sha256
tar xzf offline_wheels.tar.gz

# 인덱스 없이 설치
pip install --no-index --find-links ./offline_wheels -r requirements.txt
```

### 운영 팁

- 사내 **PyPI 미러**(`devpi`, `Nexus`, `Artifactory`) 구축 시 `pip install --index-url https://pypi.internal/simple/`로 일반 설치.
- **SBOM**(CycloneDX, SPDX) 산출: `pip-audit`, `cyclonedx-py`로 의존성 + CVE 스캔.
- 주기적 재반입 SOP: 분기별 보안 패치 → 자료전송 → 회귀 테스트.

---

## 9. 체크리스트

- [ ] `docker compose up -d`로 두 서비스 기동 확인
- [ ] 첫 admin 계정 생성 → RBAC 설정 반영
- [ ] `qwen2.5:7b-instruct`, `bge-m3` 모델 pull 성공
- [ ] Knowledge Base 생성 + PDF 업로드 + 채팅에서 검색 동작 확인
- [ ] Pipelines 슬롯에 감사 포워더 등록 테스트
- [ ] 모델 tar.gz + sha256 파일 생성 및 검증 재현
- [ ] 오프라인 wheel 번들 설치 재현 (`--no-index`)

## 더 읽어보기

- OpenWebUI: https://docs.openwebui.com
- OpenWebUI Pipelines: https://docs.openwebui.com/pipelines/
- Ollama: https://github.com/ollama/ollama / https://ollama.com/library
- GGUF & llama.cpp quantization: https://github.com/ggerganov/llama.cpp/blob/master/examples/quantize/README.md
- pip download (오프라인 설치): https://pip.pypa.io/en/stable/cli/pip_download/
- CycloneDX SBOM: https://cyclonedx.org/
