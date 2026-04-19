"""OpenAI(호환) 모델 팩토리.

OpenRouter 같은 OpenAI 호환 게이트웨이를 쓸 때는 `.env`에
`OPENAI_API_BASE=https://openrouter.ai/api/v1`, `OPENAI_MODEL=openai/gpt-4o-mini`
와 같은 식으로 지정한다. `ChatOpenAI`의 `base_url`/`model` 인자로 그대로 전달된다.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _clean_env(name: str, default: str = "") -> str:
    """환경변수에서 인라인 주석(#...) 과 주변 공백을 제거해 돌려준다.

    python-dotenv는 따옴표 없는 값의 인라인 주석을 떼지 않기 때문에,
    사용자가 `.env`에 `OPENAI_MODEL=gpt-4o-mini   # 모델 이름`처럼 써 두면
    `'gpt-4o-mini   # 모델 이름'` 전체가 값으로 잡힌다. 이를 방어한다.
    """
    raw = os.getenv(name, default)
    return raw.split("#", 1)[0].strip()


def get_chat_model(temperature: float = 0.0, streaming: bool = False, **kwargs: Any):
    """`ChatOpenAI` 인스턴스를 환경변수 기반으로 생성해 반환한다.

    읽는 env:
        OPENAI_API_KEY  — 인증 (필수)
        OPENAI_API_BASE — OpenRouter 등 호환 게이트웨이 URL (선택)
        OPENAI_MODEL    — 모델 이름 (기본 'gpt-4o-mini')
    """
    from langchain_openai import ChatOpenAI

    base_url = _clean_env("OPENAI_API_BASE") or None
    return ChatOpenAI(
        model=_clean_env("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=temperature,
        streaming=streaming,
        **({"base_url": base_url} if base_url else {}),
        **kwargs,
    )


@lru_cache(maxsize=2)
def get_embeddings():
    """OpenAI(또는 호환) Embeddings 인스턴스를 환경변수 기반으로 생성해 반환한다.

    읽는 env:
        OPENAI_API_KEY           — 인증 (필수)
        OPENAI_API_BASE          — OpenRouter 등 호환 게이트웨이 URL (선택)
        OPENAI_EMBEDDING_MODEL   — 임베딩 모델 이름 (기본 'text-embedding-3-small')
    """
    from langchain_openai import OpenAIEmbeddings

    base_url = _clean_env("OPENAI_API_BASE") or None
    return OpenAIEmbeddings(
        model=_clean_env("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        **({"openai_api_base": base_url} if base_url else {}),
    )


def provider_badge() -> str:
    """현재 설정된 모델을 한 줄로 표시."""
    return f"☁️ OpenAI | model={_clean_env('OPENAI_MODEL', 'gpt-4o-mini')}"
