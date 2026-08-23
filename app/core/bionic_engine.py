"""
Bionic Engine

The heart of the project. Converts text into a structured, renderer-agnostic
representation:

    BionicWord(original="Artificial", emphasized="Art", remaining="ificial")

The engine knows NOTHING about HTML, PDF, or terminal output — that's the
renderers' job (see app/renderers/). This separation is what lets us add
new output formats later without touching the algorithm.
"""

from dataclasses import dataclass
from typing import List, Union

from app.core.config import BionicConfig
from app.core.rules import bold_length_for_word, should_skip
from app.core.tokenizer import Token, TokenType, tokenize


@dataclass
class BionicWord:
    """A word that has been split into an emphasized head and a plain tail."""
    original: str
    emphasized: str
    remaining: str


@dataclass
class PlainText:
    """Anything that isn't emphasized: punctuation, whitespace, numbers, URLs."""
    text: str


# A processed document is just a flat sequence of these two node types,
# in original reading order.
BionicNode = Union[BionicWord, PlainText]


def process_word(word: str, config: BionicConfig, is_sentence_start: bool = False) -> BionicWord:
    """Split a single word into (emphasized, remaining) per the configured rules."""
    bold_len = bold_length_for_word(word, config, is_sentence_start=is_sentence_start)
    return BionicWord(
        original=word,
        emphasized=word[:bold_len],
        remaining=word[bold_len:],
    )


# Punctuation that ends a sentence — the word right after one of these
# (once whitespace is skipped) gets the sentence-start boost.
_SENTENCE_END_PUNCTUATION = {".", "!", "?"}


def process_text(text: str, config: BionicConfig = None) -> List[BionicNode]:
    """
    Tokenize `text` and convert every WORD token into a BionicWord,
    leaving punctuation/whitespace/numbers/URLs as PlainText.

    Tracks sentence/paragraph boundaries as it goes so the first word of
    each one can get the sentence-start emphasis boost (see
    BionicConfig.sentence_start_boost). The very first word of the whole
    text also counts as a sentence start.

    This is the main entry point renderers should call.
    """
    config = config or BionicConfig()
    tokens: List[Token] = tokenize(text)
    nodes: List[BionicNode] = []

    at_sentence_start = True  # the first word of the document is a "sentence start"

    for token in tokens:
        if token.type == TokenType.WORD and not should_skip(token.type, config):
            nodes.append(process_word(token.text, config, is_sentence_start=at_sentence_start))
            at_sentence_start = False
        else:
            nodes.append(PlainText(token.text))
            if token.type == TokenType.PUNCTUATION and token.text in _SENTENCE_END_PUNCTUATION:
                at_sentence_start = True
            elif token.type == TokenType.WHITESPACE and token.text.count("\n") >= 2:
                # A blank line (paragraph break) also resets sentence-start,
                # even mid-sentence extraction quirks from PDFs shouldn't
                # trigger on a single soft-wrap newline.
                at_sentence_start = True

    return nodes