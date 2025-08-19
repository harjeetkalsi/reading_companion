from openai import OpenAI
from dotenv import load_dotenv
from urllib.request import urlopen
from bs4 import BeautifulSoup

load_dotenv()

client = OpenAI()

def simplify_text(input_text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that rewrites academic or technical text into simpler, plain English."},
                {"role": "user", "content": f"Simplify the following text for a 10-year-old reader in less than 500 words:\n\n{input_text}"}
            ],
            temperature=0.7,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"
