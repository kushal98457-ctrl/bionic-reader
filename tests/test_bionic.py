from app.core.bionic_engine import BionicWord, PlainText, process_text, process_word
from app.core.config import BionicConfig, StrengthPreset


def test_process_word_basic_ratio():
    config = BionicConfig.from_ratio(0.4)
    result = process_word("information", config)  # len 11 -> ceil(4.4) = 5
    assert result.emphasized == "infor"
    assert result.remaining == "mation"
    assert result.emphasized + result.remaining == "information"


def test_short_words_not_over_emphasized():
    config = BionicConfig(min_word_length=3, short_word_bold_chars=1)
    for word in ["a", "an", "is", "to", "of"]:
        result = process_word(word, config)
        assert len(result.emphasized) == 1


def test_long_word_capped():
    config = BionicConfig.from_ratio(0.4, max_bold_chars=6)
    result = process_word("characterization", config)  # len 16
    assert len(result.emphasized) == 6  # capped, not ceil(16*0.4)=7


def test_word_never_fully_bolded():
    config = BionicConfig.from_ratio(0.9)
    result = process_word("cat", config)
    assert len(result.emphasized) < len("cat")


def test_presets_map_to_expected_ratios():
    assert BionicConfig.from_preset(StrengthPreset.LOW).ratio == 0.30
    assert BionicConfig.from_preset(StrengthPreset.MEDIUM).ratio == 0.40
    assert BionicConfig.from_preset(StrengthPreset.HIGH).ratio == 0.50
    assert BionicConfig.from_preset(StrengthPreset.MAX).ratio == 0.60


def test_process_text_preserves_punctuation():
    nodes = process_text("Hello, world!", BionicConfig.from_ratio(0.4))
    rebuilt = "".join(
        (n.emphasized + n.remaining) if isinstance(n, BionicWord) else n.text
        for n in nodes
    )
    assert rebuilt == "Hello, world!"


def test_numbers_and_urls_untouched():
    nodes = process_text("Call me in 2026 or visit https://example.com now", BionicConfig())
    plain_texts = [n.text for n in nodes if isinstance(n, PlainText)]
    assert "2026" in plain_texts
    assert "https://example.com" in plain_texts
