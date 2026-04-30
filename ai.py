async def generate_quiz(topic):
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{
            "role": "user",
            "content": f"""
Quiz sur {topic} :

Question: ...
A) ...
B) ...
C) ...
Réponse: A
"""
        }]
    )
    return res.choices[0].message.content
