import app.controllers as c

def test_decide_source_text_uses_uploaded():
    src, warn = c.decide_source_text(
        user_input="pdf text here",
        uploaded_file_used=True,
        url_extractor=lambda s: ["http://x"] if "http" in s else [],
        fetch_from_url=lambda u: "SHOULD_NOT_BE_CALLED",
    )
    assert src == "pdf text here"
    assert warn is None

def test_decide_source_text_fetches_when_urls():
    seen = []
    src, warn = c.decide_source_text(
        user_input="see http://a and http://b",
        uploaded_file_used=False,
        url_extractor=lambda s: ["http://a", "http://b"],
        fetch_from_url=lambda u: (seen.append(u) or f"TEXT({u})"),
    )
    assert "TEXT(http://a)" in src and "TEXT(http://b)" in src
    assert warn is None
    assert seen == ["http://a", "http://b"]

def test_decide_source_text_warns_when_empty():
    src, warn = c.decide_source_text(
        user_input="   ",
        uploaded_file_used=False,
        url_extractor=lambda s: [],
        fetch_from_url=lambda u: None,
    )
    assert src is None and "upload a PDF" in warn

def test_simplify_flow_direct_path():
    out = c.simplify_flow(
        source_text="short",
        token_count_fn=lambda s: 10,
        simplify_fn=lambda s: "SIMPLIFIED",
        chunked_pipeline_fn=lambda s: ("OVERALL", "COMBINED", []),
    )
    assert out["chunked"] is False
    assert out["processed"] == "SIMPLIFIED"
    assert out["overall"] is None

def test_simplify_flow_chunked_path():
    out = c.simplify_flow(
        source_text="long",
        token_count_fn=lambda s: 999999,
        simplify_fn=lambda s: "SHOULD_NOT_BE_CALLED",
        chunked_pipeline_fn=lambda s: ("OVERALL", "COMBINED", ["P1", "P2"]),
    )
    assert out["chunked"] is True
    assert out["processed"] == "COMBINED"
    assert out["overall"] == "OVERALL"
