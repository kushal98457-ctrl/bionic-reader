"""
Tokenizer

Splits raw text into a sequence of Tokens without losing anything —
punctuation, whitespace, newlines, numbers, URLs and hyphenated words
all come back out untouched when re-joined.

We deliberately do NOT use `str.split(" ")` because that destroys
punctuation attachment ("world!" -> we need "world" + "!" separately
for bionic purposes, but must be able to re-glue them for rendering).
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List


class TokenType(str, Enum):
    WORD = "word"          # a real word, e.g. "Artificial"
    NUMBER = "number"      # a purely numeric token, e.g. "2026"
    URL = "url"            # a URL, left untouched
    PUNCTUATION = "punct"  # punctuation marks, e.g. "," "!" "."
    WHITESPACE = "space"   # spaces, tabs, newlines


@dataclass
class Token:
    text: str
    type: TokenType


_URL_RE = re.compile(
    r"(?:https?://|www\.)[^\s<>\"']+", re.IGNORECASE
)
_NUMBER_RE = re.compile(r"^\d+([.,]\d+)*$")
_WORD_RE = re.compile(r"[A-Za-z]+(?:['\u2019][A-Za-z]+)*")  # handles don't, I'm
_WHITESPACE_RE = re.compile(r"\s+")

# Master pattern tried in order: URL, word (with apostrophes), number, whitespace, single punctuation char
_MASTER_RE = re.compile(
    r"(?P<url>{url})"
    r"|(?P<word>{word})"
    r"|(?P<number>\d+(?:[.,]\d+)*)"
    r"|(?P<space>\s+)"
    r"|(?P<punct>.)".format(url=_URL_RE.pattern, word=_WORD_RE.pattern),
    re.IGNORECASE | re.UNICODE,
)


def tokenize(text: str) -> List[Token]:
    """
    Tokenize `text` into a flat list of Tokens, preserving every character.
    Joining `t.text for t in tokenize(text)` always reproduces `text` exactly.

    Hyphenated words (e.g. "AI-powered") are tokenized as two WORD tokens
    joined by a PUNCTUATION "-" token, so each half gets its own emphasis —
    this matches the spec's "handle hyphenated words as separate components".
    """
    tokens: List[Token] = []
    for match in _MASTER_RE.finditer(text):
        if match.group("url"):
            tokens.append(Token(match.group("url"), TokenType.URL))
        elif match.group("word"):
            tokens.append(Token(match.group("word"), TokenType.WORD))
        elif match.group("number"):
            tokens.append(Token(match.group("number"), TokenType.NUMBER))
        elif match.group("space"):
            tokens.append(Token(match.group("space"), TokenType.WHITESPACE))
        elif match.group("punct"):
            tokens.append(Token(match.group("punct"), TokenType.PUNCTUATION))
    return tokens


def reconstruct(tokens: List[Token]) -> str:
    """Sanity-check helper: rebuild the original string from tokens."""
    return "".join(t.text for t in tokens)
