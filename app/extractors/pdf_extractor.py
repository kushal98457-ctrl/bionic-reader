"""
PDF extractor.

Uses PyMuPDF (imported as `fitz`) per the spec's recommendation — it's fast
and handles most real-world PDFs (including simple layouts) well without
extra dependencies.
"""

from typing import BinaryIO, Union


def extract_from_path(path: str) -> str:
    import fitz  # PyMuPDF

    text_parts = []
    with fitz.open(path) as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


def extract_from_bytes(data: bytes) -> str:
    import fitz  # PyMuPDF

    text_parts = []
    with fitz.open(stream=data, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


def extract(source: Union[str, bytes, BinaryIO]) -> str:
    """Convenience dispatcher: accepts a path, raw bytes, or a file-like object."""
    if isinstance(source, str):
        return extract_from_path(source)
    if isinstance(source, (bytes, bytearray)):
        return extract_from_bytes(bytes(source))
    # file-like object
    return extract_from_bytes(source.read())
