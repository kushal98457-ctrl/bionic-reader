from app.core.tokenizer import TokenType, reconstruct, tokenize


def test_reconstruct_preserves_original():
    text = "Hello, world! Don't stop. AI-powered tools cost $2026."
    tokens = tokenize(text)
    assert reconstruct(tokens) == text


def test_punctuation_split_from_word():
    tokens = tokenize("world!")
    kinds = [(t.text, t.type) for t in tokens]
    assert kinds == [("world", TokenType.WORD), ("!", TokenType.PUNCTUATION)]


def test_contraction_kept_as_single_word():
    tokens = tokenize("don't")
    words = [t for t in tokens if t.type == TokenType.WORD]
    assert len(words) == 1
    assert words[0].text == "don't"


def test_number_token():
    tokens = tokenize("2026")
    assert tokens[0].type == TokenType.NUMBER


def test_url_token_not_split():
    tokens = tokenize("visit https://example.com/page today")
    url_tokens = [t for t in tokens if t.type == TokenType.URL]
    assert len(url_tokens) == 1
    assert url_tokens[0].text == "https://example.com/page"


def test_hyphenated_word_split_into_two_words():
    tokens = tokenize("AI-powered")
    words = [t.text for t in tokens if t.type == TokenType.WORD]
    assert words == ["AI", "powered"]
