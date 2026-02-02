from dotenv import load_dotenv
from .openai_client import get_client


load_dotenv()


def simplify_text(input_text: str) -> str:
    client = get_client()
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": "You are an assistant that rewrites academic or technical text into simpler, plain English."},
                {"role": "user", "content": f"Simplify the following text for a 10-year-old reader in less than 500 words:\n\n{input_text}"}
            ],        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"
