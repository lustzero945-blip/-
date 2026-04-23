from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_course(topic):
    prompt = f"""
Explique {topic} :
- simple
- exemple code
- exercice
- conseil pro
"""
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content[:4000]

async def generate_quiz(topic):
    prompt = f"""
Quiz sur {topic} :

Question: ...
A) ...
B) ...
C) ...
Réponse: A ou B ou C
"""
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content

async def correct_code(code):
    prompt = f"Corrige ce code et explique :\n{code}"
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content[:4000]