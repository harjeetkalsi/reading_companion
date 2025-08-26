from dotenv import load_dotenv
from .openai_client import get_client

load_dotenv()


def explain_terms(input_text):
    client = get_client()
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": "You are an assistant that explains academic or technical vocab into simpler, plain English definitions."},
                {"role": "user", "content": f"Pick out all the scientific words and give a simple defintion for them for a 14-year-old reader, in your response just give the words and definitions in bullet points, no intro text or sentence saying what it is you have done:\n\n{input_text}"}
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"