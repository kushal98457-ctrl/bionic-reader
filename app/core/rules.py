"""
Rules

Pure functions that decide *how many* characters of a word should be
emphasized, given a BionicConfig. Kept separate from the engine so each
rule is independently testable and the engine stays a thin orchestrator.
"""

import math

from app.core.config import BionicConfig


def bold_length_for_word(word: str, config: BionicConfig, is_sentence_start: bool = False) -> int:
    """
    Return the number of leading characters of `word` to emphasize.

    - Short words (len < min_word_length): use `short_word_bold_chars`
      instead of the ratio formula, so "a", "an", "is", "of" don't get
      half of their 2 letters bolded. Sentence-starting short words get
      one extra character so they're not visually identical to a
      mid-sentence "a"/"is".
    - Normal words: ceil(length * ratio), capped by `max_bold_chars` so
      long words like "characterization" don't get an excessive chunk
      bolded. If `is_sentence_start` is True, `sentence_start_boost` is
      added to the ratio and the higher `sentence_start_max_bold_chars`
      cap is used instead — the first word after a full stop or a new
      paragraph gets a slightly stronger anchor, since that's where
      attention most often drifts.
    - Always at least 1 character bolded (if the word has any letters
      at all) and never more than len(word) - 1, so a word is never
      emphasized in its entirety (that reads as SHOUTING, not bionic
      emphasis) unless the word itself is a single character.
    """
    length = len(word)
    if length == 0:
        return 0

    if length < config.min_word_length:
        bold = config.short_word_bold_chars + (1 if is_sentence_start else 0)
        bold = min(bold, length)
        return bold

    ratio = config.ratio + (config.sentence_start_boost if is_sentence_start else 0.0)
    ratio = min(ratio, 1.0)
    cap = config.sentence_start_max_bold_chars if is_sentence_start else config.max_bold_chars

    bold = math.ceil(length * ratio)
    bold = min(bold, cap)
    bold = max(bold, 1)

    if bold >= length:
        bold = length - 1 if length > 1 else length

    return bold


def should_skip(token_type: str, config: BionicConfig) -> bool:
    """Whether a NUMBER/URL token should bypass bionic formatting entirely."""
    from app.core.tokenizer import TokenType

    if token_type == TokenType.NUMBER and config.skip_numbers:
        return True
    if token_type == TokenType.URL and config.skip_urls:
        return True
    return False