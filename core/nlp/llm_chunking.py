import re
from typing import List, Tuple
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv
from core.nlp.simplify import simplify_text


MODEL = "gpt-3.5-turbo"
CHUNK_TOKENS = 3000       # per-chunk input budget (prompt+chunk should fit model context)
CHUNK_OVERLAP_SENTS = 2   # small sentence overlap to keep continuity
OUTPUT_TOKENS_PER_CHUNK = 400  # cap responses
FINAL_SUMMARY_TOKENS = 1500     # cap final summary length

load_dotenv()

client = OpenAI()


def enc(model: str):
    # Falls back to a generic encoding if model lookup fails
    try:
        return tiktoken.encoding_for_model(model)
    except Exception:
        return tiktoken.get_encoding("cl100k_base")

def token_count(text: str, model: str = MODEL) -> int:
    return len(enc(model).encode(text))


_SENT_REGEX = re.compile(
    r"""
    (?<!\b[A-Z])        # don't split after single capital initials
    (?<=[.!?])          # end punctuation
    [\"')\]]*           # optional closing quotes/brackets
    \s+                 # whitespace
    (?=[A-Z0-9(])       # next sentence starts with capital/number/(
    """,
    re.VERBOSE
)


def split_into_sentences(text: str) -> List[str]:
    text = text.strip()
    if not text:
        return []
    # Fast path: try regex split
    sents = re.split(_SENT_REGEX, text)
    # Merge very short “sentences” back to reduce fragments
    merged = []
    buf = []
    for s in sents:
        s = s.strip()
        if not s:
            continue
        buf.append(s)
        if len(" ".join(buf)) > 60:  # ~60 chars heuristic
            merged.append(" ".join(buf))
            buf = []
    if buf:
        merged.append(" ".join(buf))
    return merged 


def chunk_by_tokens_with_sentence_bounds(
    text: str,
    model: str = MODEL,
    chunk_tokens: int = CHUNK_TOKENS,
    overlap_sents: int = CHUNK_OVERLAP_SENTS
) -> List[str]:
    sentences = split_into_sentences(text)
    if not sentences:
        return []

    e = enc(model)
    chunks, cur_sents = [], []
    cur_tok_len = 0

    for i, s in enumerate(sentences):
        stoks = e.encode(s)
        stoks_len = len(stoks)

        if cur_tok_len + stoks_len <= chunk_tokens or not cur_sents:
            cur_sents.append(s)
            cur_tok_len += stoks_len
        else:
            chunks.append(" ".join(cur_sents))
            # start new chunk with overlap
            overlap = sentences[max(0, i - overlap_sents):i]
            cur_sents = overlap + [s]
            cur_tok_len = len(e.encode(" ".join(cur_sents)))

    if cur_sents:
        chunks.append(" ".join(cur_sents))
    return chunks


def simplify_chunk(chunk_text: str, audience: str = "10-year-old") -> str:
    """Simplify a single chunk."""
    sys = (
        "You simplify/rewrite academic or technical text into clear, simpler, plain English while keeping key facts. "
        "Write for a {aud} reader. Keep definitions for jargon, and use short paragraphs or bullet points when helpful."
    ).format(aud=audience)

    user = (
        "Simplify the following text for a {aud} reader. Keep key claims, definitions, and numbers. "
        "Avoid losing nuance. If there are sections, preserve their headings.\n\n"
        f"{chunk_text}"
    )

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": sys},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=OUTPUT_TOKENS_PER_CHUNK,
    )
    return resp.choices[0].message.content.strip()


def reduce_summary(simplified_chunks: List[str], target_words: int = 500) -> str:
    """Create a short overall summary from the simplified parts."""
    combined = "\n\n".join(simplified_chunks)
    # If this combined text is huge, you can re-chunk again here; for most cases it's fine.
    # sys = (
    #     "You are a precise summarizer. Produce a concise overview that captures the central question, "
    #     "methods (if present), key findings, and implications. Write for a 10-year-old reader."
    # )
    # user = (
    #     f"Create a short overall summary of {target_words} words (no less) of the following simplified notes:\n\n{combined}"
    # )
    # resp = client.chat.completions.create(
    #     model=MODEL,
    #     messages=[
    #         {"role": "system", "content": sys},
    #         {"role": "user", "content": user},
    #     ],
    #     temperature=0.3,
    #     max_tokens=FINAL_SUMMARY_TOKENS,
    # )
    # return resp.choices[0].message.content.strip()

    return simplify_text(combined)


def simplify_long_text_with_summary(
    text: str,
    audience: str = "10-year-old",
    model: str = MODEL,
    chunk_tokens: int = CHUNK_TOKENS
) -> Tuple[str, str, List[str]]:
    """
    Returns: (final_overall_summary, combined_simplified_text, per_chunk_simplified_list)
    """
    chunks = chunk_by_tokens_with_sentence_bounds(text, model=model, chunk_tokens=chunk_tokens)
    if not chunks:
        return ("", "", [])

    simplified_parts = []
    for i, ch in enumerate(chunks, 1):
        simplified = simplify_chunk(ch, audience=audience)
        simplified_parts.append(f"## Part {i}\n{simplified}")

    combined_simplified = "\n\n".join(simplified_parts)
    overall = reduce_summary(simplified_parts, target_words=500)
    return (overall, combined_simplified, simplified_parts)