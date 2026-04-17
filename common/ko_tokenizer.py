"""한국어 형태소 기반 BM25 토크나이저.

rank_bm25는 공백 토크나이저가 기본이라 한국어에 매우 비효율적이다.
kiwipiepy로 명사·동사·어근 중심 토큰 시퀀스를 반환해 BM25·Ensemble retriever에 주입한다.
"""
from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=1)
def _kiwi():
    from kiwipiepy import Kiwi

    return Kiwi()


# BM25 품질에 도움되는 품사만 유지 (불용어 효과)
_KEEP_TAGS = {"NNG", "NNP", "VV", "VA", "XR", "SL", "SN"}


def tokenize_ko(text: str) -> list[str]:
    """한국어 문자열을 BM25용 토큰 리스트로 변환."""
    kiwi = _kiwi()
    tokens: list[str] = []
    for tok in kiwi.tokenize(text):
        if tok.tag in _KEEP_TAGS and len(tok.form) > 1:
            tokens.append(tok.form)
    return tokens


def tokenize_ko_simple(text: str) -> list[str]:
    """품사 필터 없이 모든 형태소 반환. 짧은 쿼리/실험용."""
    return [tok.form for tok in _kiwi().tokenize(text)]
