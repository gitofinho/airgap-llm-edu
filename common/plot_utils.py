"""Matplotlib 한글 폰트 유틸리티.

폐쇄망/WSL 등 한국어 폰트가 설치되지 않은 환경에서도 그래프가
□로 깨지지 않도록, 설치된 폰트를 감지해 적용하고, 없으면 안전한
대체 라벨을 돌려준다.
"""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.font_manager as fm

# 시도해볼 폰트 이름 (우선순위 순). 플랫폼별 기본 한글 폰트.
_CANDIDATES = [
    "Malgun Gothic",       # Windows
    "AppleGothic",         # macOS
    "NanumGothic",         # 리눅스 nanum 설치 시
    "Noto Sans CJK KR",    # fonts-noto-cjk
    "Noto Sans KR",
    "UnDotum",
    "Baekmuk Gulim",
]


def setup_korean_font() -> str | None:
    """설치된 한글 폰트를 찾아 matplotlib에 지정. 찾지 못하면 None."""
    installed = {f.name for f in fm.fontManager.ttflist}
    for name in _CANDIDATES:
        if name in installed:
            mpl.rcParams["font.family"] = name
            mpl.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지
            return name
    return None


def safe_labels(tokens: list[str]) -> tuple[list[str], str]:
    """한글 폰트가 있으면 원본 토큰, 없으면 인덱스 라벨을 돌려준다.

    Returns:
        labels: 그래프 틱 라벨
        legend_text: 인덱스→토큰 매핑 문자열 (한글 폰트가 있으면 빈 문자열)
    """
    if setup_korean_font() is not None:
        return list(tokens), ""
    idx_labels = [f"t{i}" for i in range(len(tokens))]
    legend = "\n".join(f"  t{i} = {t}" for i, t in enumerate(tokens))
    return idx_labels, legend


def report_korean_font_status() -> str:
    """현재 환경의 한글 폰트 상태를 한 줄 진단 문자열로 돌려준다."""
    picked = setup_korean_font()
    if picked:
        return f"✅ 한글 폰트 OK: '{picked}' 사용"
    return (
        "⚠️ 한글 폰트 없음 — 그래프 라벨이 깨질 수 있어 인덱스 라벨로 대체합니다.\n"
        "   해결: (Ubuntu/WSL) sudo apt install fonts-nanum fonts-noto-cjk-extra\n"
        "         (macOS) 시스템 기본 AppleGothic 사용 → matplotlib 캐시 삭제 후 재기동\n"
        "         (Windows) 시스템 기본 'Malgun Gothic' 사용 가능"
    )
