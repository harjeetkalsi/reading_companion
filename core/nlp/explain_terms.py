from dotenv import load_dotenv
from .openai_client import get_client

load_dotenv()


def explain_terms(input_text):
    client = get_client()
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that explains academic or technical vocab into simpler, plain English definitions."},
                {"role": "user", "content": f"Pick out the techincal words and give a simple defintion for them for a 14-year-old reader:\n\n{input_text}"}
            ],
            temperature=0.7,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"