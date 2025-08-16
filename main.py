from text_from_url import extract_main_text
from llm_chunking import simplify_long_text_with_summary


if __name__ == "__main__":

    url = "https://link.springer.com/article/10.1186/s12978-024-01797-y"
    long_text = extract_main_text(url)

    overall, combined, parts = simplify_long_text_with_summary(
        text=long_text,
        audience="10-year-old",
        model="gpt-3.5-turbo",      # or "gpt-4o-mini" if you have it
        chunk_tokens=3000           # increase if you move to larger-context models
    )

    print("Overall")
    print(overall)

    print("Combined")
    print(combined)

    print("Parts")
    print(parts)
