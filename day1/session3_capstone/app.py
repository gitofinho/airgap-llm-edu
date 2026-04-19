"""Day1 캡스톤: 금융 규정 Q&A 에이전트 (Streamlit + LangGraph ReAct + MemorySaver).

실행:
    cd day1/session3_capstone
    streamlit run app.py

사전 준비:
    day1/session2_rag_basics/04_rag_pipeline_lcel.ipynb 를 한 번은 실행해
    _store/efinance_rag (collection='efinance_regulation') 가 만들어져 있어야 합니다.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

import streamlit as st

# 프로젝트 루트를 import path에 추가 → `common` 모듈 로드
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common import get_chat_model, get_embeddings, provider_badge  # noqa: E402

from langchain_core.tools import tool  # noqa: E402
from langchain_community.vectorstores import Chroma  # noqa: E402
from langchain_community.tools import DuckDuckGoSearchRun  # noqa: E402
from langgraph.prebuilt import create_react_agent  # noqa: E402
from langgraph.checkpoint.memory import MemorySaver  # noqa: E402

CHROMA_DIR = ROOT / 'day1' / 'session2_rag_basics' / '_store' / 'efinance_rag'
COLLECTION = 'efinance_regulation'

SYSTEM_PROMPT = """당신은 금융회사의 내부 규정 Q&A를 돕는 AI 어시스턴트입니다.

도구 사용 규칙:
1. 전자금융감독규정 관련 질문은 반드시 `search_regulation` 도구를 **먼저** 호출해 근거를 확보하세요.
2. 이자·기간·금액 계산이 필요하면 반드시 `calculate_interest`를 사용하세요. 직접 계산하지 마세요.
3. 규정 밖의 최신 정보(예: 최근 공시, 뉴스)는 `web_search`로 찾되, 출처 URL을 같이 제시하세요.
4. 도구로도 확인할 수 없는 질문에는 \"확인할 수 없습니다\"라고 답하세요.

