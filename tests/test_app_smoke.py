# tests/test_app_smoke.py
import sys
from pathlib import Path
import pytest

# Ensure project root (that contains "app/" and "core/") is importable
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Guard for Streamlit testing API availability
try:
    from streamlit.testing.v1 import AppTest  # type: ignore
    _HAS_ST_TESTING = True
except Exception:
    _HAS_ST_TESTING = False

pytestmark = pytest.mark.skipif(
    not _HAS_ST_TESTING, reason="streamlit.testing.v1 not available"
)

APP_FILE = "app/app.py"

def test_app_renders_and_core_widgets_present():
    at = AppTest.from_file(APP_FILE).run()
    titles = [el for el in at.get("title")]
    assert any("Reading Companion" in t.value for t in titles)

def test_app_has_expected_expanders():
    at = AppTest.from_file(APP_FILE).run()
    expanders = [e for e in at.get("expander")]
    labels = [e.label for e in expanders]
    for expected in [
        "💡 See Example",
        "🛠️ Use Now",
        "🌟 See our Monthly Top Picks",
        "🔎 Where to search for Research?",
    ]:
        assert expected in labels