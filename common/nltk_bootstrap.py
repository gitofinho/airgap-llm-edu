"""Unstructured/NLTK 런타임 데이터 부트스트랩.

`unstructured[pdf]`의 `mode='elements'` 파이프라인은 첫 실행 시 NLTK의
`punkt_tab`과 `averaged_perceptron_tagger_eng`를 내려받습니다. 폐쇄망에서는
이 다운로드가 실패하므로, 미리 확보 여부를 체크하고 가능한 경우에만 조용히
받아둡니다. 실패해도 교안 흐름은 계속 진행될 수 있도록 예외를 삼킵니다.
"""
from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

REQUIRED = ("tokenizers/punkt_tab", "taggers/averaged_perceptron_tagger_eng")


def ensure_nltk_data() -> None:
    try:
        import nltk  # type: ignore
    except ImportError:
        return

    data_dir = os.environ.get("NLTK_DATA") or str(Path.home() / ".cache" / "nltk_data")
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    if data_dir not in nltk.data.path:
        nltk.data.path.insert(0, data_dir)

    missing: list[str] = []
    for resource in REQUIRED:
        try:
            nltk.data.find(resource)
        except LookupError:
            missing.append(resource.split("/", 1)[-1])

    if not missing:
        return

    for pkg in missing:
        try:
            nltk.download(pkg, download_dir=data_dir, quiet=True, raise_on_error=True)
        except Exception as e:  # noqa: BLE001 — 폐쇄망/타임아웃 모두 포용
            warnings.warn(
                f"[nltk_bootstrap] '{pkg}' 다운로드 실패: {e}. "
                "폐쇄망이라면 SETUP.md §6 절차로 NLTK 데이터를 사전 반입하세요.",
                RuntimeWarning,
                stacklevel=2,
            )


if "pytest" not in sys.modules:
    ensure_nltk_data()
