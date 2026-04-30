from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_course(topic):
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":f"Explique {topic} simplement avec exemple"}]
    )
    return res.choices[0].message.content

async def generate_quiz(topic):
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":f"Quiz sur {topic} avec réponse"}]
    )
    return res.choices[0].message.content

async def correct_code(code):
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":f"Corrige ce code:\n{code}"}]
    )
    return res.choices[0].message.content
