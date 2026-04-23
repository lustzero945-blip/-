from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_course(topic):
    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":f"Explain {topic} simply"}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"
