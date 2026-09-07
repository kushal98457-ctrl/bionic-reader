"""Extractor for plain text / .txt input — the trivial case."""


def extract_text(raw: str) -> str:
    """Pass-through, kept as a function so the API layer treats every
    input source uniformly (text/pdf/docx all expose `extract(...)`)."""
    return raw


def extract_from_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()
