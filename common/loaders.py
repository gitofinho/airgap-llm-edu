"""한국어 문서 로더 유틸.

PDF/DOCX/HWP(PDF 우회)/HWPX 공통 인터페이스.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from langchain_core.documents import Document


def load_pdf(path: str | Path) -> list[Document]:
    """PyMuPDF 기반 PDF 로더. 페이지 단위로 Document 반환."""
    from langchain_community.document_loaders import PyMuPDFLoader

    return PyMuPDFLoader(str(path)).load()


def load_docx(path: str | Path) -> list[Document]:
    from langchain_community.document_loaders import Docx2txtLoader

    return Docx2txtLoader(str(path)).load()


def load_hwpx(path: str | Path) -> list[Document]:
    """python-hwpx 기반. HWP(구버전)는 지원하지 않으니 PDF 변환 후 load_pdf 사용.

    python-hwpx 2.x API: ``HwpxDocument.open(path).export_text()``.
    """
    from hwpx.document import HwpxDocument

    text = HwpxDocument.open(str(path)).export_text()
    return [Document(page_content=text, metadata={"source": str(path)})]


def load_any(path: str | Path) -> list[Document]:
    """확장자로 자동 디스패치."""
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(p)
    if suffix == ".docx":
        return load_docx(p)
    if suffix == ".hwpx":
        return load_hwpx(p)
    if suffix == ".txt":
        return [Document(page_content=p.read_text(encoding="utf-8"), metadata={"source": str(p)})]
    raise ValueError(f"Unsupported file type: {suffix}")


def load_dir(dir_path: str | Path, pattern: str = "*.pdf") -> list[Document]:
    """디렉터리 내 모든 파일을 순회 로드."""
    docs: list[Document] = []
    for f in Path(dir_path).glob(pattern):
        docs.extend(load_any(f))
    return docs
