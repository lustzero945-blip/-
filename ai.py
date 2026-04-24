from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("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"))

async def generate_course(topic):
    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":f"Explain {topic} simply"}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"
