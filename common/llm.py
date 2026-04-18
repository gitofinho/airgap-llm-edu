"""Provider-agnostic LLM / Embeddings 팩토리.

.env의 LLM_PROVIDER와 EMBEDDING_PROVIDER에 따라 OpenAI 또는 Ollama/로컬로 전환한다.
모든 노트북이 이 헬퍼를 사용하면, Day 2 S4-5에서 환경변수 한 줄만 바꿔
동일한 파이프라인을 로컬 모델로 재실행할 수 있다.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 0.0, streaming: bool = False, **kwargs: Any):
    """LLM_PROVIDER에 따라 ChatOpenAI 또는 ChatOllama를 반환한다."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        base_url = os.getenv("OPENAI_API_BASE")
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=temperature,
            streaming=streaming,
            **({"base_url": base_url} if base_url else {}),
            **kwargs,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=temperature,
            **kwargs,
        )

    raise ValueError(f"Unknown LLM_PROVIDER: {provider!r}")


@lru_cache(maxsize=4)
def get_embeddings():
    """EMBEDDING_PROVIDER에 따라 OpenAI 또는 HuggingFace 로컬 임베딩을 반환한다."""
    provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower()

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        base_url = os.getenv("OPENAI_API_BASE")
        return OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            **({"openai_api_base": base_url} if base_url else {}),
        )

    if provider == "local":
        from langchain_huggingface import HuggingFaceEmbeddings

        model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "BAAI/bge-m3")
        return HuggingFaceEmbeddings(
            model_name=model_name,
            encode_kwargs={"normalize_embeddings": True},
        )

    raise ValueError(f"Unknown EMBEDDING_PROVIDER: {provider!r}")


def provider_badge() -> str:
    """현재 설정된 provider 조합을 한 줄로 표시."""
    llm = os.getenv("LLM_PROVIDER", "openai")
    emb = os.getenv("EMBEDDING_PROVIDER", "openai")
    mode = "🔒 Airgap" if (llm == "ollama" and emb == "local") else "☁️ Cloud"
    return f"{mode} | LLM={llm} | EMBEDDING={emb}"
