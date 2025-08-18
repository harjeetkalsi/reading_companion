import pytest 
import core.nlp.llm_chunking as lc


##helpers

class _FakeEncoder:
    """Very simple 'encoder': tokens = words split on whitespace."""
    def encode(self, text: str):
        return text.split()

@pytest.fixture(autouse=True)
def fake_encoder(monkeypatch):
    """
    Make token counting predictable across tests:
    tokens = number of whitespace-separated words.
    """
    monkeypatch.setattr(lc, "enc", lambda model=None: _FakeEncoder())

##Tokens
def test_token_count_basic():
    assert lc.token_count("Hello world") >= 2

def test_token_count_unicode():
    assert lc.token_count("Café — π≈3.14159") > 0


##Split into sentences
def test_split_into_sentences_merges_short_sentences():
    text = "One sentence. Another one! And a question?"
    out = lc.split_into_sentences(text)
    assert out == ["One sentence. Another one! And a question?"]    

def test_split_into_sentences_long_sentences_split_cleanly():
    text = (
        "This is a fairly long sentence that should exceed sixty characters easily for testing. "
        "Here is another lengthy sentence designed to cross that threshold as well, for clarity. "
        "Finally, a third long sentence to ensure multiple outputs occur as expected."
    )
    out = lc.split_into_sentences(text)
    assert len(out) == 3
    print(out)
    assert out == ["This is a fairly long sentence that should exceed sixty characters easily for testing.",
        "Here is another lengthy sentence designed to cross that threshold as well, for clarity.",
        "Finally, a third long sentence to ensure multiple outputs occur as expected."]
    assert all(s.strip().endswith(('.', '!', '?')) for s in out)


def test_split_into_sentences_handles_empty_and_whitespace():
    assert lc.split_into_sentences("") == []
    assert lc.split_into_sentences("   \n ") == []

##chunk_by_tokens_with_sentence_bounds

def test_chunking_empty_text_returns_empty():
    assert lc.chunk_by_tokens_with_sentence_bounds("") == []

def test_chunking_respects_budget_and_overlap():

    # Build ~12 short sentences so we force multiple chunks with a small budget
    sents = [f"Sentence {i} is here and sentence {i} is above sixty characters long with and without spaces." for i in range(12)]
    text = " ".join(sents)

    # With fake encoder: each sentence has ~3-4 tokens; set very small chunk_tokens
    chunks = lc.chunk_by_tokens_with_sentence_bounds(
        text,
        chunk_tokens=80,        # tiny budget to force multiple chunks
        overlap_sents=2
    )
    print(chunks)
    assert len(chunks) >= 2
    
    # Ensure chunks are non-empty and sentence boundaries preserved (ends with '.')
    assert all(c.strip() and c.strip()[-1] in ".!?" for c in chunks)

    # Check overlap: take the last 2 sentences of chunk 0, they should appear at start of chunk 1
    first_chunk_sents = lc.split_into_sentences(chunks[0])
    second_chunk_sents = lc.split_into_sentences(chunks[1])
    
    print(first_chunk_sents)
    print(second_chunk_sents)

    overlap_expected = first_chunk_sents[-2:]
    assert second_chunk_sents[:2] == overlap_expected
