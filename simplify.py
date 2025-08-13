from openai import OpenAI
from dotenv import load_dotenv
from urllib.request import urlopen
from bs4 import BeautifulSoup

load_dotenv()

client = OpenAI()

def validate_length(user_input, max_words):
    if len(user_input.split()) > max_words:
        return ' '.join(user_input.split()[:max_words])
    else: 
        return user_input

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
    
def simplify_from_urls(url):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are an assistant that rewrites academic or technical text into simpler, plain English."},
                {"role": "user", "content": f"Simplify the following article/text for a 10-year-old reader from this url, if there is more than one url go through each one systematically read and simplify:\n\n{url}"}
            ],
            temperature=0.7,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}" 

def extract_text_from_url(url): 
    url = "https://wellcomeopenresearch.org/articles/10-318"
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    print(text)