답변 형식:
- 한국어로 간결하게.
- 규정 근거는 `[근거: 제N조]`, 웹 출처는 `[출처: URL]` 형식으로 표기.
"""


# ──────────────── 리소스 로더 (프로세스 당 1회) ────────────────
@st.cache_resource(show_spinner='🔌 Chroma 인덱스 로드 중...')
def load_retriever():
    if not CHROMA_DIR.exists():
        st.error(
            f'Chroma 인덱스가 없습니다: {CHROMA_DIR}\n\n'
            '먼저 `day1/session2_rag_basics/04_rag_pipeline_lcel.ipynb` 를 실행해주세요.'
        )
        st.stop()
    vs = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=get_embeddings(),
        collection_name=COLLECTION,
    )
    return vs.as_retriever(
        search_type='mmr',
        search_kwargs={'k': 4, 'fetch_k': 12, 'lambda_mult': 0.5},
    )


@st.cache_resource(show_spinner='🛠 에이전트 구성 중...')
def build_agent():
    retriever = load_retriever()
    ddg = DuckDuckGoSearchRun()

    @tool
    def search_regulation(query: str) -> str:
        """전자금융감독규정을 벡터 검색해 관련 조항 본문을 반환한다.
        반환된 '[제N조(...)]' 태그는 최종 답변에서 '[근거: 제N조]' 형식으로 인용할 것.

        Args:
            query: 검색어 (자연어 질의 가능 — 예: '해킹 방지대책의 주요 통제항목')
        """
        docs = retriever.invoke(query)
        if not docs:
            return '관련 규정을 찾지 못했습니다.'
        return '\n\n'.join(
            f'[{d.metadata.get("article", "알 수 없음")}] {d.page_content}'
            for d in docs
        )

    @tool
    def calculate_interest(principal: float, annual_rate_pct: float, days: int) -> float:
        """원금, 연이자율(%), 기간(일)으로 단리 이자를 계산한다.

        Args:
            principal: 원금 (원)
            annual_rate_pct: 연 이자율 (%)
            days: 예치 기간 (일)
        """
        return round(principal * annual_rate_pct / 100 * days / 365, 2)

    @tool
    def web_search(query: str) -> str:
        """DuckDuckGo로 웹을 검색해 상위 결과의 요약을 반환한다.
        규정/도메인 지식으로 답할 수 없는 최신 정보(뉴스·공시 등)에만 사용.
        폐쇄망 배포 시 이 도구는 **제거하거나 사내 검색 API로 교체**해야 한다.

        Args:
            query: 검색어
        """
        try:
            return ddg.invoke(query)
        except Exception as e:
            return f'웹 검색 실패: {type(e).__name__}: {e}'

    tools = [search_regulation, calculate_interest, web_search]
    llm = get_chat_model(temperature=0)
    memory = MemorySaver()
    return create_react_agent(llm, tools, checkpointer=memory, prompt=SYSTEM_PROMPT)


# ──────────────── Streamlit UI ────────────────
st.set_page_config(page_title='금융 규정 Q&A 에이전트', page_icon='🏦', layout='wide')
st.title('🏦 금융 규정 Q&A 에이전트')
st.caption(f'{provider_badge()}  ·  ReAct + MemorySaver + Chroma RAG')

# 세션 상태 초기화
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []  # [{role, content, tool_events}]

# ── 사이드바 ──
with st.sidebar:
    st.subheader('🧵 대화 세션')
    st.caption('thread_id (MemorySaver 키)')
    st.code(st.session_state.thread_id, language=None)
    if st.button('🆕 새 대화', use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader('🛠 도구')
    st.markdown(
        '- `search_regulation` — 전자금융감독규정 Chroma RAG\n'
        '- `calculate_interest` — 단리 이자 계산\n'
        '- `web_search` — DuckDuckGo 웹 검색'
    )

    st.divider()
    st.subheader('💡 예시 질문')
    st.markdown(
        '- 해킹 등 방지대책의 주요 통제항목을 규정에서 찾아줘\n'
        '- 1000만원을 연 3.5%로 90일 예치하면 이자가 얼마?\n'
        '- 전자금융거래법 관련 최근 금감원 제재 뉴스 찾아줘'
    )


# ── 렌더 헬퍼 ──
def render_tool_events(events: list[dict]) -> None:
    for ev in events:
        if ev['kind'] == 'call':
            with st.expander(f"🔧 `{ev['name']}` 호출", expanded=False):
                st.json(ev['args'])
        elif ev['kind'] == 'result':
            with st.expander(f"👁 `{ev['name']}` 결과", expanded=False):
                st.code(ev['content'][:2000])


# ── 과거 메시지 렌더 ──
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        if msg['role'] == 'assistant':
            render_tool_events(msg.get('tool_events', []))
        st.markdown(msg['content'])


# ── 입력 처리 ──
if user_input := st.chat_input('규정·이자 계산·최근 뉴스 등을 물어보세요'):
    st.session_state.messages.append({
        'role': 'user',
        'content': user_input,
        'tool_events': [],
    })
    with st.chat_message('user'):
        st.markdown(user_input)

    agent = build_agent()
    config = {'configurable': {'thread_id': st.session_state.thread_id}}

    with st.chat_message('assistant'):
        tool_slot = st.container()
        answer_slot = st.empty()

        tool_events: list[dict] = []
        final_answer = ''

        try:
            for event in agent.stream(
                {'messages': [('user', user_input)]},
                config=config,
                stream_mode='updates',
            ):
                for _node, payload in event.items():
                    for m in payload.get('messages', []):
                        tool_calls = getattr(m, 'tool_calls', None)
                        if tool_calls:
                            for c in tool_calls:
                                ev = {'kind': 'call', 'name': c['name'], 'args': c['args']}
                                tool_events.append(ev)
                                with tool_slot.expander(f"🔧 `{c['name']}` 호출", expanded=False):
                                    st.json(c['args'])
                        elif m.__class__.__name__ == 'ToolMessage':
                            ev = {
                                'kind': 'result',
                                'name': getattr(m, 'name', '(tool)'),
                                'content': str(m.content),
                            }
                            tool_events.append(ev)
                            with tool_slot.expander(f"👁 `{ev['name']}` 결과", expanded=False):
                                st.code(ev['content'][:2000])
                        else:
                            if getattr(m, 'content', None):
                                final_answer = m.content
                                answer_slot.markdown(final_answer)
        except Exception as e:
            st.error(f'에이전트 실행 오류: {type(e).__name__}: {e}')
            st.stop()

        st.session_state.messages.append({
            'role': 'assistant',
            'content': final_answer or '(응답 없음)',
            'tool_events': tool_events,
        })
