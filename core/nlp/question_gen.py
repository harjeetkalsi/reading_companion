from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def question_gen(input_text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a teacher that checks a student's understanding of academic text."},
                {"role": "user", "content": f"Generate 3 comprehension questions based on the text for a 14 year old learner:\n\n{input_text}"}
            ],
            temperature=0.7,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"
    
def question_answers(input_text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a teacher that checks a student's understanding of academic text."},
                {"role": "user", "content": f"You gave the students the 3 questions provided, now give them the answers in language that a 10 year old would understand :\n\n{input_text}"}
            ],
            temperature=0.7,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"   