# app/controllers.py
from typing import Callable, Optional, Tuple, Dict
from urlextract import URLExtract

def decide_source_text(
    user_input: str,
    uploaded_file_used: bool,
    url_extractor: Callable[[str], list] = None,
    fetch_from_url: Callable[[str], Optional[str]] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Return (source_text, warning_msg). If no usable text, source_text=None and a warning string.
    """
    url_extractor = url_extractor or (lambda s: URLExtract().find_urls(s))
    fetch_from_url = fetch_from_url or (lambda u: None)

    user_input = (user_input or "").strip()
    if uploaded_file_used and user_input:
        return user_input, None

    if user_input:
        urls = url_extractor(user_input)
        if urls:
            fetched = []
            for url in urls:
                try:
                    txt = fetch_from_url(url)
                    if txt:
                        fetched.append(txt)
                except Exception:
                    continue
            if fetched:
                return "\n\n".join(fetched), None
        # fall back to typed text
        return user_input, None

    return None, "Please upload a PDF, paste text, or provide a valid link first."


def simplify_flow(
    source_text: str,
    token_count_fn: Callable[[str], int],
    simplify_fn: Callable[[str], str],
    chunked_pipeline_fn: Callable[[str], Tuple[str, str, list]],
    token_budget: int = 3000,
) -> Dict[str, Optional[str]]:
    """
    Returns: dict(processed, simplified, overall, chunked: bool)
    """
    if token_count_fn(source_text) <= token_budget:
        simplified = simplify_fn(source_text)
        return {
            "processed": simplified,
            "simplified": simplified,
            "overall": None,
            "chunked": False,
        }
    overall, combined, _parts = chunked_pipeline_fn(source_text)
    return {
        "processed": combined,
        "simplified": combined,
        "overall": overall,
        "chunked": True,
    }
