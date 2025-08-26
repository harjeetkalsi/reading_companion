import core.scraping.text_from_url as tfu

## _clean_text

def test_clean_text_collapses_blanks():
    raw = "Line 1\n\n\n\nLine 2\n\nLine 3  "
    out = tfu._clean_text(raw)
    assert out == "Line 1\n\nLine 2\n\nLine 3"

## trafilatura fast-path 

def test_extract_main_text_trafilatura_success(monkeypatch):
    # Fake trafilatura responses
    monkeypatch.setattr(tfu.trafilatura, "fetch_url", lambda url: "<html>ok</html>")
    def fake_extract(downloaded, **kwargs):
        assert kwargs.get("favor_recall") is True
        return "Title\n\nBody text."
    monkeypatch.setattr(tfu.trafilatura, "extract", fake_extract)

    text = tfu.extract_main_text_trafilatura("http://example.com")
    assert text == "Title\n\nBody text."

def test_extract_main_text_trafilatura_none(monkeypatch):
    monkeypatch.setattr(tfu.trafilatura, "fetch_url", lambda url: None)
    assert tfu.extract_main_text_trafilatura("http://nope") is None

## selenium path 

class FakeElement:
    def click(self): pass

class FakeDriver:
    """Minimal Selenium-like driver for tests."""
    def __init__(self, html, cookie_will_match_index=None):
        self._html = html
        self._quit_called = False
        self._cookie_calls = 0
        self._cookie_will_match_index = cookie_will_match_index  # which XPATH index should "exist"

    def get(self, url): pass
    @property
    def page_source(self): return self._html
    def quit(self): self._quit_called = True

    # Simulate find_element trying several COOKIE_XPATHS until one matches
    def find_element(self, by, xp):
        assert by == tfu.By.XPATH
        idx = self._cookie_calls
        self._cookie_calls += 1
        if self._cookie_will_match_index is not None and idx == self._cookie_will_match_index:
            return FakeElement()
        raise Exception("not found")

def test_extract_main_text_selenium_happy_path(monkeypatch):
    # Prepare "page" html
    html = """
    <html><head><title>t</title></head>
    <body>
      <div id="banner">cookie banner</div>
      <article><h1>H1</h1><p>A</p><p>B</p><script>bad()</script></article>
    </body></html>
    """

    # Fake driver factory
    created = {}
    def fake_chrome(service=None, options=None):
        drv = FakeDriver(html, cookie_will_match_index=1)  # click matches on 2nd xpath
        created["driver"] = drv
        return drv

    # Patch Selenium bits used in your function
    monkeypatch.setattr(tfu.webdriver, "Chrome", fake_chrome)

    # Patch readability.Document to return just the article part
    class FakeDoc:
        def __init__(self, html): self.html = html
        def summary(self, html_partial=True):
            return "<article><h1>H1</h1><p>A</p><p>B</p><noscript>x</noscript></article>"
    monkeypatch.setattr(tfu, "Document", FakeDoc)

    out = tfu.extract_main_text_selenium("http://example.com", headless=True, wait=0.0)
    # Driver must be quit
    assert created["driver"]._quit_called is True
    # Text should be cleaned and contain article content, without script/noscript
    assert "H1" in out and "A" in out and "B" in out
    assert "noscript" not in out

def test_extract_main_text_selenium_no_cookie_button(monkeypatch):
    # No cookie xpath ever matches but content still extracts
    html = "<html><body><article><p>Body only.</p></article></body></html>"

    def fake_chrome(service=None, options=None):
        return FakeDriver(html, cookie_will_match_index=None)

    monkeypatch.setattr(tfu.webdriver, "Chrome", fake_chrome)

    class FakeDoc:
        def __init__(self, html): self.html = html
        def summary(self, html_partial=True):
            return "<article><p>Body only.</p></article>"
    monkeypatch.setattr(tfu, "Document", FakeDoc)

    out = tfu.extract_main_text_selenium("http://example.com", wait=0.0)
    assert out == "Body only."

def test_extract_main_text_selenium_returns_none_on_empty(monkeypatch):
    def fake_chrome(service=None, options=None):
        return FakeDriver("<html><body></body></html>")
    monkeypatch.setattr(tfu.webdriver, "Chrome", fake_chrome)

    class FakeDoc:
        def __init__(self, html): self.html = html
        def summary(self, html_partial=True):
            return "<div></div>"
    monkeypatch.setattr(tfu, "Document", FakeDoc)

    out = tfu.extract_main_text_selenium("http://example.com", wait=0.0)
    assert out is None

## top-level orchestrator

def test_extract_main_text_prefers_trafilatura(monkeypatch):
    # Fast path returns text => no selenium
    monkeypatch.setattr(tfu, "extract_main_text_trafilatura", lambda url: "FAST TEXT")
    called = {"selenium": False}
    def fake_sel(url): 
        called["selenium"] = True
        return "SEL TEXT"
    monkeypatch.setattr(tfu, "extract_main_text_selenium", fake_sel)

    out = tfu.extract_main_text("http://example.com")
    assert out == "FAST TEXT"
    assert called["selenium"] is False

def test_extract_main_text_falls_back_to_selenium(monkeypatch):
    monkeypatch.setattr(tfu, "extract_main_text_trafilatura", lambda url: None)
    monkeypatch.setattr(tfu, "extract_main_text_selenium", lambda url: "SEL TEXT")
    out = tfu.extract_main_text("http://example.com")
    assert out == "SEL TEXT"

def test_extract_main_text_both_fail_returns_message(monkeypatch):
    monkeypatch.setattr(tfu, "extract_main_text_trafilatura", lambda url: None)
    monkeypatch.setattr(tfu, "extract_main_text_selenium", lambda url: None)
    out = tfu.extract_main_text("http://example.com")
    assert "couldn't extract readable" in out.lower()      