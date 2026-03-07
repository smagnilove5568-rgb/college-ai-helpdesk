from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_history(history):

    text = ""

    for msg in history:
        text += f"{msg['role']}: {msg['content']}\n"

    prompt = f"""
Summarize the following conversation briefly but keep important context.

{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content