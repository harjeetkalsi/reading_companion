import pytest 
import types
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

##simplify_chunk (mock OpenAI)

def test_simplify_chunk_calls_openai(monkeypatch):
    # Build a dummy response object like OpenAI returns
    class DummyChoice:
        def __init__(self, content):
            self.message = types.SimpleNamespace(content=content)

    class DummyResp:
        def __init__(self, content):
            self.choices = [DummyChoice(content)]

    def fake_create(*args, **kwargs):
        # Basic sanity checks on the prompt shape
        assert kwargs["model"] == lc.MODEL
        assert any(m["role"] == "system" for m in kwargs["messages"])
        assert any("Simplify the following text" in m["content"] for m in kwargs["messages"] if m["role"] == "user")
        return DummyResp("Simplified chunk output")

    # Patch the OpenAI client used in the module
    monkeypatch.setattr(lc.client.chat.completions, "create", fake_create)

    out = lc.simplify_chunk("Original text about vitamin D.", audience="10-year-old")
    assert "Simplified chunk output" in out


## reduce_summary (mock simplify_text it delegates to) ----------

def test_reduce_summary_uses_simplify_text(monkeypatch):
    called = {}

    def fake_simplify_text(text):
        # Make sure it receives the concatenated chunks
        assert "## Part 1" in text or "Part" in text or "Chunk" in text or "\n\n" in text
        called["ok"] = True
        return "Overall reduced summary (mocked)"

    monkeypatch.setattr(lc, "simplify_text", fake_simplify_text)

    summary = lc.reduce_summary(["## Part 1\nA", "## Part 2\nB"], target_words=500)
    assert called.get("ok") is True
    assert summary == "Overall reduced summary (mocked)"


##pipeline simplify_long_text_with_summary

def test_pipeline_map_reduce_flow(monkeypatch):
    # Force small chunks to ensure multiple parts
    # Mock simplify_chunk to produce deterministic output
    monkeypatch.setattr(lc, "simplify_chunk", lambda ch, audience="10-year-old": f"[SIMPLIFIED::{ch[:20]}...]")
    # Mock reduce_summary to return fixed overall
    monkeypatch.setattr(lc, "reduce_summary", lambda parts, target_words=500: "OVERALL SUMMARY")

    long_text = "S1. " * 50 + "S2. " * 50 + "S3. " * 50
    overall, combined, parts = lc.simplify_long_text_with_summary(
        long_text,
        audience="10-year-old",
        model=lc.MODEL,
        chunk_tokens=20  # tiny budget: with fake encoder this will produce multiple chunks
    )

    assert overall == "OVERALL SUMMARY"
    assert isinstance(combined, str) and combined
    assert isinstance(parts, list) and len(parts) > 1
    # Combined should contain headers "## Part i"
    assert "## Part 1" in combined
    assert any("## Part 2" in p or "## Part 3" in p for p in parts)

def test_reduce_summary_functional_no_api(monkeypatch):
    parts = [
        "## Part 1\n" + ("word " * 800),
        "## Part 2\n" + ("word " * 800),
    ]
    def fake_simplify_text(text):
        # pretend “summarisation”: return first 120 words
        words = text.split()
        return " ".join(words[:120])
    monkeypatch.setattr(lc, "simplify_text", fake_simplify_text)

    summary = lc.reduce_summary(parts, target_words=500)
    assert len(summary.split()) <= 130  # “shorter than input” contract

##edge cases

def test_pipeline_handles_all_empty():
    overall, combined, parts = lc.simplify_long_text_with_summary("", audience="10-year-old")
    assert overall == "" and combined == "" and parts == []