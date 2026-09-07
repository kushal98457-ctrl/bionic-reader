"""
Configuration for the Bionic Reading engine.

Everything that controls *how strong* the emphasis is lives here, so the
algorithm itself never hard-codes a percentage.
"""

from dataclasses import dataclass
from enum import Enum


class StrengthPreset(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAX = "max"


PRESET_RATIOS = {
    StrengthPreset.LOW: 0.30,
    StrengthPreset.MEDIUM: 0.40,
    StrengthPreset.HIGH: 0.50,
    StrengthPreset.MAX: 0.60,
}


@dataclass
class BionicConfig:
    """
    ratio: fraction (0.0 - 1.0) of each word's letters to emphasize.
           Comes from a preset (see `from_preset`) or a raw float (custom slider).
    min_word_length: words shorter than this are treated as "short words"
                      and get special handling instead of the normal formula.
    short_word_bold_chars: how many characters to bold on a short word
                            (0 = leave short words alone entirely).
    max_bold_chars: hard ceiling on emphasized characters for very long words,
                    so e.g. "characterization" doesn't get half the word bolded.
    skip_numbers: if True, purely numeric tokens are left unformatted.
    skip_urls: if True, URLs are left unformatted.
    sentence_start_boost: extra ratio (added on top of `ratio`) applied to the
                          first word of a sentence or paragraph. Attention
                          naturally lapses right after a full stop or a new
                          paragraph, so that word gets a slightly stronger
                          anchor than the rest of the sentence.
    sentence_start_max_bold_chars: cap on emphasized characters for a
                                    sentence-starting word (separate from
                                    `max_bold_chars` since the boosted ratio
                                    would otherwise hit the normal cap too
                                    early on long words).
    """

    ratio: float = 0.40
    min_word_length: int = 3
    short_word_bold_chars: int = 1
    max_bold_chars: int = 6
    skip_numbers: bool = True
    skip_urls: bool = True
    sentence_start_boost: float = 0.15
    sentence_start_max_bold_chars: int = 8

    @classmethod
    def from_preset(cls, preset: StrengthPreset, **overrides) -> "BionicConfig":
        return cls(ratio=PRESET_RATIOS[preset], **overrides)

    @classmethod
    def from_ratio(cls, ratio: float, **overrides) -> "BionicConfig":
        if not 0.0 < ratio <= 1.0:
            raise ValueError("ratio must be between 0 and 1")
        return cls(ratio=ratio, **overrides)